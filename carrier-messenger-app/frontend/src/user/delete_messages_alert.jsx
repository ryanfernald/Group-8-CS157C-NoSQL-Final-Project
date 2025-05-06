import React from 'react';
import './styling/delete_messages_alert.css';

const DeleteMessagesAlert = ({ onClose, selectedChat, userId }) => {

  const handleDelete = async () => {
    const chatId = selectedChat?.chat_id;

    console.log("🟡 Attempting to delete chat");
    console.log("User ID:", userId);
    console.log("Chat ID:", chatId);

    if (!userId || !chatId) {
      alert('Missing user or chat info');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/messages/delete-participant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, chat_id: chatId })
      });
      const data = await response.json();
      console.log("🔵 Server response:", data);
      if (!response.ok) {
        alert(data.message || 'Failed to delete chat');
      } else {
        alert('Chat deleted!');
        onClose();
        window.location.reload();
      }
    } catch (err) {
      console.error("🔴 Delete chat error:", err);
      alert("Error deleting chat");
    }
  };

  return (
    <div className="delete-alert-overlay">
      <div className="delete-alert-box">
        <h2>Are you sure you want to delete this Chat?</h2>
        <h3>This action cannot be undone.</h3>
        <p>All other members of this chat will still be able to read messages.</p>
        <div className="delete-alert-buttons">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button onClick={handleDelete} className="confirm-button">Yes</button>
        </div>
      </div>
    </div>
  );
};

export default DeleteMessagesAlert;