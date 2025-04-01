import React from 'react';
import './styling/profile_mini.css';
import defaultProfilePhoto from '../assets/carrierpigeon-logo.svg';

const ProfileMini = ({ user, onClick }) => {
  return (
    <div className="profile-mini" onClick={onClick}>
      <img
        src={user.profilePhoto || defaultProfilePhoto}
        alt="Profile"
        className="profile-mini-photo"
      />
      <p className="profile-mini-username">{user.username}</p>
    </div>
  );
};

export default ProfileMini;