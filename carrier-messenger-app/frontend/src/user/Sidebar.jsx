import React, { useState } from 'react';
import './styling/Sidebar.css';
import ProfileMini from './profile_mini';
import ProfileFull from './profile_full';
import DeleteMessagesAlert from './delete_messages_alert';
import DownloadMessages from './download_messages';
import green from '../assets/default_profile_icons/green.png';
import orange from '../assets/default_profile_icons/orange.png';
import silver from '../assets/default_profile_icons/silver.png';

const Sidebar = ({ contacts, onSelectContact, selectedContact }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showProfile, setShowProfile] = useState(false);
  const [dropdownVisible, setDropdownVisible] = useState(null); // Track which dropdown is open
  const [showDeleteAlert, setShowDeleteAlert] = useState(false);
  const [showDownloadPopup, setShowDownloadPopup] = useState(false);

  const [user, setUser] = useState({
    username: 'JohnDoe',
    profilePhoto: null,
  });

  const contactsWithPhotos = contacts.map((contact) => {
    if (contact.name === 'Alice') {
      return { ...contact, profilePhoto: green };
    } else if (contact.name === 'Bob') {
      return { ...contact, profilePhoto: orange };
    } else if (contact.name === 'Charlie') {
      return { ...contact, profilePhoto: silver };
    }
    return contact; // Default case (if needed)
  });

  const filteredContacts = contactsWithPhotos.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDropdownToggle = (index) => {
    setDropdownVisible(dropdownVisible === index ? null : index);
  };

  const handleDeleteChat = () => {
    setShowDeleteAlert(true);
    setDropdownVisible(null); // Close dropdown
  };

  const handleDownloadMessages = () => {
    setShowDownloadPopup(true);
    setDropdownVisible(null); // Close dropdown
  };

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
            className={contact.name === selectedContact?.name ? 'active' : ''}
            onClick={() => onSelectContact(contact)}
          >
            <img src={contact.profilePhoto} alt="Profile" className="contact-photo" />
            {contact.name}
            <button
              className="contact-options-button"
              onClick={(e) => {
                e.stopPropagation(); // Prevent triggering the contact selection
                handleDropdownToggle(index);
              }}
            >
              ⋮
            </button>
            {dropdownVisible === index && (
              <div className="dropdown-menu">
                <button onClick={handleDeleteChat}>Delete Chat</button>
                <button onClick={handleDownloadMessages}>Download Messages</button>
              </div>
            )}
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
      {showDeleteAlert && (
        <DeleteMessagesAlert onClose={() => setShowDeleteAlert(false)} />
      )}
      {showDownloadPopup && (
        <DownloadMessages onClose={() => setShowDownloadPopup(false)} />
      )}
    </div>
  );
};

export default Sidebar;
