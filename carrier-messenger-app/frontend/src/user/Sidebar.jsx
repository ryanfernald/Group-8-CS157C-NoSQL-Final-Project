import React, { useState } from 'react';
import './styling/Sidebar.css';
import ProfileMini from './profile_mini';
import ProfileFull from './profile_full';

const Sidebar = ({ contacts, onSelectContact, selectedContact }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showProfile, setShowProfile] = useState(false);

  // User object with default profile photo
  const [user, setUser] = useState({
    username: 'JohnDoe',
    profilePhoto: null, // Will be set to a default photo in ProfileFull
  });

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSaveProfile = (updatedUser) => {
    setUser(updatedUser); // Update the user object with the new data
    setShowProfile(false); // Close the profile editor
  };

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
      <ProfileMini user={user} onClick={() => setShowProfile(true)} />
      {showProfile && (
        <ProfileFull
          user={user}
          onClose={() => setShowProfile(false)}
          onSave={handleSaveProfile}
        />
      )}
    </div>
  );
};

export default Sidebar;
