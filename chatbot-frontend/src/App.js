import logo from './logo.svg';
import './App.css';


import React from 'react';
import ChatWindow from './ChatWindow';
import MessageList from './MessageList';
import InputWidget from './InputWidget';
import TextInputWidget from './TextInputWidget';
import SliderInputWidget from './SliderInputWidget';

function App() {

  return (
    <div className="App">
      <h1>Reframing Bot</h1>
      <ChatWindow />
    </div>
  );
}

export default App;