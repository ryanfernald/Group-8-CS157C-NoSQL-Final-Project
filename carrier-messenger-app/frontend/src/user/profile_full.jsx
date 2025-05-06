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
  const [localUser, setUser] = useState(user);
  const [isEditing, setIsEditing] = useState(false);
  const [username, setUsername] = useState(localUser.username);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); 
  const [profilePhoto, setProfilePhoto] = useState(
    localUser.profilePhoto || defaultIcons[Math.floor(Math.random() * defaultIcons.length)]
  );

  const handleSave = async () => {
    const userId = localStorage.getItem('userId');
    const originalUsername = localUser.username;

    if (username !== originalUsername) {
      await updateUsername(userId, username);
    }

    if (password) {
      if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
      }
      try {
        const res = await fetch('http://127.0.0.1:5000/user/update-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            new_password: password
          })
        });

        const data = await res.json();

        if (!res.ok) {
          alert(data.message || "Failed to update password");
        } else {
          alert("Password updated!");
          setPassword('');
          setConfirmPassword('');
        }
      } catch (err) {
        console.error("Error updating password:", err);
        alert("Server error while updating password.");
      }
    }

    onSave({ username, password, profilePhoto });
    setIsEditing(false);
  };

  const handleLogout = () => {
    // Redirect to the landing page
    window.location.href = '/';
  };

  const updateUsername = async (userId, newUsername) => {
    if (!userId || !newUsername.trim()) {
      alert("Missing username or user ID.");
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:5000/user/update-username', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, new_username: newUsername })
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.message || "Failed to update username");
      } else {
        alert("Username updated!");
        localStorage.setItem("username", newUsername);
        setUser(prev => ({ ...prev, username: newUsername }));
      }
    } catch (err) {
      console.error("Error updating username:", err);
      alert("Server error while updating username.");
    }
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
              placeholder="Confirm New Password"
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
            <p className="profile-full-username">{localUser.username}</p>
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