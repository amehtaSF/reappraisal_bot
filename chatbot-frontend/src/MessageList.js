import React from 'react';
import DOMPurify from 'dompurify'; // Import DOMPurify

function MessageList({ messages, messageListRef }) {
  return (
    <div className="message-list" ref={messageListRef}>
      {messages.map((msg, idx) => {
        const sanitizedText = DOMPurify.sanitize(msg.text);  // Sanitize each message's text
        return (
          <div key={idx} className={`message ${msg.sender}-message`}>
            <div dangerouslySetInnerHTML={{ __html: sanitizedText }} />  
          </div>
        );
      })}
    </div>
  );
}

export default MessageList;