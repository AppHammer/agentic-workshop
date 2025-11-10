import { useState, useEffect } from 'react';
import { profileAPI } from '../api';
import '../App.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await profileAPI.getMyProfile();
      setProfile(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError(err.response?.data?.detail || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading-message">Loading profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchProfile} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container">
        <div className="error-message">No profile data available</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="profile-container">
        <h1>My Profile</h1>
        
        <div className="profile-section">
          <div className="profile-field">
            <label className="profile-label">Username:</label>
            <span className="profile-value">{profile.username}</span>
          </div>

          <div className="profile-field">
            <label className="profile-label">Email:</label>
            <span className="profile-value">{profile.email}</span>
          </div>

          <div className="profile-field">
            <label className="profile-label">Account Type:</label>
            <span className="profile-value">
              {profile.user_type.charAt(0).toUpperCase() + profile.user_type.slice(1)}
            </span>
          </div>

          <div className="profile-field">
            <label className="profile-label">Member Since:</label>
            <span className="profile-value">{formatDate(profile.created_at)}</span>
          </div>
        </div>

        {profile.user_type === 'tasker' && (
          <div className="tasker-info-section">
            <h2>Tasker Information</h2>
            
            <div className="profile-field">
              <label className="profile-label">Skills:</label>
              <span className="profile-value">
                {profile.skills || 'Not specified'}
              </span>
            </div>

            <div className="profile-field">
              <label className="profile-label">Hourly Rate:</label>
              <span className="profile-value">
                {profile.hourly_rate 
                  ? `$${parseFloat(profile.hourly_rate).toFixed(2)}`
                  : 'Not specified'
                }
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}