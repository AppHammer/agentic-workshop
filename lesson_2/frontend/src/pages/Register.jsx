import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    user_type: 'customer',
    skills: '',
    hourly_rate: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      const data = { ...formData };
      if (formData.user_type === 'customer') {
        delete data.skills;
        delete data.hourly_rate;
      } else {
        data.hourly_rate = parseFloat(data.hourly_rate);
      }
      
      await register(data);
      setSuccess('Registration successful! Please login.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="auth-container">
      <h2>Register for Tasker</h2>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>User Type</label>
          <select
            value={formData.user_type}
            onChange={(e) => setFormData({ ...formData, user_type: e.target.value })}
          >
            <option value="customer">Customer</option>
            <option value="tasker">Tasker</option>
          </select>
        </div>
        {formData.user_type === 'tasker' && (
          <>
            <div className="form-group">
              <label>Skills</label>
              <textarea
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="e.g., Plumbing, Electrical, Moving, Cleaning"
              />
            </div>
            <div className="form-group">
              <label>Hourly Rate ($)</label>
              <input
                type="number"
                step="0.01"
                value={formData.hourly_rate}
                onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                placeholder="25.00"
              />
            </div>
          </>
        )}
        <button type="submit" className="btn">Register</button>
      </form>
      <p style={{ marginTop: '15px', textAlign: 'center' }}>
        Already have an account? <Link to="/login" className="link">Login</Link>
      </p>
    </div>
  );
}

export default Register;