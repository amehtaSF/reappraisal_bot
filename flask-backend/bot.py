from .logger_setup import setup_logger
import yaml
from langchain.schema import HumanMessage, AIMessage
from typing import Literal, Dict, Any, List
from langchain_core.runnables import chain
import json
import random
from decimal import Decimal
from datetime import datetime
from .db import db_get_entry, db_update_entry, db_update_nested_field, db_append_list, db_add_message
from .runnables import explain_emotions, generate_value_reap, generate_general_reap



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
    return [resp]

def bot_solicit_emotions(data):
    resp = {
        "sender": "bot",
        "response": msgs["solicit_emotions"],
        "widget_type": "multiselect",
        "widget_config": {
            "options": bot_data["emotions"]
        }
    }
    return [resp]

def bot_explain_emotions(data):
    lc_history = get_lc_history(data["messages"])
    # logger.debug(json.dumps(data["messages"], indent=2))
    selected_emotions = [emo.get("emotion") for emo in data.get("emotions", []) if emo.get("emotion")]
    msg = explain_emotions.invoke({"messages": lc_history, "emotions": selected_emotions})
    resp = {
        "sender": "bot",
        "response": msg,
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]

def bot_solicit_values(data):
    vals = data.get("vals", [])
    # logger.debug(f'vals: {vals}')
    done_val_nums = [int(val.get("value_num")) for val in vals if val.get("value_num") is not None]
    # logger.debug(f'done_val_nums: {done_val_nums}')
    remaining = [int(i) for i in range(bot_data['num_values']) if int(i) not in done_val_nums]
    # logger.debug(f'remaining: {remaining}')
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
        return [resp]
    else:
        return {"error": "All values have been collected"}
    
def bot_reappraise(data):
    
    max_val_dict, min_val_dict = get_max_min_person_value(data)
    
    # Identify the next reappraisal condition
    finished_reaps = data.get("reappraisals", [])
    finished_conditions = [reap.get("value_rank") for reap in finished_reaps]  # max, min, general
    unfinished_conditions = [cond for cond in ["max", "min", "general"] if cond not in finished_conditions]
    assert len(unfinished_conditions) > 0, "All reappraisals have been completed"
    next_condition = random.choice(unfinished_conditions)
    next_reap_num = len(finished_reaps) + 1
    
    # Generate a reappraisal message
    if next_condition == "max":
        reap = generate_value_reap.invoke({"messages": get_lc_history(data["issue_messages"]), "value": max_val_dict})
    elif next_condition == "min":
        reap = generate_value_reap.invoke({"messages": get_lc_history(data["issue_messages"]), "value": min_val_dict})
    elif next_condition == "general":
        reap = generate_general_reap.invoke({"messages": get_lc_history(data["issue_messages"])})
    reap = reap.replace("\n", "<br>")
    
    # Add the reappraisal to the database
    if next_condition == "max":
        value_dict = max_val_dict
    elif next_condition == "min":
        value_dict = min_val_dict
    else:
        value_dict = None
    reap_dict = {
        "reap_text": reap,
        "value_text": value_dict.get("value_text") if value_dict else "",
        "value_rank": next_condition,
        "value_rating": value_dict.get("value_rating") if value_dict else "",
        "reap_efficacy": ""
    }
    db_append_list(data["chat_id"], "reappraisals", reap_dict)
    
    # Compose the bot response
    resp = [{
        "sender": "bot",
        "response": f"Perspective {next_reap_num} of 3:",
        "widget_type": "text",
        "widget_config": {}
    }, {
        "sender": "bot",
        "response": reap,
        "widget_type": "text",
        "widget_config": {
            "metadata": {
                "msg_type": "reappraisal",
                "condition": next_condition}
        }
    }, {
        "sender": "bot",
        "response": msgs["reappraisal_success"],
        "widget_type": "slider",
        "widget_config": {
            "metadata": {
                "msg_type": "reappraisal_success",
                "condition": next_condition,
                "reap_num": next_reap_num},
            "min": 0,
            "max": 100,
            "start": 50,
            "step": 1
        }
    }]
    return resp

