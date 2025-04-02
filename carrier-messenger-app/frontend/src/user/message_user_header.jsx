import React from 'react';
import './styling/message_user_header.css';

const MessageUserHeader = ({ contact }) => {
  if (!contact) return null;

  return (
    <div className="message-user-header">
      <img src={contact.profilePhoto} alt="Profile" className="header-photo" />
      <p className="header-username">{contact.name}</p>
    </div>
  );
};

export default MessageUserHeader;