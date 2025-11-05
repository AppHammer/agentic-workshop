import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getTasks, getMyTasks, createBid } from '../api';

function TaskerDashboard({ user }) {
  const [availableTasks, setAvailableTasks] = useState([]);
  const [myTasks, setMyTasks] = useState([]);
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
      const [available, mine] = await Promise.all([
        getTasks('open'),
        getMyTasks()
      ]);
      setAvailableTasks(available.data);
      setMyTasks(mine.data);
    } catch (err) {
      setError('Failed to load tasks');
    }
  };

  return (
    <div className="container">
      <h2>Tasker Dashboard</h2>
      <p>Welcome, {user.full_name}!</p>
      
      {user.skills && (
        <div className="card">
          <h3>Your Profile</h3>
          <p><strong>Skills:</strong> {user.skills}</p>
          {user.hourly_rate && <p><strong>Hourly Rate:</strong> ${user.hourly_rate}</p>}
          {user.bio && <p><strong>Bio:</strong> {user.bio}</p>}
        </div>
      )}

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <h3 style={{ marginTop: '30px' }}>My Active Tasks</h3>
      <div className="grid">
        {myTasks.map((task) => (
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
      {myTasks.length === 0 && <p>No active tasks yet. Browse available tasks to bid!</p>}

      <h3 style={{ marginTop: '30px' }}>Available Tasks</h3>
      <div className="grid">
        {availableTasks.map((task) => (
          <div
            key={task.id}
            className="task-card"
            style={{ backgroundColor: getStatusColor(task.status) }}
          >
            <h3>{task.title}</h3>
            <p className="budget">${task.budget}</p>
            <p className="location">📍 {task.location}</p>
            <p className="date">📅 {new Date(task.date).toLocaleString()}</p>
            <p>{task.description.substring(0, 100)}...</p>
            <button
              onClick={() => navigate(`/tasks/${task.id}`)}
              className="btn-primary"
              style={{ marginTop: '10px' }}
            >
              View & Bid
            </button>
          </div>
        ))}
      </div>
      {availableTasks.length === 0 && <p>No available tasks at the moment.</p>}
    </div>
  );
}

export default TaskerDashboard;