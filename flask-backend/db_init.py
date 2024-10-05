
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

boto3.set_stream_logger('botocore', level=logging.DEBUG)

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


TABLE_PREFIX = "vbr_bot_career"
RCU = 5
WCU = 5

'''
New DB schema

Tables - primary key, sort key:
- Messages - chat_id, timestamp: 1 item = 1 message (note: i should tag them with if they are the issue or not)
- State - chat_id - 1 item = 1 conversation
- Emotions - chat_id, timestamp: 1 item = 1 user
    - dict with single key "emotion" (some day will expand to put "reason")
- Values - chat_id: 1 item = 1 value
- Reappraisals - chat_id: 1 item = 1 reappraisal
    - dict with keys "reap_text", "reap_num", "value_text", "value_rank", "value_rating", "reap_efficacy"
- Conversations - chat_id: 1 item = 1 user :: columns: chat_id, created, completed, ip_address
'''

tables = [
    {
        "table_name": f"{TABLE_PREFIX}_convos",
        "partition_key": ("chat_id", "S"),
        "sort_key": ("timestamp", "S"),
    },
    {
        "table_name": f"{TABLE_PREFIX}_messages",
        "partition_key": ("chat_id", "S"),
        "sort_key": ("timestamp", "S"),
        # dict with keys "sender", "text", "timestamp", "widget_type", "widget_config"
    },
    {
        "table_name": f"{TABLE_PREFIX}_state",
        "partition_key": ("chat_id", "S"),
        # current state of the conversation
    },
    {
        "table_name": f"{TABLE_PREFIX}_emotions",
        "partition_key": ("chat_id", "S"),
        # "sort_key": ("timestamp", "S"),
        # dict with single key "emotion" (some day will expand to put "reason")
    },
    {
        "table_name": f"{TABLE_PREFIX}_values",
        "partition_key": ("chat_id", "S"),
        "sort_key": ("timestamp", "S"),
    },
    {
        "table_name": f"{TABLE_PREFIX}_reappraisals",
        "partition_key": ("chat_id", "S"),
        "sort_key": ("timestamp", "S"),
    }
]

for tbl in tables:
    key_schema = [
        {
            'AttributeName': tbl["partition_key"][0],
            'KeyType': 'HASH'
        }
    ]
    if "sort_key" in tbl:
        key_schema.append(
            {
                'AttributeName': tbl["sort_key"][0],
                'KeyType': 'RANGE'
            }
        )
        
    attribute_definitions = [
        {
            'AttributeName': tbl["partition_key"][0],
            'AttributeType': tbl["partition_key"][1]
        }
    ]
    if "sort_key" in tbl:
        attribute_definitions.append(
            {
                'AttributeName': tbl["sort_key"][0],
                'AttributeType': tbl["sort_key"][1]
            }
        )
    table = dynamodb.create_table(
        TableName=tbl["table_name"],
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput={
            'ReadCapacityUnits': RCU,
            'WriteCapacityUnits': WCU
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=tbl["table_name"])
    

    # Wait until the table exists
    table.meta.client.get_waiter('table_exists').wait(TableName=tbl["table_name"])

    print(f"Table status: {table.table_status}")
