import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { taskAPI, bidAPI } from '../api';

function TaskDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [bidAmount, setBidAmount] = useState('');
  const [bidMessage, setBidMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTask();
  }, [id]);

  const fetchTask = async () => {
    try {
      const response = await taskAPI.get(id);
      setTask(response.data);
    } catch (error) {
      console.error('Error fetching task:', error);
      setError('Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const handleBidSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await bidAPI.create({
        task_id: parseInt(id),
        amount: parseFloat(bidAmount),
        message: bidMessage
      });
      setSuccess('Bid submitted successfully!');
      setBidAmount('');
      setBidMessage('');
      fetchTask();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit bid');
    }
  };

  const handleAcceptBid = async (bidId) => {
    try {
      await bidAPI.accept(bidId);
      setSuccess('Bid accepted! Agreement created.');
      fetchTask();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept bid');
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await taskAPI.updateStatus(id, newStatus);
      setSuccess('Task status updated!');
      fetchTask();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update status');
    }
  };

  if (loading) {
    return <div className="loading">Loading task details...</div>;
  }

  if (!task) {
    return <div className="error">Task not found</div>;
  }

  return (
    <div>
      <button onClick={() => navigate('/tasks')} className="btn btn-secondary btn-small" style={{marginBottom: '20px'}}>
        ← Back to Tasks
      </button>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <h2>{task.title}</h2>
        <p><strong>Description:</strong> {task.description}</p>
        <p><strong>Budget:</strong> ${task.budget}</p>
        <p><strong>Location:</strong> {task.location}</p>
        <p><strong>Date:</strong> {new Date(task.date).toLocaleString()}</p>
        <p>
          <strong>Status:</strong>
          <span className={`task-status status-${task.status}`} style={{marginLeft: '10px'}}>
            {task.status.replace('_', ' ').toUpperCase()}
          </span>
        </p>

        {user.user_type === 'customer' && user.id === task.customer_id && (
          <div style={{marginTop: '20px'}}>
            <h4>Manage Task</h4>
            <div style={{display: 'flex', gap: '10px', marginTop: '10px'}}>
              {task.status === 'in_progress' && (
                <button onClick={() => handleStatusChange('completed')} className="btn btn-success btn-small">
                  Mark as Completed
                </button>
              )}
              {task.status === 'completed' && (
                <button onClick={() => handleStatusChange('archived')} className="btn btn-secondary btn-small">
                  Archive Task
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bids Section */}
      {task.bids && task.bids.length > 0 && (
        <div className="card">
          <h3>Bids ({task.bids.length})</h3>
          <div className="bid-list">
            {task.bids.map(bid => (
              <div key={bid.id} className="bid-item">
                <div className="bid-item-info">
                  <h4>Tasker ID: {bid.tasker_id}</h4>
                  <p><strong>Amount:</strong> ${bid.amount}</p>
                  {bid.message && <p><strong>Message:</strong> {bid.message}</p>}
                  <p><strong>Status:</strong> {bid.status}</p>
                </div>
                {user.user_type === 'customer' && 
                 user.id === task.customer_id && 
                 bid.status === 'pending' && 
                 task.status === 'open' && (
                  <button 
                    onClick={() => handleAcceptBid(bid.id)} 
                    className="btn btn-success btn-small"
                  >
                    Accept Bid
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bid Form for Taskers */}
      {user.user_type === 'tasker' && task.status === 'open' && (
        <div className="card">
          <h3>Submit a Bid</h3>
          <form onSubmit={handleBidSubmit}>
            <div className="form-group">
              <label>Bid Amount ($)</label>
              <input
                type="number"
                step="0.01"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Message (optional)</label>
              <textarea
                value={bidMessage}
                onChange={(e) => setBidMessage(e.target.value)}
                placeholder="Tell the customer why you're the best person for this job..."
              />
            </div>
            <button type="submit" className="btn">Submit Bid</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default TaskDetail;