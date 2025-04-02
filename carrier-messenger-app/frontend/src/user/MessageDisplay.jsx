import React, { useState, useEffect, useRef } from 'react';
import './styling/MessageDisplay.css';
import carrierPigeonLogo from '../assets/carrierpigeon-logo.svg';
import MessageUserHeader from './message_user_header';

const MessageDisplay = ({ messages, onSendMessage, selectedContact }) => {
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null); // Ref to track the end of the messages list

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

  const parseMessage = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic text
      .replace(/__(.*?)__/g, '<u>$1</u>'); // Underline text
  };

  // Scroll to the bottom of the messages list whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="message-display">
      <img src={carrierPigeonLogo} alt="Carrier Pigeon Logo" className="logo-overlay" />
      <MessageUserHeader contact={selectedContact} />
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.isUser ? 'user-message' : 'incoming-message'}`}>
            <div dangerouslySetInnerHTML={{ __html: parseMessage(message.text) }} />
          </div>
        ))}
        {/* Invisible div to ensure scrolling to the bottom */}
        <div ref={messagesEndRef} />
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