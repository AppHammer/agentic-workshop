import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { authAPI } from '../api';

function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await authAPI.getCurrentUser();
      setProfile(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load profile');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading profile...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!profile) {
    return <div className="error">Profile not found</div>;
  }

  return (
    <div className="profile-container">
      <h2>My Profile</h2>
      
      <div className="profile-section">
        <h3>Account Information</h3>
        <div className="profile-field">
          <label>Username:</label>
          <span>{profile.username}</span>
        </div>
        <div className="profile-field">
          <label>Email:</label>
          <span>{profile.email}</span>
        </div>
        <div className="profile-field">
          <label>Account Type:</label>
          <span className="user-type-badge">{profile.user_type}</span>
        </div>
        <div className="profile-field">
          <label>Member Since:</label>
          <span>{new Date(profile.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {profile.user_type === 'tasker' && (
        <div className="profile-section">
          <h3>Tasker Information</h3>
          <div className="profile-field">
            <label>Skills:</label>
            <span>{profile.skills || 'Not specified'}</span>
          </div>
          <div className="profile-field">
            <label>Hourly Rate:</label>
            <span>{profile.hourly_rate ? `$${profile.hourly_rate}/hour` : 'Not specified'}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;