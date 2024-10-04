import React, { useState, useEffect, useRef } from 'react';
import InputWidget from './InputWidget';
import MessageList from './MessageList';
import axios from 'axios';

function ChatWindow() {
    const [messages, setMessages] = useState([]);
    const [widgetType, setWidgetType] = useState('text');
    const [widgetConfig, setWidgetConfig] = useState({});
    const [jwtToken, setJwtToken] = useState(null);

    const messageListRef = useRef(null);  // Reference for the message list container

    // Get the API URL from the environment variable
    const API_URL = process.env.REACT_APP_FLASK_API_URL;

    // Login and retrieve the JWT token when the component is mounted
    useEffect(() => {
        const login = async () => {
            console.log('Logging in...', API_URL);
            try {
                const response = await axios.post(`${API_URL}/api/login`);
                const token = response.data.access_token;
                setJwtToken(token); // Store the JWT token in state
            } catch (error) {
                console.error('Login failed', error);
            }
        };

        login(); // Call the login function when the component mounts
    }, [API_URL]);

    // Scroll to the bottom of the message list when messages change
    useEffect(() => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [messages]);

    // Function to send a message to the chat API (onSend callback)
    const sendMessage = async (userMessage) => {
        // Show the user's message immediately
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'user', text: userMessage }
        ]);

        if (!jwtToken) {
            console.error('JWT token not available');
            return;
        }

        try {
            // Send the user's message to the API and get the bot's response
            const response = await axios.post(
                `${API_URL}/api/chat`,
                { response: userMessage, 
                    widget_type: widgetType,
                    widget_config: widgetConfig },
                {
                    headers: {
                        Authorization: `Bearer ${jwtToken}` // Include JWT token in Authorization header
                    }
                }
            );

            const botMessage = response.data.response;
            const newWidgetType = response.data.widget_type || 'text'; // Retrieve new widget type from API
            const newWidgetConfig = response.data.widget_config || {}; // Retrieve new widget config from API

            // Append the bot's response once it's ready
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: 'bot', text: botMessage },
            ]);

            // Update widget type and config based on the bot response
            setWidgetType(newWidgetType);
            setWidgetConfig(newWidgetConfig);
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    return (
        <div className="chat-window">
            {/* Pass messageListRef to the MessageList component */}
            <MessageList messages={messages} messageListRef={messageListRef} />
            <InputWidget widgetType={widgetType} onSend={sendMessage} widgetConfig={widgetConfig} />
        </div>
    );
}

export default ChatWindow;