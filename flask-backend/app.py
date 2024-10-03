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
from .db import db_create_entry, db_get_entry

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
    data = request.get_json()
    user_widget_type = data.get('widget_type')
    user_widget_config = data.get('widget_config', {})
    user_message = data.get('user_message')
    
    # Error checking
    if not user_message:
        return jsonify({'response': 'error: missing message'})
    if not user_widget_type:
        return jsonify({'response': 'error: missing widget_type'})

    # Process user input and generate a response
    response = process_user_input(user_input, widget_type)

    # Store the conversation
    # messages.append({
    #     'user': user_input,
    #     'bot': response,
    #     'widget_type': widget_type,
    #     'timestamp': datetime.now().isoformat()
    # })
    messages.append({
        'sender': 'user',
        'text': user_message,
        'widget_type': user_widget_type,
        'widget_config': user_widget_config,
        'timestamp': datetime.now().isoformat()
    })
    messages.append({
        'sender': 'bot',
        'text': response,
        'widget_type': widget_type,
        'widget_config': widget_config,
        'timestamp': datetime.now().isoformat()
    })


    return jsonify({'response': response})

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