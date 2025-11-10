import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTask, getMyTasks, getTaskBids, acceptBid, completeAgreement, createReview } from '../api';

function CustomerDashboard({ user }) {
  const [tasks, setTasks] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    date: '',
    budget: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const getStatusColor = (status) => {
    switch(status) {
      case 'open':
        return '#ffffff'; // white
      case 'in_progress':
        return '#90EE90'; // light green
      case 'completed':
        return '#C0C0C0'; // silver
      default:
        return '#ffffff';
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await getMyTasks();
      setTasks(response.data);
    } catch (err) {
      setError('Failed to load tasks');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await createTask({
        ...formData,
        budget: parseFloat(formData.budget),
        date: new Date(formData.date).toISOString()
      });
      setSuccess('Task created successfully!');
      setFormData({
        title: '',
        description: '',
        location: '',
        date: '',
        budget: ''
      });
      setShowCreateForm(false);
      loadTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create task');
    }
  };

  return (
    <div className="container">
      <h2>Customer Dashboard</h2>
      <p>Welcome, {user.full_name}!</p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <button 
        onClick={() => setShowCreateForm(!showCreateForm)} 
        className="btn-primary"
        style={{ marginBottom: '20px' }}
      >
        {showCreateForm ? 'Cancel' : 'Post New Task'}
      </button>

      {showCreateForm && (
        <div className="card">
          <h3>Create New Task</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="4"
                required
              />
            </div>
            <div className="form-group">
              <label>Location *</label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Date & Time *</label>
              <input
                type="datetime-local"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Budget ($) *</label>
              <input
                type="number"
                name="budget"
                value={formData.budget}
                onChange={handleChange}
                min="0"
                step="0.01"
                required
              />
            </div>
            <button type="submit" className="btn-success">
              Create Task
            </button>
          </form>
        </div>
      )}

      <h3 style={{ marginTop: '30px' }}>My Tasks</h3>
      <div className="grid">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="task-card"
            style={{ backgroundColor: getStatusColor(task.status) }}
          >
            <h3>{task.title}</h3>
            <p className="budget">${task.budget}</p>
            <p className="location">📍 {task.location}</p>
            <p className="date">📅 {new Date(task.date).toLocaleString()}</p>
            <p><strong>Status:</strong> {task.status}</p>
            <p>{task.description.substring(0, 100)}...</p>
            <button
              onClick={() => navigate(`/tasks/${task.id}`)}
              className="btn-primary"
              style={{ marginTop: '10px' }}
            >
              View Details
            </button>
          </div>
        ))}
      </div>
      {tasks.length === 0 && <p>No tasks yet. Create your first task!</p>}
    </div>
  );
}

export default CustomerDashboard;