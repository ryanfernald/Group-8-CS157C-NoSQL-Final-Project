import React from 'react';
import './styling/delete_messages_alert.css';

const DeleteMessagesAlert = ({ onClose }) => {
  const handleConfirm = () => {
    alert('Chat deleted!');
    onClose();
  };

  return (
    <div className="delete-alert-overlay">
      <div className="delete-alert-box">
        <h2>Are you sure you want to delete this Chat?</h2>
        <div className="delete-alert-buttons">
          <button onClick={handleConfirm} className="confirm-button">Yes</button>
          <button onClick={onClose} className="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default DeleteMessagesAlert;