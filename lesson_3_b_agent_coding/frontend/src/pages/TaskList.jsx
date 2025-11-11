import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { taskAPI } from '../api';

function TaskList() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await taskAPI.list();
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div>
      <h1>{user.user_type === 'customer' ? 'My Tasks' : 'Available Tasks'}</h1>
      
      {tasks.length === 0 ? (
        <div className="card">
          <p>No tasks available at the moment.</p>
        </div>
      ) : (
        <div className="task-grid">
          {tasks.map(task => (
            <div 
              key={task.id} 
              className="task-card"
              onClick={() => navigate(`/tasks/${task.id}`)}
            >
              <h3>{task.title}</h3>
              <p><strong>Budget:</strong> ${task.budget}</p>
              <p><strong>Location:</strong> {task.location}</p>
              <p><strong>Date:</strong> {new Date(task.date).toLocaleDateString()}</p>
              <p className="task-description">{task.description.substring(0, 100)}...</p>
              <span className={`task-status status-${task.status}`}>
                {task.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TaskList;