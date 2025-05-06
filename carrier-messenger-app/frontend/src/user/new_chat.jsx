import React, { useState } from 'react';
import './styling/new_chat.css';

const NewChat = ({ onClose }) => {
  const [inputs, setInputs] = useState(['']);

  const handleInputChange = (index, value) => {
    const newInputs = [...inputs];
    newInputs[index] = value;
    setInputs(newInputs);
  };

  const handleAddField = () => {
    setInputs([...inputs, '']);
  };

  const handleCreateChat = async () => {
    const currentUserId = localStorage.getItem('userId');
    const currentUsername = localStorage.getItem('username');

    const validInputs = inputs.map(input => input.trim()).filter(Boolean);

    if (validInputs.length === 0) {
      alert("Please enter at least one username or email.");
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:5000/messages/new-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          currentUserId,
          currentUsername,
          targets: validInputs  // Notice this is now an array
        })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Failed to create chat");
      } else {
        alert(`✅ New chat started with: ${data.created_with.join(', ')}`);
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
        <p>Enter Username(s) or Email(s):</p>
        {inputs.map((input, index) => (
          <input
            key={index}
            type="text"
            placeholder={`User ${index + 1}`}
            value={input}
            onChange={(e) => handleInputChange(index, e.target.value)}
            className="new-chat-input"
          />
        ))}
        <button onClick={handleAddField} className="add-user-button">+</button>
        <div className="new-chat-buttons">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button onClick={handleCreateChat} className="create-button">Create</button>
        </div>
      </div>
    </div>
  );
};

export default NewChat;