def bot_finished(data):
    resp = {
        "sender": "bot",
        "response": msgs["finished"],
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]

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
    val_ratings = [val.get("value_rating") for val in vals if val.get("value_rating") is not None]
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
    This is the central logic of the bot.
    Parses the user message and calls function to return the appropriate bot response.
    '''
    
    user_data = db_get_entry(chat_id)
    prev_state = user_data["state"]
    logger.debug(f'chat_id: {chat_id}')
    logger.debug(f'prev_state: {prev_state}')
    logger.debug(f'message: {request_data["response"]}')
    bot_msg = {"messages": []}
    if prev_state == "begin":
        
        # Update state
        next_state = "solicit_issue"
        db_update_entry(chat_id, "state", next_state)
        user_data['state'] = next_state
        
        bot_msg["messages"] += bot_solicit_issue(user_data)
    
    elif prev_state == "solicit_issue":
        
        # Update state
        next_state = "solicit_emotions"
        db_update_entry(chat_id, "state", next_state)
        user_data['state'] = next_state
        
        bot_msg["messages"] += bot_solicit_emotions(user_data)
    
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
        
        bot_msg["messages"] += bot_explain_emotions(user_data)
    
    elif prev_state == "explain_emotions":
        
        # Get next bot message or detect stage completion
        bot_msg_explain_emos = bot_explain_emotions(user_data)
        bot_msg_text = bot_msg_explain_emos[0]['response']
        if "::finished::" in bot_msg_text.lower():
            # Update state
            next_state = "solicit_values"
            db_update_entry(chat_id, "state", next_state)
            user_data['state'] = next_state
            
            # Save subset of conversation related to issue and emotions
            db_update_entry(chat_id, "issue_messages", user_data["messages"])
            
            # Add end of explain emotions message
            bot_msg["messages"] += [{
                "sender": "bot",
                "response": msgs["explain_emotions_end"],
                "widget_type": "text",
                "widget_config": {}
            }]
            
            # Add solicit_values message
            bot_msg["messages"] += bot_solicit_values(user_data)
        else:
            next_state = "explain_emotions"
            bot_msg["messages"] += bot_msg_explain_emos
    
    elif prev_state == "solicit_values":
        
        # Save values to database
        # logger.debug(f'request_data: {json.dumps(request_data, indent=2)}')
        value_num = int(request_data['widget_config']['metadata'].get("val_num"))
        value_rating = int(request_data.get("response"))
        value_text = bot_data["vals"][value_num]
        val_db_entry = {"value_text": value_text, "value_num": value_num, "value_rating": value_rating}
        db_append_list(chat_id, "vals", val_db_entry)
        user_data['vals'].append(val_db_entry)
        
        # Generate next message
        if len(user_data['vals']) < len(bot_data["vals"]):
            bot_msg["messages"] += bot_solicit_values(user_data)
        else:
            # Introduce reappraisal
            # next_state = "reap_intro"
            # db_update_entry(chat_id, "state", next_state)
            # user_data['state'] = next_state
            bot_msg["messages"].append({
                "sender": "bot",
                "response": msgs['intro_reappraisal'],
                "widget_type": "text",
                "widget_config": {}
            })
            next_state = "reappraisal"
            db_update_entry(chat_id, "state", next_state)
            user_data['state'] = next_state

        
    elif prev_state == "reappraisal":
        finished_reaps = user_data.get("reappraisals", [])
        if len(finished_reaps) < 3:
            bot_msg["messages"] += bot_reappraise(user_data)
        else:
            next_state = "finished"
            db_update_entry(chat_id, "state", next_state)
            user_data['state'] = next_state
            bot_msg["messages"] += bot_finished(user_data)
    
    else:
        return {"error": "Invalid state"}
    
    return bot_msg
    
        
    
    
    # i'm getting repeat values