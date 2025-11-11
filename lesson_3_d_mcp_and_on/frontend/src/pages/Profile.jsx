import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { profileAPI } from '../api';
import '../App.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    skills: '',
    hourly_rate: 0,
  });
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    const startTime = Date.now();
    
    try {
      setLoading(true);
      setError(null);
      const response = await profileAPI.getMyProfile();
      const profileData = response.data;
      setProfile(profileData);
      
      // Initialize form data with profile data
      setFormData({
        email: profileData.email || '',
        skills: profileData.skills || '',
        hourly_rate: profileData.hourly_rate || 0,
      });
    } catch (err) {
      console.error('Error fetching profile:', err);
      console.error('Error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message
      });
      
      // Handle authentication errors
      if (err.response?.status === 401) {
        console.log('Authentication failed, logging out...');
        logout();
        navigate('/login', {
          state: { message: 'Your session has expired. Please login again.' }
        });
        return;
      }
      
      // Handle different error types with user-friendly messages
      let errorMessage = 'Unable to load profile. Please try again.';
      
      if (!err.response) {
        // Network error (no response from server)
        errorMessage = 'Unable to connect to server. Please check your internet connection and try again.';
      } else if (err.response.status >= 500) {
        // Server error
        errorMessage = 'Server error occurred. Please try again later.';
      } else if (err.response?.data?.detail) {
        // Use server-provided error message if available
        errorMessage = err.response.data.detail;
      }
      
      setError(errorMessage);
    } finally {
      // Ensure minimum loading time to prevent flash
      const elapsedTime = Date.now() - startTime;
      const minimumLoadTime = 300; // milliseconds
      
      if (elapsedTime < minimumLoadTime) {
        setTimeout(() => setLoading(false), minimumLoadTime - elapsedTime);
      } else {
        setLoading(false);
      }
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

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return 'Not specified';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const renderSkills = (skills) => {
    if (!skills || skills.trim() === '') return 'Not specified';
    
    // Handle comma-separated skills with better formatting
    const skillList = skills.split(',').map(s => s.trim()).filter(Boolean);
    
    if (skillList.length === 0) return 'Not specified';
    
    return skillList.join(', ');
  };

  /**
   * Enable edit mode by setting isEditing to true
   */
  const handleEdit = () => {
    setIsEditing(true);
  };

  /**
   * Cancel edit mode and reset form data to profile values
   */
  const handleCancel = () => {
    setFormData({
      email: profile.email || '',
      skills: profile.skills || '',
      hourly_rate: profile.hourly_rate || 0,
    });
    setIsEditing(false);
    setError(null);
  };

  /**
   * Save profile changes by sending only modified fields to the server
   */
  const handleSave = async () => {
    try {
      setError(null);
      
      const updates = {};
      if (formData.email !== profile.email) updates.email = formData.email;
      if (formData.skills !== profile.skills) updates.skills = formData.skills;
      if (formData.hourly_rate !== profile.hourly_rate) updates.hourly_rate = formData.hourly_rate;
      
      const response = await profileAPI.updateMyProfile(updates);
      setProfile(response.data);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update profile:', err);
      let errorMessage = 'Failed to save changes. Please try again.';
      if (err.response?.status === 400 && err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (!err.response) {
        errorMessage = 'Unable to connect to server. Please check your internet connection.';
      }
      setError(errorMessage);
    }
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
        <div className="error-container">
          <div className="error-icon">⚠️</div>
          <h2 className="error-title">Unable to Load Profile</h2>
          <p className="error-message">{error}</p>
          <div className="error-buttons">
            <button onClick={fetchProfile} className="retry-button">
              Try Again
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="secondary-button"
            >
              Back to Dashboard
            </button>
          </div>
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
            {isEditing ? (
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="profile-input"
              />
            ) : (
              <span className="profile-value">{profile.email}</span>
            )}
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
              {isEditing ? (
                <input
                  type="text"
                  value={formData.skills}
                  onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                  className="profile-input"
                  placeholder="e.g., Plumbing, Carpentry, Electrical"
                />
              ) : (
                <span className="profile-value">
                  {renderSkills(profile.skills)}
                </span>
              )}
            </div>

            <div className="profile-field">
              <label className="profile-label">Hourly Rate:</label>
              {isEditing ? (
                <input
                  type="number"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) || 0 })}
                  className="profile-input"
                  min="0"
                  step="0.01"
                />
              ) : (
                <span className="profile-value">
                  {formatCurrency(profile.hourly_rate)}
                </span>
              )}
            </div>
          </div>
        )}

        <div className="profile-actions">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="save-button">Save</button>
              <button onClick={handleCancel} className="cancel-button">Cancel</button>
            </>
          ) : (
            <button onClick={handleEdit} className="edit-button">Edit</button>
          )}
        </div>
      </div>
    </div>
  );
}