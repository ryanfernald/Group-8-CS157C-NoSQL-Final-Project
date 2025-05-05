import React from 'react';
import './styling/message_user_header.css';
import defaultProfilePhoto from '../assets/default_profile_icons/blue-flying.png';

const MessageUserHeader = ({ contact }) => {
  if (!contact) return null;

  return (
    <div className="message-user-header">
      <img
        src={contact.profilePhoto || defaultProfilePhoto}
        alt="Profile"
        className="header-photo"
      />
      <p className="header-username">{contact.name}</p>
    </div>
  );
};

export default MessageUserHeader;