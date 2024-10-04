import React, { useState } from 'react';

function MultiSelectInputWidget({ onSend, options = []}) {
  const [selectedOptions, setSelectedOptions] = useState([]);

  // Handle option click to toggle selection
  const handleOptionClick = (value) => {
    setSelectedOptions((prevSelected) =>
      prevSelected.includes(value)
        ? prevSelected.filter((option) => option !== value)
        : [...prevSelected, value]
    );
  };

  // Handle sending the selected options
  const handleSend = () => {
    if (selectedOptions.length > 0) {
      onSend(selectedOptions);
    }
  };

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