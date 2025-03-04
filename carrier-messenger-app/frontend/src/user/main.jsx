import React, { useState } from 'react';
import Sidebar from './Sidebar';
import MessageDisplay from './MessageDisplay';
import './styling/main.css'
import './styling/Sidebar.css';
import './styling/MessageDisplay.css';

function Main() {
  const [contacts] = useState([
    { name: 'Alice' },
    { name: 'Bob' },
    { name: 'Charlie' },
  ]);
  const [messages, setMessages] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);

  const handleSelectContact = (contact) => {
    setSelectedContact(contact);
    // Fetch messages for the selected contact
    setMessages([
      { text: `Hello, this is  ${contact.name}!`, isUser: false },
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
      <Sidebar contacts={contacts} onSelectContact={handleSelectContact} />
      <MessageDisplay messages={messages} onSendMessage={handleSendMessage} />
    </div>
  );
}

export default Main;
