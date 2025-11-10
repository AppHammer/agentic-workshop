import React, { useState, useEffect } from 'react';
import { getCurrentUser } from '../api';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getCurrentUser();
        setUser(response.data);
      } catch (err) {
        setError('Failed to load profile. Please try again.');
        console.error('Profile fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // Format date helper function
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Capitalize first letter of role
  const formatRole = (role) => {
    if (!role) return 'N/A';
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  // Format hourly rate as currency
  const formatRate = (rate) => {
    if (!rate || rate === 0) return 'Not provided';
    return `$${parseFloat(rate).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-message">Loading profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="profile-container">
        <div className="error-message">No profile data available</div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <h2>My Profile</h2>
      
      <div className="profile-section">
        <h3>Account Information</h3>
        
        <div className="profile-field">
          <label className="field-label">Full Name:</label>
          <span className="field-value">{user.full_name}</span>
        </div>
        
        <div className="profile-field">
          <label className="field-label">Email:</label>
          <span className="field-value">{user.email}</span>
        </div>
        
        <div className="profile-field">
          <label className="field-label">Role:</label>
          <span className="field-value">{formatRole(user.role)}</span>
        </div>
        
        <div className="profile-field">
          <label className="field-label">Phone:</label>
          <span className="field-value">{user.phone || 'Not provided'}</span>
        </div>
        
        <div className="profile-field">
          <label className="field-label">Location:</label>
          <span className="field-value">{user.location || 'Not provided'}</span>
        </div>
        
        <div className="profile-field">
          <label className="field-label">Member Since:</label>
          <span className="field-value">{formatDate(user.created_at)}</span>
        </div>
      </div>
      
      {user.role === 'tasker' && (
        <div className="profile-section">
          <h3>Professional Information</h3>
          
          <div className="profile-field">
            <label className="field-label">Skills:</label>
            <span className="field-value">{user.skills || 'Not provided'}</span>
          </div>
          
          <div className="profile-field">
            <label className="field-label">Hourly Rate:</label>
            <span className="field-value">{formatRate(user.hourly_rate)}</span>
          </div>
          
          <div className="profile-field">
            <label className="field-label">Bio:</label>
            <span className="field-value" style={{ whiteSpace: 'pre-wrap' }}>
              {user.bio || 'Not provided'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;