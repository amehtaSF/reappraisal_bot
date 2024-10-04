import React, { useState, useEffect, useCallback } from 'react';

function SliderInputWidget({ onSend, min = 0, max = 100, step = 1, start = 50, isSending }) {
  const [value, setValue] = useState(start);

  useEffect(() => {
    setValue(start); // Reset the value to the "start" value when the widget is re-rendered
  }, [start]);

  const handleSend = useCallback(() => {
    onSend(value);  // Send the most up-to-date slider value
  }, [onSend, value]);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !isSending) {
        handleSend();  // Trigger sending when Enter is pressed
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleSend, isSending]);

  return (
    <div className="slider-input-widget">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={isSending}  // Disable slider when sending
      />
      <span>{value}</span>
      <button onClick={handleSend} disabled={isSending}>
        Send
      </button>
    </div>
  );
}

export default SliderInputWidget;