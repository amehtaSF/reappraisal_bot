
from logger_setup import setup_logger
import json
from flask import Flask, request, jsonify
from langchain_community.chat_message_histories import (
    DynamoDBChatMessageHistory,
)
from decimal import Decimal
import os
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from flask_cors import CORS
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from db import db_new_chat, db_add_message
# from bot import parse_user_message
from bot_refactor import process_next_step

logger = setup_logger()

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True, 
    origins=["http://localhost:3000", "http://localhost"], # can't use * (wildcard domain) when using supports_credentials=True
)

# setup JWT
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

def format_json(data, indent=2):
    # json dumps, but first convert Decimal to float
    return json.dumps(data, indent=indent, default=lambda x: float(x) if isinstance(x, Decimal) else x)

@app.route('/api/login', methods=['POST'])
def login():

    # Generate a chat id
    chat_id = str(uuid.uuid4())
    
    # Get PID from request if it exists
    request_data = request.get_json()
    pid = request_data.get('pid')
    
    # Generate a JWT access token
    access_token = create_access_token(identity=chat_id)
    
    # Get ip address
    ip_address = request.remote_addr
    
    # Create a new chat in the database
    new_chat = {"chat_id": chat_id, "ip_address": ip_address}
    if pid:
        new_chat["pid"] = pid
    db_new_chat(**new_chat)
    logger.debug(f'new chat created: {format_json(new_chat, indent=2)}')
    
    return jsonify(access_token=access_token), 200


@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    
    # Get the chat data
    chat_id = get_jwt_identity()
    
    # Get the request data
    request_data = request.get_json()
    user_msg = {
        'sender': 'user',
        'response': request_data.get('response'),
        'widget_type': request_data.get('widget_type'),
        'widget_config': request_data.get('widget_config', {}),
        'timestamp': datetime.now().isoformat()
    }
    db_add_message(chat_id, "user", user_msg)
    logger.debug(f'user message received: {format_json(user_msg, indent=2)}')
    user_message = request_data.get('response')
    logger.debug(f'user_message: {user_message}')
    
    # Parse out specific data from the user message and get next message
    next_bot_msgs = process_next_step(chat_id, request_data)
    logger.debug(next_bot_msgs)
    for message in next_bot_msgs['messages']:
        db_add_message(chat_id, "bot", message)
    
    logger.debug(f'app message send: {format_json(next_bot_msgs, indent=2)}')
    return jsonify(next_bot_msgs), 200



if __name__ == '__main__':
    app.run(debug=False)