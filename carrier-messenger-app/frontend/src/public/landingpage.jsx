import React from "react";
import "./styling/landingpage.css";
import messagingIcon from "../assets/messaging-icon.gif";
import uiIcon from "../assets/ui-icon.gif";
import profileIcon from "../assets/profile-icon.gif";
import dataIcon from "../assets/data-icon.gif";
import personIcon from "../assets/person-icon.gif";

const LandingPage = () => {
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
          <p>Customize your user profile</p>
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
        <h2>Login</h2>
        <input type="text" placeholder="Username" className="input-field" />
        <input type="password" placeholder="Password" className="input-field" />
        <button className="login-btn">Login</button>
        
        {/* Placeholder for login functionality */}
        {/* TODO: Implement login API connection here */}
        
        <p className="signup-text">Don't have an account yet? <a href="/signup">Sign Up</a></p>
        <button className="signup-btn" onClick={() => window.location.href='/signup'}>Sign Up</button>
      </div>
    </div>
  );
};

export default LandingPage;
