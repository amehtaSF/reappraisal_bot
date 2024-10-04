import React, { useState, useEffect, useCallback } from 'react';

function MultiSelectInputWidget({ onSend, options = [] }) {
  const [selectedOptions, setSelectedOptions] = useState([]);

  // Handle option click to toggle selection
  const handleOptionClick = (value) => {
    setSelectedOptions((prevSelected) =>
      prevSelected.includes(value)
        ? prevSelected.filter((option) => option !== value)
        : [...prevSelected, value]
    );
  };

  // Memoize handleSend to prevent it from being recreated on each render
  const handleSend = useCallback(() => {
    if (selectedOptions.length > 0) {
      onSend(selectedOptions);
    }
  }, [onSend, selectedOptions]);

  // Attach event listener to the whole widget for keydown events
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'Enter') {
        handleSend(); // Trigger sending when Enter is pressed
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleSend]); // Now handleSend is a stable reference

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
            >
              {label}
            </button>
          );
        })}
      </div>
      <button className="send-button" onClick={handleSend}>
        Send
      </button>
    </div>
  );
}

export default MultiSelectInputWidget;