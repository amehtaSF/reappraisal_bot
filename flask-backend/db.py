import boto3

import os
import uuid
from datetime import datetime, timezone
from datetime import datetime
from dotenv import load_dotenv

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

'''
db schema
{
    chat_id: str  # unique id
    token: str  # security token for the chat
    created: str  # timestamp of when the chat was created
    token_expiration: str  # timestamp of when the chat will expire
    messages: list  # list of 3-tuples with values for role, content, and timestamp
    completed: int  # 0 if the chat is not completed, 1 if the chat is completed
    prolific_id: str  # prolific id of the user
}

'''


table = dynamodb.Table(os.getenv('DYNAMODB_TABLE_NAME'))


def db_create_entry(chat_id, **kwargs):
    '''Initialize a new entry in the table'''
    item = {
        "chat_id": chat_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "messages": [],  # list of dicts with keys "sender", "text", "timestamp", "widget_type", "widget_config"
        "completed": 0,  # 0 if the chat is not completed, 1 if the chat is completed,
        "state": "begin",
        "ip_address": "",
        "emotions": [],  # list of len 3 where each element is a dict with keys emotion and reason. if emotion == other, then there is another key called other_emotion
        "vals": [],  # list of len 15 with dicts with keys "value_text", "value_num", "value_rating"
        # "prolific_id": "",
        # "person_values": {"v" + str(i+1): int(-99) for i in range(16)},
        # "issue": "",
        # "issue_summary_bot": "",
        # "issue_summary": "",
        # "crisis_input": "",
        # "reappraisals": [{"reappraisal": "", "reappraisal_value": "", "value_rank": "", "rating": "", "efficacy": "", "believability": "", "rank": ""} for _ in range(3)], 
    }
    item.update(kwargs)
    table.put_item(Item=item)
    return chat_id

def db_get_entry(chat_id):
    '''Get an entry from the table'''
    response = table.get_item(Key={'chat_id': str(chat_id)})
    item = response['Item']
    return item

def db_update_entry(chat_id, key, value):
    '''Update a simple entry in the table, allowing for various data types (e.g., dict, list, etc.)'''
    # Ensure key and value retain their original types
    table.update_item(
        Key={
            'chat_id': str(chat_id)
        },
        UpdateExpression=f"set #key = :val",
        ExpressionAttributeNames={
            '#key': key  
        },
        ExpressionAttributeValues={
            ':val': value  
        },
        ReturnValues="UPDATED_NEW"
    )
    
def db_update_nested_field(chat_id, list_name, index, field, new_value):
    '''Update a specific field within a list of dictionaries at a given index.'''
    # Update the specific field in a nested list of dictionaries
    table.update_item(
        Key={
            'chat_id': str(chat_id)
        },
        UpdateExpression=f"set #{list_name}[{index}].{field} = :val",
        ExpressionAttributeNames={
            f'#{list_name}': list_name  # Ensure the list field is recognized
        },
        ExpressionAttributeValues={
            ':val': new_value  # New value to update
        },
        ReturnValues="UPDATED_NEW"
    )

def db_append_list(chat_id, key, value):
    '''Append any value (str, dict, etc.) to an existing list in the DynamoDB table'''
    table.update_item(
        Key={
            'chat_id': str(chat_id)
        },
        UpdateExpression=f"SET {key} = list_append(if_not_exists({key}, :empty_list), :val)",
        ExpressionAttributeValues={
            ':val': [value],  # Append the value (wrapped in a list for list_append)
            ':empty_list': []  # Fallback to an empty list if the key doesn't exist
        },
        ReturnValues="UPDATED_NEW"
    )

# def db_add_message(chat_id, role, content):
#     '''Add a message to the messages list in the table'''
#     role = str(role)
#     content = str(content)
#     timestamp = datetime.now(timezone.utc).isoformat()
#     db_append_list(chat_id, "messages", (role, content, timestamp))