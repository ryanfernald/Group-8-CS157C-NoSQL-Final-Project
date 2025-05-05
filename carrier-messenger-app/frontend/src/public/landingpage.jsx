import React, { useState } from "react";
import axios from 'axios';
import "./styling/landingpage.css";
import messagingIcon from "../assets/messaging-icon.gif";
import uiIcon from "../assets/ui-icon.gif";
import profileIcon from "../assets/profile-icon.gif";
import dataIcon from "../assets/data-icon.gif";
import personIcon from "../assets/person-icon.gif";
import carrierPigeonLogo from "../assets/carrierpigeon-logo.svg";

const LandingPage = () => {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const testConnection = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/user/ping", {
        method: 'GET'
      });
      const data = await res.json();
      console.log(data)
    } catch (err) {
      console.error("❌ Ping failed:", err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault(); 
    console.log("🔵 handleLogin triggered");
    console.log("Username:", username);
    console.log("Password:", password);
  
    try {
      const response = await fetch('http://127.0.0.1:5173/user/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // credentials: 'include',  // for cookies and session support
        body: JSON.stringify({
          username: username,
          password: password  // assuming you add password validation later
        })
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }
  
      const data = await response.json();
      console.log("🟢 Login Response:", data);
      alert('Login successful!');
      window.location.href = '/messages';
  
    } catch (error) {
      console.error("🔴 Login Error:", error.message);
      alert('Invalid credentials');
    }
  };

  return (
    <div className="landing-container">
      {/* Left Side - App Information */}
      <div className="info-section">
        <h1>Carrier Messenger</h1>
        <div className="feature">
          <img src={messagingIcon} alt="Messaging Icon" />
          <p>Fast and Secure Messaging</p>
        </div>
        <div className="feature">
          <img src={uiIcon} alt="UI Icon" />
          <p>Great User Interface</p>
        </div>
        <div className="feature">
          <img src={profileIcon} alt="Profile Icon" />
          <p>Customize your User Profile</p>
        </div>
        <div className="feature">
          <img src={dataIcon} alt="Data Icon" />
          <p>Built on the Redis Platform</p>
        </div>
        <div className="feature">
          <img src={personIcon} alt="Person Icon" />
          <p>Sponsored by Mike Wu</p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="login-section">
        <img src={carrierPigeonLogo} alt="Carrier Pigeon Logo" className="logo" />
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input 
            type="text" 
            placeholder="Username" 
            className="input-field" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
          />
          <input 
            type="password" 
            placeholder="Password" 
            className="input-field" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
          />
          <button type="submit" className="login-btn">Login</button>
    
        </form>

        <button onClick={testConnection}>Test Flask Connection</button>
        

        <p className="signup-text">
          Don't have an account yet? <a href="/signup">Sign Up</a>
        </p>
        <button className="signup-btn" onClick={() => window.location.href='/signup'}>Sign Up</button>
      </div>
    </div>
  );
};

export default LandingPage;