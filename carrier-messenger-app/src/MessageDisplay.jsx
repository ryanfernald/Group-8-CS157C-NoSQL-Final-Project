import React, { useState } from 'react';
import './MessageDisplay.css';
import carrierPigeonLogo from '../public/carrierpigeon-logo.svg';

const MessageDisplay = ({ messages, onSendMessage }) => {
  const [newMessage, setNewMessage] = useState('');

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
  };

  const handleSendMessage = () => {
    if (newMessage.trim() !== '') {
      onSendMessage(newMessage);
      setNewMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="message-display">
      <img src={carrierPigeonLogo} alt="Carrier Pigeon Logo" className="logo-overlay" />
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.isUser ? 'user-message' : 'incoming-message'}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      <div className="message-box">
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default MessageDisplay;