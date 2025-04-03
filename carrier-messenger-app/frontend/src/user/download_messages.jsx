import React from 'react';
import './styling/download_messages.css';

const DownloadMessages = ({ onClose }) => {
  return (
    <div className="download-overlay">
      <div className="download-box">
        <h2>Download Messages</h2>
        <div className="date-selectors">
          <div>
            <label htmlFor="start-date">Start Date:</label>
            <input type="date" id="start-date" />
          </div>
        </div>

        <div>
          <div>
            <label htmlFor="end-date">End Date:</label>
            <input type="date" id="end-date" />
          </div>
          <div className="checkbox-container">
            <input type="checkbox" id="current" />
            <label htmlFor="current">Current</label>
          </div>
        </div>

        <div className="download-buttons">
          <button onClick={onClose} className="cancel-button">Cancel</button>
          <button className="download-button">Download</button>
        </div>

      </div>

    </div>
  );
};

export default DownloadMessages;