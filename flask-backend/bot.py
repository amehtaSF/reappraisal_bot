from logger_setup import setup_logger
import yaml
from langchain.schema import HumanMessage, AIMessage
from typing import Literal, Dict, Any, List
from langchain_core.runnables import chain
import json
import random
from decimal import Decimal
from datetime import datetime
from db import (
    db_add_message, 
    db_add_value, 
    db_add_reappraisal,
    db_set_state, 
    db_set_emotions, 
    db_get_state, 
    db_get_vals, 
    db_get_messages, 
    db_get_issue_messages, 
    db_get_reappraisals, 
    db_get_emotions
)
from runnables import explain_emotions, generate_value_reap, generate_general_reap



logger = setup_logger()


with open("bot.yml", "r") as ymlfile:
    bot_data = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
with open("messages.yml", "r") as ymlfile:
    msgs = yaml.load(ymlfile, Loader=yaml.FullLoader)
    

# The "bot_" functions construct messages for the bot to send to the user

def bot_hello() -> List[Dict[str, Any]]:
    resp = {
        "sender": "bot",
        "response": msgs["introduction"],
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]

def bot_solicit_issue() -> List[Dict[str, Any]]:
    resp = {
        "sender": "bot",
        "response": msgs["solicit_issue"],
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]

def bot_solicit_emotions() -> List[Dict[str, Any]]:
    resp = {
        "sender": "bot",
        "response": msgs["solicit_emotions"],
        "widget_type": "multiselecttext",
        "widget_config": {
            "options": bot_data["emotions"]
        }
    }
    return [resp]

def bot_explain_emotions(chat_id, emotions) -> List[Dict[str, Any]]:
    messages = db_get_messages(chat_id)
    lc_history = convert_to_lc_history(messages)
    selected_emotions = [emo.get("emotion") for emo in emotions if emo.get("emotion")]
    msg = explain_emotions.invoke({"messages": lc_history, "emotions": selected_emotions})
    resp = {
        "sender": "bot",
        "response": msg,
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]

def bot_solicit_values(chat_id) -> List[Dict[str, Any]]:
    vals = db_get_vals(chat_id)  # Get values that have already been collected
    done_val_nums = [int(val.get("value_num")) for val in vals if val.get("value_num") is not None]  # Get value numbers already collected
    remaining = [int(i) for i in range(len(bot_data['vals'])) if int(i) not in done_val_nums]  # Get value numbers not collected
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
    
def bot_reappraise(chat_id) -> List[Dict[str, Any]]:
    
    max_val_dict, min_val_dict = get_max_min_person_value(chat_id)
    
    # Identify the next reappraisal condition
    finished_reaps = db_get_reappraisals(chat_id)
    finished_conditions = [reap.get("value_rank") for reap in finished_reaps]  # max, min, general
    unfinished_conditions = [cond for cond in ["max", "min", "general"] if cond not in finished_conditions]
    assert len(unfinished_conditions) > 0, "All reappraisals have been completed"
    next_condition = random.choice(unfinished_conditions)
    next_reap_num = len(finished_reaps) + 1
    
    # Get issue messages
    issue_messages = db_get_issue_messages(chat_id)
    lc_history = convert_to_lc_history(issue_messages)
    
    # Generate a reappraisal message
    if next_condition == "max":
        reap = generate_value_reap.invoke({"messages": lc_history, "value": max_val_dict})
    elif next_condition == "min":
        reap = generate_value_reap.invoke({"messages": lc_history, "value": min_val_dict})
    elif next_condition == "general":
        reap = generate_general_reap.invoke({"messages": lc_history})
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
        "reap_num": next_reap_num,
        "value_text": value_dict.get("value_text") if value_dict else "",
        "value_rank": next_condition,
        "value_rating": value_dict.get("value_rating") if value_dict else ""
    }
    db_add_reappraisal(chat_id, **reap_dict)
    
    # Compose the bot response
    resp = [{
        "sender": "bot",
        "response": f"Perspective {next_reap_num} of 3:",
        "widget_type": "text",
        "widget_config": {}
    }, 
    {
        "sender": "bot",
        "response": reap,
        "widget_type": "text",
        "widget_config": {
            "metadata": {
                "msg_type": "reappraisal",
                "condition": next_condition}
        }
    }, 
    {
        "sender": "bot",
        "response": f"Send any message to continue.",
        "widget_type": "text",
        "widget_config": {}
    }, 
    ]
    return resp


def bot_judge_reappraisals(chat_id) -> List[Dict[str, Any]]:
    
    reaps = db_get_reappraisals(chat_id)
    unjudged_reaps = [reap for reap in reaps if reap.get("reap_efficacy") is None]
    assert len(unjudged_reaps) > 0, "All reappraisals have been judged"
    cur_reap = unjudged_reaps[0]
    reap_text = cur_reap.get("reap_text")
    reap_num = cur_reap.get("reap_num")
    condition = cur_reap.get("value_rank")
    resp = [
        {
            "sender": "bot",
            "response": f"Perspective {reap_num} of 3:",
            "widget_type": "text",
            "widget_config": {}
        },
        {
            "sender": "bot",
            "response": reap_text,
            "widget_type": "text",
            "widget_config": {}
        },
        {
            "sender": "bot",
            "response": msgs["reappraisal_success"],
            "widget_type": "slider",
            "widget_config": {
                "metadata": {
                    "msg_type": "reappraisal_success",
                    "condition": condition,
                    "reap_num": reap_num},
                "min": 0,
                "max": 100,
                "start": 50,
                "step": 1
            }
    }]
    return resp


