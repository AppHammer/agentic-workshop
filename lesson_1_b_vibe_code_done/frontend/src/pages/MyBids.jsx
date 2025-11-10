import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { bidAPI } from '../api';

function MyBids() {
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBids = async () => {
      try {
        const response = await bidAPI.getMyBids();
        setBids(response.data);
      } catch (error) {
        console.error('Error fetching bids:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBids();
  }, []);

  if (loading) {
    return <div className="loading">Loading your bids...</div>;
  }

  return (
    <div>
      <h1>My Bids</h1>
      
      {bids.length === 0 ? (
        <div className="card">
          <p>You haven't submitted any bids yet.</p>
          <button onClick={() => navigate('/tasks')} className="btn btn-small" style={{marginTop: '10px'}}>
            Browse Tasks
          </button>
        </div>
      ) : (
        <div className="bid-list">
          {bids.map(bid => (
            <div key={bid.id} className="card">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                <div>
                  <h3>Task #{bid.task_id}</h3>
                  <p><strong>Bid Amount:</strong> ${bid.amount}</p>
                  {bid.message && <p><strong>Message:</strong> {bid.message}</p>}
                  <p>
                    <strong>Status:</strong>
                    <span className={`task-status status-${bid.status}`} style={{marginLeft: '10px'}}>
                      {bid.status.toUpperCase()}
                    </span>
                  </p>
                  <p style={{fontSize: '12px', color: '#666'}}>
                    Submitted: {new Date(bid.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button 
                  onClick={() => navigate(`/tasks/${bid.task_id}`)} 
                  className="btn btn-small"
                >
                  View Task
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyBids;