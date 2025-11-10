import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getTasks } from '../api';

function TaskList({ user }) {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('open');
  const [error, setError] = useState('');
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
  }, [filter]);

  const loadTasks = async () => {
    try {
      const response = await getTasks(filter);
      setTasks(response.data);
    } catch (err) {
      setError('Failed to load tasks');
    }
  };

  return (
    <div className="container">
      <h2>Browse Tasks</h2>
      
      {error && <div className="error">{error}</div>}

      <div style={{ marginBottom: '20px' }}>
        <label>Filter by status: </label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

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
      {tasks.length === 0 && <p>No tasks found.</p>}
    </div>
  );
}

export default TaskList;