def bot_finished() -> List[Dict[str, Any]]:
    resp = {
        "sender": "bot",
        "response": msgs["finished"],
        "widget_type": "text",
        "widget_config": {}
    }
    return [resp]


def convert_to_lc_history(chat_history):
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

def get_max_min_person_value(chat_id):
    vals = db_get_vals(chat_id)
    assert len(vals) == len(bot_data['vals']), "Not all values have been collected"
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
    
    prev_state = db_get_state(chat_id)
    logger.debug(f'chat_id: {chat_id}')
    logger.debug(f'prev_state: {prev_state}')
    logger.debug(f'message: {request_data["response"]}')
    bot_msgs = []
    if prev_state == "begin":
        
        # Update state
        db_set_state(chat_id, "hello")
        bot_msgs += bot_hello()
        
        
    elif prev_state == "hello":
        
        db_set_state(chat_id, "solicit_issue")
        bot_msgs += bot_solicit_issue()
    
    elif prev_state == "solicit_issue":
        
        # Update state
        db_set_state(chat_id, "solicit_emotions")
        
        bot_msgs += bot_solicit_emotions()
    
    elif prev_state == "solicit_emotions":
        
        # Update state
        db_set_state(chat_id, "explain_emotions")
        
        # Parse and store selected emotions
        emotions = request_data.get("response", [])
        emotions = [{"emotion": emo} for emo in emotions]
        db_set_emotions(chat_id, emotions)
        
        # Get next bot message
        bot_msgs += bot_explain_emotions(chat_id, emotions)
    
    elif prev_state == "explain_emotions":
        
        emotions = db_get_emotions(chat_id)
        logger.debug(f'emotions: {emotions}')
        
        # Get next bot message or detect stage completion
        bot_msg_explain_emos = bot_explain_emotions(chat_id, emotions)
        bot_msg_text = bot_msg_explain_emos[0]['response']
        
        # If stage is completed...
        if "::finished::" in bot_msg_text.lower():
            # Update state
            db_set_state(chat_id, "solicit_values")
            
            # Add end of explain emotions message
            bot_msgs += [{
                "sender": "bot",
                "response": msgs["explain_emotions_end"],
                "widget_type": "text",
                "widget_config": {}
            }]
            
            # Add solicit_values message
            bot_msgs += bot_solicit_values(chat_id)
        
        # If state is ongoing...
        else:
            bot_msgs += bot_msg_explain_emos

    elif prev_state == "solicit_values":
        
        # Save values to database
        value_num = int(request_data['widget_config']['metadata'].get("val_num"))
        value_rating = int(request_data.get("response"))
        value_text = bot_data["vals"][value_num]
        db_add_value(chat_id, value_text, value_num, value_rating)
        
        user_vals = db_get_vals(chat_id)
        
        # Generate next message
        if len(user_vals) < len(bot_data["vals"]):
            bot_msgs += bot_solicit_values(chat_id)
        else:
            bot_msgs.append({
                "sender": "bot",
                "response": msgs['intro_reappraisal'],
                "widget_type": "text",
                "widget_config": {}
            })
            db_set_state(chat_id, "reappraisal")

        
    elif prev_state == "reappraisal":
        # Show each reappraisal one by one
        finished_reaps = db_get_reappraisals(chat_id)
        # logger.debug(f'finished_reaps: {finished_reaps}')
        if len(finished_reaps) < 3:
            bot_msgs += bot_reappraise(chat_id)
        else:
            # Show transition message to reappraisal judging section
            db_set_state(chat_id, "judge_reappraisals")
            bot_msgs += [{
                "sender": "bot",
                "response": msgs["intro_judge_reappraisals"],
                "widget_type": "text",
                "widget_config": {
                    "metadata": {
                        "msg_type": "intro_judge_reappraisals"
                    }
                }
            }]
            
    elif prev_state == "judge_reappraisals":
        
        reaps = db_get_reappraisals(chat_id)
        unjudged_reaps = [reap for reap in reaps if reap.get("reap_efficacy") is None]
        # logger.debug(request_data)
        
        # if the last message was judging reap success, save to db
        if request_data['widget_config']['metadata']['msg_type'] == "reappraisal_success":
            prev_reap_num = int(request_data['widget_config']['metadata'].get("reap_num"))
            prev_reap_efficacy = int(request_data.get("response"))
            prev_reap_entry = [reap for reap in reaps if reap.get("reap_num") == prev_reap_num][0]
            assert "reap_efficacy" not in prev_reap_entry.keys(), "Reappraisal efficacy already judged"
            db_add_reappraisal(reap_efficacy=prev_reap_efficacy, **prev_reap_entry)
            
        # Judge next reappraisal or finish
        if len(unjudged_reaps) > 1:  # 1 because another reap just got added
            bot_msgs += bot_judge_reappraisals(chat_id)
        else:
            # check if done
            db_set_state(chat_id, "finished")
            bot_msgs += bot_finished()
    
    else:
        return {"error": "Invalid state"}
    
    logger.debug(f'bot_msgs: {bot_msgs}')
    return {"messages": bot_msgs}
    
        
    
    
    # i'm getting repeat values