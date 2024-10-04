from .logger_setup import setup_logger
import json
from flask import Flask, request, jsonify
from langchain_community.chat_message_histories import (
    DynamoDBChatMessageHistory,
)
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
from .db import db_create_entry, db_get_entry, db_append_list, db_update_entry, db_add_message
from .bot import parse_user_message

logger = setup_logger()

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True, 
    origins=["http://localhost:3000"], # You'll need this, you cannot use * (wildcard domain) when using supports_credentials=True
)

# setup JWT
app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

# setup chat history 
# chat_history = []
# lc_history = DynamoDBChatMessageHistory(table_name=os.environ['DYNAMODB_TABLE_NAME'], session_id="0")

'''
bot can send different kinds of messages. messages sent from bot take the form of a dictionary with the following keys:
- message: the text of the message
- widget_type: the type of widget to display (e.g., text, select)
- widget_config: a dictionary with additional properties for the widget (e.g., options for a select widget)
- state: a string with the current state of the conversation 
    - solicit_issue
    - solicit_emotions
    - collect_reap_feedback

Widget properties:
- text: no additional properties
- slider: min, max, default, step
- multiselect: options (list of dicts with keys "val" and "label")
'''

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
    
    return jsonify(access_token=access_token)

@app.route('/api/test_chat', methods=['POST'])
@jwt_required()
def test_chat():
    print("chat")
    return jsonify({'response': 'Hello, world!'})

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
    if not user_message:
        return jsonify({'response': 'error: missing message'})
    if not user_widget_type:
        return jsonify({'response': 'error: missing widget_type'})
    
    
    # Parse out specific data from the user message and get next message
    next_msg = parse_user_message(chat_id, request_data)
    for msg in next_msg['messages']:
        db_add_message(chat_id, "bot", msg)
    
    
    logger.debug(f'app message send: {json.dumps(next_msg, indent=2)}')
    return jsonify(next_msg), 200

# def process_user_input(user_input, widget_type):
#     # Basic processing based on widget type
#     if widget_type == 'text':
#         return f"You said: {user_input}"
#     elif widget_type == 'number':
#         return f"You entered the number: {user_input}"
#     elif widget_type == 'select':
#         return f"You selected: {user_input}"
#     else:
#         return f"Received: {user_input}"
    


if __name__ == '__main__':
    app.run(debug=True, port=80)