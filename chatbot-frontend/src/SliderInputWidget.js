import React, { useState } from 'react';

function SliderInputWidget({ onSend, min = 0, max = 100 }) { // Accept min and max as props
  const [value, setValue] = useState((min + max) / 2); // Default value is in the middle of min and max

  const handleSend = () => {
    onSend(value); // Send the value and the widget type
  };

  return (
    <div className="slider-input-widget">
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <span>{value}</span>
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

export default SliderInputWidget;