import React, { useState } from 'react';

function SliderInputWidget({ onSend, min = 0, max = 100, step = 1, start = 50 }) { // Accept min and max as props
  const [value, setValue] = useState(start); // Default value is in the middle of min and max

  const handleSend = () => {
    onSend(value);
  };

  return (
    <div className="slider-input-widget">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <span>{value}</span>
      <button onClick={handleSend}>Send</button>
    </div>
  );
}

export default SliderInputWidget;