import React, { useState, useEffect } from 'react';
import './styling/Sidebar.css';
import ProfileMini from './profile_mini';
import ProfileFull from './profile_full';
import DeleteMessagesAlert from './delete_messages_alert';
import DownloadMessages from './download_messages';
import NewChat from './new_chat';
import defaultProfilePhoto from '../assets/default_profile_icons/blue-flying.png';  

const Sidebar = ({ onSelectContact, selectedContact }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showProfile, setShowProfile] = useState(false);
  const [showNewChatPopup, setShowNewChatPopup] = useState(false); // Track New Chat popup visibility
  const [dropdownVisible, setDropdownVisible] = useState(null); // Track which dropdown is open
  const [showDeleteAlert, setShowDeleteAlert] = useState(false);
  const [showDownloadPopup, setShowDownloadPopup] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);
  const [activeDropdownChatId, setActiveDropdownChatId] = useState(null);

  const [user, setUser] = useState({
    username: 'JohnDoe',
    profilePhoto: null,
  });

  useEffect(() => {
    console.log("📦 Stored userId:", localStorage.getItem('userId'));
    console.log("📦 Stored username:", localStorage.getItem('username'));
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      const userId = localStorage.getItem('userId');
      if (!userId) return;

      try {
        const response = await fetch(`http://127.0.0.1:5000/user/profile/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch user');
        const data = await response.json();
        setUser({
          username: data.username,
          profilePhoto: data.profilePhoto || null
        });
      } catch (err) {
        console.error("Failed to load user profile:", err);
      }
    };

    fetchUser();
  }, []);

  // const contactsWithPhotos = contacts.map((contact) => {
  //   if (contact.name === 'Alice') {
  //     return { ...contact, profilePhoto: green };
  //   } else if (contact.name === 'Bob') {
  //     return { ...contact, profilePhoto: orange };
  //   } else if (contact.name === 'Charlie') {
  //     return { ...contact, profilePhoto: silver };
  //   }
  //   return contact; // Default case (if needed)
  // });

  const [contacts, setContacts] = useState([]);
  
  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const loadContacts = async () => {
      const userId = localStorage.getItem('userId');
      if (!userId) return;
  
      try {
        const response = await fetch(`http://127.0.0.1:5000/user/contacts/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch contacts');
        const data = await response.json();
  
        const processedContacts = (data.contacts || []).map(chat => {
          const participants = chat.participants || [];
          const otherParticipants = participants.filter(p => p.id !== userId);
        
          return {
            chat_id: chat.chat_id,
            name: otherParticipants.map(p => p.username).join(', '),
            profilePhoto: otherParticipants[0]?.profilePhoto || null
          };
        });
  
        setContacts(processedContacts);
      } catch (err) {
        console.error("Failed to load contacts:", err);
      }
    };
  
    loadContacts();
  }, []);

  const handleDropdownToggle = (chatId) => {
    setActiveDropdownChatId(activeDropdownChatId === chatId ? null : chatId);
  };

  const handleDeleteChat = (chat) => {
    setChatToDelete(chat);
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

  const handleNewChat = () => {
    setShowNewChatPopup(true);
  };

  return (
    <div className="sidebar">
      <button className="new-chat-button" onClick={handleNewChat}>
        New Chat
      </button>
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
            <img src={contact.profilePhoto || defaultProfilePhoto} alt="Profile" className="contact-photo" />
            {contact.name}
            <button
              className="contact-options-button"
              onClick={(e) => {
                e.stopPropagation();
                handleDropdownToggle(contact.chat_id);
              }}
            >
              ⋮
            </button>
            {activeDropdownChatId === contact.chat_id && (
              <div className="dropdown-menu">
                <button onClick={() => handleDeleteChat(contact)}>Delete Chat</button>
                {/* <button onClick={handleDownloadMessages}>Download Messages</button> */}
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
      {showDeleteAlert && chatToDelete && (
        <DeleteMessagesAlert
          onClose={() => setShowDeleteAlert(false)}
          selectedChat={chatToDelete}
          userId={localStorage.getItem('userId')}
        />
      )}
      {showDownloadPopup && (
        <DownloadMessages onClose={() => setShowDownloadPopup(false)} />
      )}
      {showNewChatPopup && (
        <NewChat onClose={() => setShowNewChatPopup(false)} />
      )}
    </div>
  );
};

export default Sidebar;
