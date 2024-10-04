import React, { useState, useEffect, useRef } from 'react';
import InputWidget from './InputWidget';
import MessageList from './MessageList';
import axios from 'axios';

function ChatWindow() {
    const [messages, setMessages] = useState([]);
    const [widgetType, setWidgetType] = useState('text');
    const [widgetConfig, setWidgetConfig] = useState({});
    const [jwtToken, setJwtToken] = useState(null);

    const messageListRef = useRef(null);

    const API_URL = process.env.REACT_APP_FLASK_API_URL;

    useEffect(() => {
        const login = async () => {
            try {
                const response = await axios.post("/api/login");
                const token = response.data.access_token;
                setJwtToken(token);
            } catch (error) {
                console.error('Login failed', error);
            }
        };
        login();
    }, [API_URL]);

    useEffect(() => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [messages]);

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
                "/api/chat",
                { response: userMessage, widget_type: widgetType, widget_config: widgetConfig },
                { headers: { Authorization: `Bearer ${jwtToken}` } }
            );

            const botMessages = response.data.messages;  // Expecting a list of messages

            // Loop through each message with a delay between them
            for (const message of botMessages) {
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { sender: 'bot', text: message.response }
                ]);
                setWidgetType(message.widget_type || 'text');
                setWidgetConfig(message.widget_config || {});

                // Scroll to the bottom after adding each message
                if (messageListRef.current) {
                    messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
                }

                // Wait for 1 second before displaying the next message
                await new Promise((resolve) => setTimeout(resolve, 1000));
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    return (
        <div className="chat-window">
            <MessageList messages={messages} messageListRef={messageListRef} />
            {/* Ensure unique key based on widgetConfig to force reset */}
            <InputWidget
                key={widgetType + JSON.stringify(widgetConfig)}
                widgetType={widgetType}
                onSend={sendMessage}
                widgetConfig={widgetConfig}
            />
        </div>
    );
}

export default ChatWindow;