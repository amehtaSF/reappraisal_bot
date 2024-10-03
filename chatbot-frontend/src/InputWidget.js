import React from 'react';
import TextInputWidget from './TextInputWidget';
import MultiSelectInputWidget from './MultiSelectInputWidget';
// import NumberInputWidget from './NumberInputWidget';
// import SelectInputWidget from './SelectInputWidget';
// import DateInputWidget from './DateInputWidget';
import SliderInputWidget from './SliderInputWidget'; 

function InputWidget({ widgetType = 'text', onSend }) {
  const widgetComponents = {
    text: TextInputWidget,
    multiselect: MultiSelectInputWidget,
    // number: NumberInputWidget,
    // select: SelectInputWidget,
    // date: DateInputWidget,
    slider: SliderInputWidget, 
  };

  const WidgetComponent = widgetComponents[widgetType] || TextInputWidget;

  return (
    <div className="input-widget">
      <WidgetComponent onSend={onSend} />
    </div>
  );
}

export default InputWidget;