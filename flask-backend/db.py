import boto3
from logger_setup import setup_logger
import os
import uuid
from datetime import datetime, timezone
from datetime import datetime
import random
import yaml
from decimal import Decimal
from dotenv import load_dotenv
import logging

# boto3.set_stream_logger('botocore', level=logging.DEBUG)

logger = setup_logger()
load_dotenv()


aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_DEFAULT_REGION')


dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)



convo_tbl = dynamodb.Table('vbr_bot_career_convos')
state_tbl = dynamodb.Table('vbr_bot_career_state')
msg_tbl = dynamodb.Table('vbr_bot_career_messages')
emotions_tbl = dynamodb.Table('vbr_bot_career_emotions')
values_tbl = dynamodb.Table('vbr_bot_career_values')
reappraisals_tbl = dynamodb.Table('vbr_bot_career_reappraisals')


with open("bot.yml", "r") as ymlfile:
    bot_data = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
def db_new_chat(chat_id, ip_address, **kwargs):
    '''Initialize a new chat in the database'''
    
    # Create convo item
    convo_item = {
        "chat_id": chat_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "completed": 0,  # 0 if the chat is not completed, 1 if the chat is completed,
        "ip_address": ip_address,
    }
    for key, val in kwargs.items():
        convo_item[key] = val
    convo_tbl.put_item(Item=convo_item)
    
    # Create state item (keep this as separate table since it is read/written often)
    state_item = {
        "chat_id": chat_id,
        "state": "begin"
    }
    state_tbl.put_item(Item=state_item)
    
    return chat_id

def db_add_message(chat_id, sender, data):
    '''Add a single message as a new item to the table'''
    if sender not in ["user", "bot"]:
        raise ValueError("Sender must be 'user' or 'bot'")
    msg = {
        "chat_id": chat_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Sort key
        "sender": sender,
        "response": data['response'],
        "state": db_get_state(chat_id), #  TODO: might want to pass this around in a different way. e.g. state gets passed with everything
        "widget_type": data.get('widget_type'),
        "widget_config": data.get("widget_config", {})
    }
    msg_tbl.put_item(Item=msg)

def db_set_state(chat_id, new_state):
    '''Update the state of the conversation'''
    state_tbl.update_item(
        Key={
            'chat_id': chat_id
        },
        UpdateExpression="set #s = :new_state",
        ExpressionAttributeNames={
            '#s': 'state'
        },
        ExpressionAttributeValues={
            ':new_state': new_state
        }
    )

def db_get_messages(chat_id):
    '''Get all messages for a given chat_id'''
    response = msg_tbl.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id),
        ScanIndexForward=True  # Sort by timestamp
    )
    messages = response.get('Items', [])
    return messages

def db_get_issue_messages(chat_id):
    # TODO: test this
    issue_states = ['begin', 'solicit_issue', 'solicit_emotions', 'explain_emotions']
    messages = db_get_messages(chat_id)
    issue_messages = [msg for msg in messages if msg['state'] in issue_states]
    return issue_messages

 
def db_get_state(chat_id):
    '''Get the current state of the conversation'''
    response = state_tbl.get_item(Key={'chat_id': chat_id})
    return response['Item'].get('state')

def db_get_emotions(chat_id):
    '''Get the users emotions'''
    response = emotions_tbl.get_item(Key={'chat_id': chat_id})
    return response['Item'].get('emotions', {})

def db_get_vals(chat_id):
    '''Get the users values'''
    response = values_tbl.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id),
        ScanIndexForward=True  # Sort by timestamp
    )
    vals = response.get('Items', [])
    return vals

def db_add_reappraisal(chat_id, **kwargs):
    '''Add a reappraisal to the users reappraisals'''
    item = {
        'chat_id': chat_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    for key, val in kwargs.items():
        item[key] = val
    reappraisals_tbl.put_item(Item=item)


def db_get_reappraisals(chat_id):
    '''Get the users reappraisals'''
    response = reappraisals_tbl.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id),
        ScanIndexForward=True  # Sort by timestamp
    )
    reappraisals = response.get('Items', [])
    return reappraisals



def db_set_emotions(chat_id, emotions):
    '''Set the users emotions'''
    emotions_tbl.put_item(Item={'chat_id': chat_id, 'emotions': emotions})
    
def db_add_value(chat_id, value_text, value_num, value_rating):
    '''Add a value to the users values'''
    item = {
        'chat_id': chat_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'value_text': value_text,
        'value_num': value_num,
        'value_rating': value_rating
    }
    values_tbl.put_item(Item=item)


def db_add_reappraisal(chat_id, **kwargs):
    '''Add a reappraisal to the users reappraisals'''
    item = {
        'chat_id': chat_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    for key, val in kwargs.items():
        item[key] = val
    reappraisals_tbl.put_item(Item=item)
    

def db_update_reappraisal(chat_id, timestamp, **kwargs):
    '''Update a reappraisal'''
    update_expr = "set "
    expr_attr_vals = {}
    for key, val in kwargs.items():
        update_expr += f"#{key} = :{key}, "
        expr_attr_vals[f":{key}"] = val
    update_expr = update_expr[:-2]  # Remove trailing comma
    expr_attr_vals[":timestamp"] = timestamp
    response = reappraisals_tbl.update_item(
        Key={
            'chat_id': chat_id,
            'timestamp': timestamp
        },
        UpdateExpression=update_expr,
        ExpressionAttributeNames={f"#{key}": key for key in kwargs.keys()},
        ExpressionAttributeValues=expr_attr_vals
    )
    return response

def db_update_convo_completion(chat_id, completion: int):
    '''Mark a conversation as completed'''
    convo_tbl.update_item(
        Key={
            'chat_id': chat_id
        },
        UpdateExpression="set #c = :completed",
        ExpressionAttributeNames={
            '#c': 'completed'
        },
        ExpressionAttributeValues={
            ':completed': completion
        }
    )