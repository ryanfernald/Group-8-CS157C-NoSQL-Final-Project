import React, { useState } from 'react';
import Sidebar from './Sidebar';
import MessageDisplay from './MessageDisplay';
import './styling/main.css';
import './styling/Sidebar.css';
import './styling/MessageDisplay.css';

// Import profile icons
import green from '../assets/default_profile_icons/green.png';
import orange from '../assets/default_profile_icons/orange.png';
import silver from '../assets/default_profile_icons/silver.png';

function Main() {
  // Temporary contacts with fixed profile pictures
  const [contacts] = useState([
    { name: 'Alice', profilePhoto: green },
    { name: 'Bob', profilePhoto: orange },
    { name: 'Charlie', profilePhoto: silver },
  ]);

  const [messages, setMessages] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);

  const handleSelectContact = (contact) => {
    setSelectedContact(contact);
    // Fetch messages for the selected contact (placeholder logic)
    setMessages([
      { text: `Hello, this is ${contact.name}!`, isUser: false },
      { text: 'How are you this fine evening?', isUser: false },
      { text: 'I\'m doing well, thank you!', isUser: true },
      { text: 'I\'m also doing well. How about you?', isUser: false },
      { text: 'I\'m doing great too. Goodnight!', isUser: true },
      { text: 'This is a long test test test test test test test to see if the message will wrap around. Yes, yes it does, that\'s very nice.', isUser: false },
    ]);
  };

  const handleSendMessage = (text) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { text, isUser: true },
    ]);
  };

  return (
    <div className="app">
      <Sidebar
        contacts={contacts}
        onSelectContact={handleSelectContact}
        selectedContact={selectedContact}
      />
      <MessageDisplay
        messages={messages}
        onSendMessage={handleSendMessage}
        selectedContact={selectedContact}
      />
    </div>
  );
}

export default Main;
