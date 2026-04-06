import React, { useState, useEffect } from 'react';
import './InvitationPending.css';

function InvitationPending({ invitation, onSent }) {
  const [status, setStatus] = useState('preview'); // preview, sending, sent
  const [progress, setProgress] = useState(0);

  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const handleSend = () => {
    setStatus('sending');
    
    // Simulate sending progress
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress += Math.random() * 40;
      if (currentProgress >= 100) {
        currentProgress = 100;
        clearInterval(interval);
        
        setTimeout(() => {
          setStatus('sent');
          setProgress(100);
          
          // Auto dismiss after 2 seconds
          setTimeout(() => {
            onSent();
          }, 2000);
        }, 300);
      }
      setProgress(Math.min(currentProgress, 100));
    }, 200);
  };

  return (
    <div className="invitation-pending-container">
      {status === 'preview' && (
        <div className="invitation-card preview">
          <div className="gradient-accent"></div>
          
          <div className="card-header">
            <div className="avatar">{invitation.recipient.name.split(' ').map(n => n[0]).join('')}</div>
            <div className="header-info">
              <h3>{invitation.recipient.name}</h3>
              <p>{invitation.recipient.email}</p>
            </div>
          </div>

          <div className="card-details">
            <div className="detail">
              <span className="label">Event</span>
              <span className="value">{invitation.title}</span>
            </div>
            <div className="detail">
              <span className="label">Time</span>
              <span className="value">{formatTime(invitation.startTime)}</span>
            </div>
            <div className="detail">
              <span className="label">Duration</span>
              <span className="value">{invitation.duration} min</span>
            </div>
          </div>

          <div className="card-actions">
            <button className="btn btn-cancel" onClick={() => window.history.back()}>
              Cancel
            </button>
            <button className="btn btn-send" onClick={handleSend}>
              Send via Google Calendar
            </button>
          </div>

          <p className="card-note">This will send a Google Calendar invitation to the recipient.</p>
        </div>
      )}

      {status === 'sending' && (
        <div className="invitation-card sending">
          <div className="gradient-accent blue"></div>
          
          <div className="sending-content">
            <div className="sending-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path>
                <circle cx="12" cy="12" r="8" opacity="0.2"></circle>
              </svg>
            </div>
            <p className="sending-text">Sending invitation...</p>
            
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {status === 'sent' && (
        <div className="invitation-card sent">
          <div className="gradient-accent green"></div>
          
          <div className="sent-content">
            <div className="sent-icon">✓</div>
            <h4>Invitation Sent</h4>
            <p className="sent-message">
              {invitation.recipient.name} will receive the Google Calendar invitation shortly.
            </p>
            <p className="sent-note">Waiting for response...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default InvitationPending;
