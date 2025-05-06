import React, { useState } from 'react';
import './styling/new_chat.css';

const NewChat = ({ onClose }) => {
  const [input, setInput] = useState('');

  const handleCreateChat = async () => {
    const currentUserId = localStorage.getItem('userId');
    const currentUsername = localStorage.getItem('username');

    if (!input.trim()) {
      alert("Please enter a username or email.");
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:5000/messages/new-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentUserId, currentUsername, target: input })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Failed to create chat");
      } else {
        alert(`✅ New chat started with ${data.other_username}`);
        onClose();
        window.location.reload();
      }
    } catch (err) {
      console.error("Failed to create chat:", err);
      alert("Server error while creating chat");
    }
  };

  return (
    <div className="new-chat-overlay">
      <div className="new-chat-box">
        <h2>Start a New Chat</h2>
        <p>Enter the Username or Email of the new contact:</p>
        <input
          type="text"
          placeholder="Enter Username or Email"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="new-chat-input"
        />
        <div className="new-chat-buttons">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button onClick={handleCreateChat} className="create-button">Create</button>
        </div>
      </div>
    </div>
  );
};

export default NewChat;