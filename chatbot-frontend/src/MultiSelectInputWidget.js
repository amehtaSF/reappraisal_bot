import React, { useState, useEffect, useCallback } from 'react';

function MultiSelectInputWidget({ onSend, options = [], isSending }) {
  const [selectedOptions, setSelectedOptions] = useState([]);

  const handleOptionClick = (value) => {
    setSelectedOptions((prevSelected) =>
      prevSelected.includes(value)
        ? prevSelected.filter((option) => option !== value)
        : [...prevSelected, value]
    );
  };

  const handleSend = useCallback(() => {
    if (selectedOptions.length > 0) {
      onSend(selectedOptions);
    }
  }, [onSend, selectedOptions]);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !isSending) {
        handleSend();  // Trigger sending when Enter is pressed and not sending
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleSend, isSending]);

  return (
    <div className="multiselect-input-widget">
      <div className="options-container">
        {options.map((option, index) => {
          const value = option.value || option;
          const label = option.label || option;
          const isSelected = selectedOptions.includes(value);

          return (
            <button
              key={index}
              className={`option-button ${isSelected ? 'selected' : ''}`}
              onClick={() => handleOptionClick(value)}
              disabled={isSending}  // Disable option buttons when sending
            >
              {label}
            </button>
          );
        })}
      </div>
      <button className="send-button" onClick={handleSend} disabled={isSending}>
        Send
      </button>
    </div>
  );
}

export default MultiSelectInputWidget;