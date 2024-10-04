import React, { useState, useRef, useEffect } from 'react';

function TextInputWidget({ onSend, isSending }) {
    const [input, setInput] = useState('');
    const inputRef = useRef(null);  // Create a ref for the input element

    const handleSend = () => {
        if (input.trim() === '') return;
        onSend(input); // Send the input 
        setInput('');  // Clear the input field
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !isSending) {
            handleSend(); // Trigger sending when Enter is pressed
        }
    };

    // Refocus the input field when it becomes available
    useEffect(() => {
        if (!isSending && inputRef.current) {
            inputRef.current.focus();  // Focus the input field when not sending
        }
    }, [isSending]);  // Trigger refocus when isSending changes

    return (
        <div className="text-input-widget">
            <input
                ref={inputRef}  // Attach the ref to the input element
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message..."
                disabled={isSending}  // Disable input when sending
            />
            <button onClick={handleSend} disabled={isSending}>
                Send
            </button>
        </div>
    );
}

export default TextInputWidget;