
import yaml
from logger_setup import setup_logger
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langchain.schema import HumanMessage, AIMessage
from typing import Literal, Dict, Any, List

from langchain_core.runnables import chain
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableMap, RunnableParallel

logger = setup_logger()

MODEL = ChatOpenAI(model="gpt-4o")

with open("bot.yml", "r") as ymlfile:
    bot_data = yaml.load(ymlfile, Loader=yaml.FullLoader)

with open("prompts.yml", "r") as ymlfile:
    prompts = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
with open("messages.yml", "r") as ymlfile:
    msgs = yaml.load(ymlfile, Loader=yaml.FullLoader)

@chain
def explain_emotions(input):
    messages = input["messages"]  # Chat history
    emotion_str = input["emotions"]  # String of emotions to explain
    
    # Create the list of emotions string to be inserted into the prompt
    # emotion_str = ""
    # for i, emo in enumerate(emotions):
    #     emotion_str += f"<emotion{i+1}>{emo}</emotion{i+1}>\n"
        
    # Call the model
    system_msg = [ChatPromptTemplate.from_template(prompts["explain_emo"])]
    msgs = system_msg + messages
    prompt = ChatPromptTemplate(msgs)
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({"emotion_str": emotion_str})

@chain
def generate_value_reap(input):
    messages = input["messages"]
    value = input["value"]  # Value according to which the bot will reappraise
    system_msg = ChatPromptTemplate.from_template(prompts["value_reappraise"])
    msgs = [system_msg] + messages
    prompt = ChatPromptTemplate(msgs)
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({"value": value})

@chain
def generate_general_reap(input):
    messages = input["messages"]
    system_msg = ChatPromptTemplate.from_template(prompts["general_reappraise"])
    msgs = [system_msg] + messages
    prompt = ChatPromptTemplate(msgs)
    chain = prompt | MODEL | StrOutputParser()
    return chain.invoke({})