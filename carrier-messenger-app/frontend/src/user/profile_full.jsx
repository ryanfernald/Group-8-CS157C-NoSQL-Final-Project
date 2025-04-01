import React, { useState } from 'react';
import './styling/profile_full.css';

// Import all default profile icons
import blueFlying from '../assets/default_profile_icons/blue-flying.png';
import blueStanding from '../assets/default_profile_icons/blue-standing.png';
import green from '../assets/default_profile_icons/green.png';
import orange from '../assets/default_profile_icons/orange.png';
import pink from '../assets/default_profile_icons/pink.png';
import silver from '../assets/default_profile_icons/silver.png';

const defaultIcons = [blueFlying, blueStanding, green, orange, pink, silver];

const ProfileFull = ({ user, onClose, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [username, setUsername] = useState(user.username);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [profilePhoto, setProfilePhoto] = useState(
    user.profilePhoto || defaultIcons[Math.floor(Math.random() * defaultIcons.length)]
  );

  const handleSave = () => {
    if (password !== confirmPassword) {
      alert('Passwords do not match!');
      return;
    }
    onSave({ username, password, profilePhoto });
    setIsEditing(false);
  };

  const handleLogout = () => {
    // Redirect to the landing page
    window.location.href = '/';
  };

  return (
    <div className="profile-full-overlay">
      <div className="profile-full">
        <button className="close-btn" onClick={onClose}>X</button>
        <img
          src={profilePhoto}
          alt="Profile"
          className="profile-full-photo"
        />
        {isEditing ? (
          <>
            <div className="profile-photo-selector">
              <h3>Select a Profile Photo</h3>
              <div className="default-photo-list">
                {defaultIcons.map((icon, index) => (
                  <img
                    key={index}
                    src={icon}
                    alt={`Default Icon ${index}`}
                    className={`default-photo ${profilePhoto === icon ? 'selected' : ''}`}
                    onClick={() => setProfilePhoto(icon)}
                  />
                ))}
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setProfilePhoto(URL.createObjectURL(e.target.files[0]))}
                className="upload-photo-input"
              />
            </div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="profile-full-input"
            />
            <input
              type="password"
              placeholder="New Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="profile-full-input"
            />
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="profile-full-input"
            />
            <div className="profile-full-buttons">
              <button onClick={handleSave} className="save-btn">Save</button>
              <button onClick={() => setIsEditing(false)} className="cancel-btn">Cancel</button>
            </div>
          </>
        ) : (
          <>
            <p className="profile-full-username">{username}</p>
            <div className="profile-full-buttons">
              <button onClick={() => setIsEditing(true)} className="edit-btn">Edit</button>
              <button onClick={handleLogout} className="logout-btn">Log Out</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProfileFull;