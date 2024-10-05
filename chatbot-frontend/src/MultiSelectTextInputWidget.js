import React, { useState, useEffect, useCallback } from 'react';

function MultiSelectInputWidget({ onSend, options = [], isSending }) {
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [inputValue, setInputValue] = useState('');

  const handleOptionClick = (value) => {
    setSelectedOptions((prevSelected) => {
      let newSelected;
      if (prevSelected.includes(value)) {
        // Remove value from selectedOptions
        newSelected = prevSelected.filter((option) => option !== value);

        // Remove value from inputValue
        setInputValue((prevInput) => {
          const regex = new RegExp(`\\b${value}\\b`, 'g');
          return prevInput.replace(regex, '').replace(/\s+/g, ' ').trim();
        });
      } else {
        // Add value to selectedOptions
        newSelected = [...prevSelected, value];

        // Add value to inputValue
        setInputValue((prevInput) => {
          if (prevInput.includes(value)) {
            return prevInput; // Value already in inputValue
          } else {
            return (prevInput + ' ' + value).trim();
          }
        });
      }
      return newSelected;
    });
  };

  const handleInputChange = (event) => {
    const newValue = event.target.value;
    setInputValue(newValue);

    // Update selectedOptions based on inputValue
    const tokens = newValue.split(/\s+/);
    const newSelectedOptions = options
      .map((option) => (option.value || option))
      .filter((value) => tokens.includes(value));

    setSelectedOptions(newSelectedOptions);
  };

  const handleSend = useCallback(() => {
    if (inputValue.trim().length > 0) {
      onSend(inputValue);
    }
  }, [onSend, inputValue]);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !isSending) {
        handleSend(); // Trigger sending when Enter is pressed and not sending
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
              disabled={isSending} // Disable option buttons when sending
            >
              {label}
            </button>
          );
        })}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        disabled={isSending}
        className="multiselect-text-input"
      />
      <button className="send-button" onClick={handleSend} disabled={isSending}>
        Send
      </button>
    </div>
  );
}

export default MultiSelectInputWidget;