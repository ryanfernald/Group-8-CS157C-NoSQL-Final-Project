import React, { useState } from 'react';
import Sidebar from './Sidebar';
import MessageDisplay from './MessageDisplay';
import './App.css';
import './Sidebar.css';
import './MessageDisplay.css';

function App() {
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
      { text: `Hello ${contact.name}!`, isUser: false },
      { text: 'How are you this fine evening?', isUser: false },
      { text: 'I\'m doing well, thank you!', isUser: true },
      { text: 'I\'m also doing well. How about you?', isUser: false },
      { text: 'I\'m doing great too. Goodnight!', isUser: true },
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

export default App;
