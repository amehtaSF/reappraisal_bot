import React, { useState, useEffect } from 'react';
import TextInputWidget from './TextInputWidget';
import MultiSelectInputWidget from './MultiSelectInputWidget';
import MultiSelectTextInputWidget from './MultiSelectTextInputWidget';
import SliderInputWidget from './SliderInputWidget'; 

function InputWidget({ widgetType = 'text', onSend, widgetConfig = {} }) {  
  const [isSending, setIsSending] = useState(false);  // Track if message is being sent

  const widgetComponents = {
    text: TextInputWidget,
    multiselect: MultiSelectInputWidget,
    multiselecttext: MultiSelectTextInputWidget,
    slider: SliderInputWidget,
  };

  const WidgetComponent = widgetComponents[widgetType] || TextInputWidget;

  // Function to handle sending the message
  const handleSend = (message) => {
    setIsSending(true);  // Disable the send button after sending the message
    onSend(message);      // Call the parent onSend function
  };

  useEffect(() => {
    setIsSending(false);  // Re-enable send button when a new bot message is received
  }, [widgetType, widgetConfig]);  // Reset when a new widget type or config is received

  return (
    <div className="input-widget">
      <WidgetComponent onSend={handleSend} isSending={isSending} {...widgetConfig} />
    </div>
  );
}

export default InputWidget;