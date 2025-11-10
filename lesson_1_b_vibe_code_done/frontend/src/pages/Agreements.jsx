import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { agreementAPI } from '../api';

function Agreements() {
  const { user } = useAuth();
  const [agreements, setAgreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgreements();
  }, []);

  const fetchAgreements = async () => {
    try {
      const response = await agreementAPI.list();
      setAgreements(response.data);
    } catch (error) {
      console.error('Error fetching agreements:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkPaid = async (agreementId) => {
    setError('');
    setSuccess('');
    
    try {
      await agreementAPI.markPaid(agreementId);
      setSuccess('Payment confirmed! Task marked as completed.');
      fetchAgreements();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to mark as paid');
    }
  };

  if (loading) {
    return <div className="loading">Loading agreements...</div>;
  }

  return (
    <div>
      <h1>My Agreements</h1>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {agreements.length === 0 ? (
        <div className="card">
          <p>You don't have any agreements yet.</p>
        </div>
      ) : (
        <div>
          {agreements.map(agreement => (
            <div key={agreement.id} className="card">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                <div>
                  <h3>Agreement #{agreement.id}</h3>
                  <p><strong>Task ID:</strong> {agreement.task_id}</p>
                  <p><strong>Bid ID:</strong> {agreement.bid_id}</p>
                  <p><strong>Agreed Amount:</strong> ${agreement.agreed_amount}</p>
                  <p>
                    <strong>Payment Status:</strong>
                    <span 
                      className={`task-status ${agreement.is_paid ? 'status-completed' : 'status-in_progress'}`}
                      style={{marginLeft: '10px'}}
                    >
                      {agreement.is_paid ? 'PAID' : 'PENDING'}
                    </span>
                  </p>
                  <p style={{fontSize: '12px', color: '#666'}}>
                    Created: {new Date(agreement.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div style={{display: 'flex', gap: '10px'}}>
                  <button 
                    onClick={() => navigate(`/tasks/${agreement.task_id}`)} 
                    className="btn btn-small"
                  >
                    View Task
                  </button>
                  {user.user_type === 'customer' && !agreement.is_paid && (
                    <button 
                      onClick={() => handleMarkPaid(agreement.id)} 
                      className="btn btn-success btn-small"
                    >
                      Mark as Paid
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Agreements;