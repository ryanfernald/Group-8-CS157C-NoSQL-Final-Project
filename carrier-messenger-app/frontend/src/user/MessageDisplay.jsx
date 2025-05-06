import React, { useState, useEffect, useRef } from 'react';
import './styling/MessageDisplay.css';
import carrierPigeonLogo from '../assets/carrierpigeon-logo.svg';
import MessageUserHeader from './message_user_header';

const MessageDisplay = ({ onSendMessage, selectedContact }) => {
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null); // Ref to track the end of the messages list

  const [showTimestamps, setShowTimestamps] = useState(true);
  const [selectedMessageIndex, setSelectedMessageIndex] = useState(null);

  const [showUsernames, setShowUsernames] = useState(true);

  const currentUserId = localStorage.getItem('userId');

  const toggleTimestamps = () => {
    setShowTimestamps(!showTimestamps);
    setSelectedMessageIndex(null);
  };

  const currentUsername = localStorage.getItem('username');

  const handleInputChange = (e) => setNewMessage(e.target.value);

  const toggleUsernames = () => {
    setShowUsernames(!showUsernames);
    setSelectedMessageIndex(null);  // collapse on toggle
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() === '' || !selectedContact) return;

    const messagePayload = {
      sender_id: currentUserId,
      sender: currentUsername,
      text: newMessage
    };

    try {
      const res = await fetch(`http://127.0.0.1:5000/messages/${selectedContact.chat_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messagePayload)
      });

      if (!res.ok) throw new Error("Failed to send message");

      const timestamp = new Date().toISOString();
      setMessages(prev => [...prev, { ...messagePayload, timestamp }]);
      setNewMessage('');
    } catch (err) {
      console.error("❌ Failed to send message:", err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSendMessage();
  };

  const parseMessage = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold text
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic text
      .replace(/__(.*?)__/g, '<u>$1</u>'); // Underline text
  };

  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const fetchMessages = async () => {
      console.log("🟡 Chat ID:", selectedContact?.chat_id);
      console.log("🌐 Fetching from:", `http://127.0.0.1:5000/${selectedContact?.chat_id}`);
      if (!selectedContact || !selectedContact.chat_id) return;
      try {
        const res = await fetch(`http://127.0.0.1:5000/messages/${selectedContact.chat_id}`);
        if (!res.ok) throw new Error("Failed to fetch messages");
        const data = await res.json();
        setMessages(data.messages || []);
      } catch (err) {
        console.error("Failed to fetch messages:", err);
        setMessages([]);
      }
    };
    fetchMessages();
  }, [selectedContact]);

  // Scroll to the bottom of the messages list whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end'
      });
    }
  }, [messages]);

  if (!selectedContact) {
    return <div className="message-display">Select a contact to view messages.</div>;
  }

  
  return (
    <div className="message-display">
      <img src={carrierPigeonLogo} alt="Carrier Pigeon Logo" className="logo-overlay" />
      <MessageUserHeader contact={selectedContact} />
      <div className="messages">
      {messages.map((message, index) => (
          <div
          key={index}
          className={`message ${message.sender_id === currentUserId ? 'user-message' : 'incoming-message'}`}
          onClick={() => setSelectedMessageIndex(index)}
        >
          {showUsernames && (
            <p className="message-sender"><strong>{message.sender}</strong></p>
          )}
          
          <div dangerouslySetInnerHTML={{ __html: parseMessage(message.text) }} />
        
          {showTimestamps && (
            <p className="message-timestamp">{new Date(message.timestamp).toLocaleString()}</p>
          )}
        
          {selectedMessageIndex === index && (
            <div className="timestamp-toggle">
              <label>
                <input
                  type="checkbox"
                  checked={!showTimestamps}
                  onChange={toggleTimestamps}
                />
                Hide timestamps
              </label>
              <label style={{ marginLeft: '1em' }}>
                <input
                  type="checkbox"
                  checked={!showUsernames}
                  onChange={toggleUsernames}
                />
                Hide usernames
              </label>
            </div>
          )}
        </div>
        ))}
        {/* Invisible div to ensure scrolling to the bottom */}
        <div ref={messagesEndRef} />
      </div>
      <div className="message-box">
        <input
          type="text"
          placeholder="Type a message..."
          value={newMessage}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default MessageDisplay;