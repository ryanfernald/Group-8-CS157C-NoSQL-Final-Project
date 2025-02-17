import React from 'react';
import './Sidebar.css';

const Sidebar = ({ contacts, onSelectContact }) => {
  return (
    <div className="sidebar">
      <h2>Contacts</h2>
      <ul>
        {contacts.map((contact, index) => (
          <li key={index} onClick={() => onSelectContact(contact)}>
            {contact.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;