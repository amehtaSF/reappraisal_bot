import React from 'react';
import TextInputWidget from './TextInputWidget';
import MultiSelectInputWidget from './MultiSelectInputWidget';
import SliderInputWidget from './SliderInputWidget'; 

function InputWidget({ widgetType = 'text', onSend, widgetConfig = {} }) {  // Added widgetConfig as a prop
  const widgetComponents = {
    text: TextInputWidget,
    multiselect: MultiSelectInputWidget,
    slider: SliderInputWidget,
  };

  const WidgetComponent = widgetComponents[widgetType] || TextInputWidget;

  return (
    <div className="input-widget">
      <WidgetComponent onSend={onSend} {...widgetConfig} />
    </div>
  );
}

export default InputWidget;