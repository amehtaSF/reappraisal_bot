import React, { useState } from 'react';

function TextInputWidget({ onSend }) {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim() === '') return;
        onSend(input); // Send the input 
        setInput('');
    };

    // Function to handle key press events
    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleSend(); // Trigger sending when Enter is pressed
        }
    };

    return (
        <div className="text-input-widget">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message..."
            />
            <button onClick={handleSend}>Send</button>
        </div>
    );
}

export default TextInputWidget;