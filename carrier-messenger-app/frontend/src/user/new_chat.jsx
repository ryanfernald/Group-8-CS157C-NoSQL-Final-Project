import React from 'react';
import './styling/new_chat.css';

const NewChat = ({ onClose }) => {
  const handleCreate = () => {
    alert('New chat created!');
    onClose();
  };

  return (
    <div className="new-chat-overlay">
      <div className="new-chat-box">
        <h2>Start a New Chat</h2>
        <p>Enter the Username or Email of the new contact:</p>
        <input type="text" placeholder="Username or Email" className="new-chat-input" />
        <div className="new-chat-buttons">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button onClick={handleCreate} className="create-button">Create</button>
        </div>
      </div>
    </div>
  );
};

export default NewChat;