import React, { useState, useEffect, useCallback } from 'react';

function SliderInputWidget({ onSend, min = 0, max = 100, step = 1, start = 50 }) {
  const [value, setValue] = useState(start);

  // Reset the slider value whenever the "start" prop changes
  useEffect(() => {
    setValue(start); // Reset the value to the "start" value when the widget is re-rendered
  }, [start]);

  // Memoize handleSend to prevent it from being recreated on each render
  const handleSend = useCallback(() => {
    onSend(value);  // Send the most up-to-date slider value
  }, [onSend, value]);

  // Attach event listener to the whole widget for keydown events
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'Enter') {
        handleSend();  // Trigger sending when Enter is pressed
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleSend]);  // Now handleSend is a stable reference

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