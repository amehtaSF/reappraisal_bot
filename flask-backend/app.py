
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
from db import db_create_entry, db_get_entry, db_append_list, db_update_entry, db_add_message
from bot import parse_user_message

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

@app.route('/api/login', methods=['POST'])
def login():
    print("login")
    # Generate a chat id
    chat_id = str(uuid.uuid4())
    
    # Generate a JWT access token
    access_token = create_access_token(identity=chat_id)
    
    # Create a new chat entry in the database
    ip_address = request.remote_addr
    db_create_entry(chat_id, ip_address=ip_address)
    
    return jsonify(access_token=access_token), 200


@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    
    # Get the chat data
    chat_id = get_jwt_identity()
    user_data = db_get_entry(chat_id)
    messages = user_data.get('messages', [])
    
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
    logger.debug(f'user message received: {json.dumps(user_msg, indent=2)}')
    user_widget_type = request_data.get('widget_type')
    user_widget_config = request_data.get('widget_config', {})
    user_message = request_data.get('response')
    print(f'user_message: {user_message}')
    
    # Error checking
    # if not user_message:
    #     return jsonify({'response': 'error: missing message'})
    # if not user_widget_type:
    #     return jsonify({'response': 'error: missing widget_type'})
    
    
    # Parse out specific data from the user message and get next message
    next_msg = parse_user_message(chat_id, request_data)
    logger.debug(next_msg)
    db_add_message(chat_id, "bot", next_msg)
    
    
    logger.debug(f'app message send: {json.dumps(next_msg, indent=2)}')
    return jsonify(next_msg), 200



if __name__ == '__main__':
    app.run(debug=False)