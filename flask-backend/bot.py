from .logger_setup import setup_logger
import yaml
from langchain.schema import HumanMessage, AIMessage
from typing import Literal, Dict, Any, List
from langchain_core.runnables import chain
import json
import random
from datetime import datetime
from .db import db_get_entry, db_update_entry, db_update_nested_field, db_append_list, db_add_message
from .runnables import explain_emotions, generate_value_reap, test_convo



logger = setup_logger()


with open("bot.yml", "r") as ymlfile:
    bot_data = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
with open("messages.yml", "r") as ymlfile:
    msgs = yaml.load(ymlfile, Loader=yaml.FullLoader)
    

# The "bot_" functions construct messages for the bot to send to the user
def bot_solicit_issue(data):
    resp = {
        "sender": "bot",
        "response": msgs["solicit_issue"],
        "widget_type": "text",
        "widget_config": {}
    }
    return resp

def bot_solicit_emotions(data):
    resp = {
        "sender": "bot",
        "response": msgs["solicit_emotions"],
        "widget_type": "multiselect",
        "widget_config": {
            "options": bot_data["emotions"]
        }
    }
    return resp

def bot_explain_emotions(data):
    lc_history = get_lc_history(data["messages"])
    logger.debug(json.dumps(data["messages"], indent=2))
    selected_emotions = [emo.get("emotion") for emo in data.get("emotions", []) if emo.get("emotion")]
    msg = explain_emotions.invoke({"messages": lc_history, "emotions": selected_emotions})
    resp = {
        "sender": "bot",
        "response": msg,
        "widget_type": "text",
        "widget_config": {}
    }
    return resp

def bot_solicit_values(data):
    vals = data.get("vals", [])
    done_val_nums = [val.get("value_num") for val in vals if val.get("value_num")]
    remaining = [i for i in range(bot_data['num_values']) if i not in done_val_nums]
    if remaining:
        val_num = random.choice(remaining)
        resp = {
            "sender": "bot",
            "response": msgs["solicit_values"].format(value=bot_data["vals"][val_num]),
            "widget_type": "slider",
            "widget_config": {
                "min": 0,
                "max": 100,
                "start": 50,
                "step": 1,
                "metadata": {
                    "val_num": val_num
                }
            }
        }
        return resp
    else:
        return {"error": "All values have been collected"}

def get_lc_history(chat_history):
    '''
    Convert chat history to langchain format
    '''
    lc_history = []
    for msg in chat_history:
        if msg["sender"] == "bot":
            lc_history.append(AIMessage(str(msg["response"])))
        else:
            lc_history.append(HumanMessage(str(msg["response"])))
    return lc_history

def get_max_min_person_value(user_data):
    vals = user_data.get("vals", [])
    assert len(vals) == bot_data["num_values"], "Not all values have been collected"
    val_ratings = [val.get("value_rating") for val in vals if val.get("value_rating")]
    max_val = max(val_ratings)
    min_val = min(val_ratings)
    val_rating_max_indices = [i for i, rating in enumerate(val_ratings) if rating == max_val]
    val_rating_min_indices = [i for i, rating in enumerate(val_ratings) if rating == min_val]
    val_rating_max_idx = random.choice(val_rating_max_indices)
    val_rating_min_idx = random.choice(val_rating_min_indices)
    max_val_dict = vals[val_rating_max_idx]
    min_val_dict = vals[val_rating_min_idx]
    return max_val_dict, min_val_dict


def parse_user_message(chat_id, request_data):
    '''
    Parse request data sent from user, 
    save data to database accordingly, 
    and determine next state.
    '''
    
    user_data = db_get_entry(chat_id)
    prev_state = user_data["state"]
    logger.debug(f'chat_id: {chat_id}')
    logger.debug(f'prev_state: {prev_state}')
    logger.debug(f'message: {request_data["response"]}')
    if prev_state == "begin":
        
        # Update state
        next_state = "solicit_issue"
        db_update_entry(chat_id, "state", next_state)
        user_data['state'] = next_state
        
        bot_msg = bot_solicit_issue(user_data)
    
    elif prev_state == "solicit_issue":
        
        # Update state
        next_state = "solicit_emotions"
        db_update_entry(chat_id, "state", next_state)
        user_data['state'] = next_state
        
        bot_msg = bot_solicit_emotions(user_data)
    
    elif prev_state == "solicit_emotions":
        
        # Parse and store selected emotions
        emotions = request_data.get("response", [])
        emotions = [{"emotion": emo} for emo in emotions]
        db_update_entry(chat_id, "emotions", emotions)
        user_data['emotions'] = emotions
        
        # Update state
        next_state = "explain_emotions"
        db_update_entry(chat_id, "state", next_state)
        user_data['state'] = next_state
        
        bot_msg = bot_explain_emotions(user_data)
    
    elif prev_state == "explain_emotions":
        
        # Get next bot message or detect stage completion
        bot_msg_explain_emos = bot_explain_emotions(user_data)
        if "::finished::" in bot_msg_explain_emos['response'].lower():
            # TODO: bot also says some final stuff when it's finished. would be good to allow sending multiple messages in a single response.
            next_state = "solicit_values"
            db_update_entry(chat_id, "state", next_state)
            user_data['state'] = next_state
            bot_msg = bot_solicit_values(user_data)
        else:
            next_state = "explain_emotions"
            bot_msg = bot_msg_explain_emos
    
    elif prev_state == "solicit_values":
        
        # Save values to database
        value_num = request_data['metadata'].get("val_num")
        value_rating = request_data.get("response")
        value_text = bot_data["vals"][value_num]
        db_append_list(chat_id, "vals", {"value_text": value_text, "value_num": value_num, "value_rating": value_rating})
        
        # Check which values have not been collected
        vals = user_data.get("vals", [])
        logger.debug(f'vals: {vals}')
        done_val_nums = [val.get("value_num") for val in vals if val.get("value_num")]
        remaining = [i for i in range(bot_data['num_values']) if i not in done_val_nums]

        # Generate next message
        if len(remaining) > 0:
            bot_msg = bot_solicit_values(user_data)
        else:
            next_state = "reappraisal"
            db_update_entry(chat_id, "state", next_state)
            user_data['state'] = next_state
            bot_msg 
            # bot_msg = {"response": "All values have been collected. Now we will reappraise your values."}

        
    elif prev_state == "reappraisal":
        
        # Get the max and min values
        # If there are ties, randomly sample one of the tied values
        max_val_dict, min_val_dict = get_max_min_person_value(user_data)
        
        
        
        return 
    else:
        return {"error": "Invalid state"}
    
    return bot_msg
    
        
    