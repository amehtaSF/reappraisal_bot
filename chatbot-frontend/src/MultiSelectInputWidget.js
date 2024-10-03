import React, { useState } from 'react';

function MultiSelectInputWidget({ onSend, options = [] }) {
  const [selectedOptions, setSelectedOptions] = useState([]);

  // Handle selection changes
  const handleSelectionChange = (event) => {
    const selected = Array.from(event.target.selectedOptions, (option) => option.value);
    setSelectedOptions(selected);
  };

  // Handle sending the selected options
  const handleSend = () => {
    if (selectedOptions.length > 0) {
      onSend(selectedOptions);
    }
  };

  return (
    <div className="multiselect-input-widget">
      <select multiple value={selectedOptions} onChange={handleSelectionChange} size={options.length > 5 ? 5 : options.length}>
        {options.map((option, index) => (
          <option key={index} value={option.value || option}>
            {option.label || option}
          </option>
        ))}
      </select>
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

export default MultiSelectInputWidget;