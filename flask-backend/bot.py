import yaml
import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import chain
from langchain.schema import HumanMessage, AIMessage
from typing import Literal, Dict, Any, List

from langchain_core.runnables import chain
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
import random
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableMap, RunnableParallel
from .db import db_get_entry


MODEL = "gpt-4o"

with open("bot.yml", "r") as ymlfile:
    bot_data = yaml.load(ymlfile, Loader=yaml.FullLoader)

with open("prompts.yml", "r") as ymlfile:
    prompts = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
with open("messages.yml", "r") as ymlfile:
    msgs = yaml.load(ymlfile, Loader=yaml.FullLoader)
    

@chain
def test_convo(messages):
    prompt = ChatPromptTemplate.from_template(prompts["test_prompt"])
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({"messages": messages})


@chain
def explain_emotions(input):
    messages = input["messages"]  # Chat history
    emotions = input["emotions"]  # List of user-selected emotions
    
    # Create the list of emotions string to be inserted into the prompt
    emotion_str = ""
    for i, emo in enumerate(emotions):
        emotion_str += f"<emotion{i+1}>{emo}</emotion{i+1}>\n"
        
    # Call the model
    system_msg = [ChatPromptTemplate.from_template(prompts["explain_emo"])]
    msgs = system_msg + messages
    prompt = ChatPromptTemplate(msgs)
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({"emotion_str": emotion_str})

@chain
def generate_value_reap(input):
    messages = input["messages"]  # Chat history
    value = input["value"]  # Value according to which the bot will reappraise
    system_msg = ChatPromptTemplate.from_template(prompts["value_reappraise"])
    msgs = [system_msg] + messages
    prompt = ChatPromptTemplate(msgs)
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({"value": value})


def bot_solicit_issue():
    resp = 
    return msgs["solicit_issue"]

def bot_solicit_emotions():
    

def generate_next_message(chat_id):
    '''
    Determine the next message to send
    '''
    data = db_get_entry(chat_id)
    state = data["state"]  
    if state == "begin":
        return bot_solicit_issue()
    elif state == "solicit_issue":
        return "solicit_emotions"
    elif state == "solicit_emotions":
        return "explain_emotions"
    elif state == "explain_emotions":
        emotions = data.get("emotions", [])
        remaining = [emo.get("emotion") for emo in emotions if emo.get("reason") and emo.get("emotion")]
        next_state = "explain_emotions" if remaining else "solicit_values"
        return next_state
    elif state == "solicit_values":
        vals = data.get("vals", [])
        done_val_nums = [val.get("value_num") for val in vals if val.get("value_num")]
        remaining = [i for i in range(1, bot_data['num_values']+1) if i not in done_val_nums]
        if remaining:
            return "solicit_values"
        else:
            return "collect_reap_feedback"
    elif state == "reappraisal":
        return 
    else:
        return {"error": "Invalid state"}
    