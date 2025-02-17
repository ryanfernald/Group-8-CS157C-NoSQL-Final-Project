import React, { useState } from 'react';
import './Sidebar.css';

const Sidebar = ({ contacts, onSelectContact, selectedContact }) => {
  const [searchQuery, setSearchQuery] = useState('');

  // Filter contacts based on search query
  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="sidebar">
      <h2>Contacts</h2>
      <input
        type="text"
        placeholder="Search contacts..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="search-bar"
      />
      <ul>
        {filteredContacts.map((contact, index) => (
          <li
            key={index}
            className={contact.id === selectedContact?.id ? 'active' : ''}
            onClick={() => onSelectContact(contact)}
          >
            {contact.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
