import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  getTask, 
  getTaskBids, 
  createBid, 
  acceptBid, 
  createOffer, 
  acceptOffer,
  getMyOffers,
  getAgreements,
  completeAgreement,
  createReview,
  getUserReviews,
  getUser
} from '../api';

function TaskDetail({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [bids, setBids] = useState([]);
  const [offers, setOffers] = useState([]);
  const [agreement, setAgreement] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [bidAmount, setBidAmount] = useState('');
  const [bidMessage, setBidMessage] = useState('');
  const [offerAmount, setOfferAmount] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [selectedTasker, setSelectedTasker] = useState('');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');
  const [customer, setCustomer] = useState(null);

  useEffect(() => {
    loadTaskDetails();
  }, [id]);

  const loadTaskDetails = async () => {
    try {
      const [taskRes, bidsRes, offersRes, agreementsRes] = await Promise.all([
        getTask(id),
        getTaskBids(id),
        getMyOffers(),
        getAgreements()
      ]);
      
      setTask(taskRes.data);
      setBids(bidsRes.data);
      
      // Filter offers for this task
      const taskOffers = offersRes.data.filter(o => o.task_id === parseInt(id));
      setOffers(taskOffers);
      
      // Find agreement for this task
      const taskAgreement = agreementsRes.data.find(a => a.task_id === parseInt(id));
      setAgreement(taskAgreement);

      // Load customer info
      const customerRes = await getUser(taskRes.data.customer_id);
      setCustomer(customerRes.data);

      // Load reviews if task is completed
      if (taskRes.data.status === 'completed') {
        const reviewsRes = await getUserReviews(taskRes.data.customer_id);
        setReviews(reviewsRes.data.filter(r => r.task_id === parseInt(id)));
      }
    } catch (err) {
      setError('Failed to load task details');
    }
  };

  const handlePlaceBid = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await createBid({
        task_id: parseInt(id),
        amount: parseFloat(bidAmount),
        message: bidMessage
      });
      setSuccess('Bid placed successfully!');
      setBidAmount('');
      setBidMessage('');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to place bid');
    }
  };

  const handleMakeOffer = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await createOffer({
        task_id: parseInt(id),
        tasker_id: parseInt(selectedTasker),
        amount: parseFloat(offerAmount),
        message: offerMessage
      });
      setSuccess('Offer sent successfully!');
      setOfferAmount('');
      setOfferMessage('');
      setSelectedTasker('');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to make offer');
    }
  };

  const handleAcceptBid = async (bidId) => {
    setError('');
    setSuccess('');
    try {
      await acceptBid(bidId);
      setSuccess('Bid accepted! Agreement created.');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept bid');
    }
  };

  const handleAcceptOffer = async (offerId) => {
    setError('');
    setSuccess('');
    try {
      await acceptOffer(offerId);
      setSuccess('Offer accepted! Agreement created.');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept offer');
    }
  };

  const handleCompleteTask = async () => {
    setError('');
    setSuccess('');
    try {
      await completeAgreement(agreement.id);
      setSuccess('Task marked as complete!');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete task');
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const revieweeId = user.role === 'customer' ? agreement.tasker_id : task.customer_id;
      await createReview({
        task_id: parseInt(id),
        reviewee_id: revieweeId,
        rating: reviewRating,
        comment: reviewComment
      });
      setSuccess('Review submitted successfully!');
      setReviewRating(5);
      setReviewComment('');
      loadTaskDetails();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit review');
    }
  };

  if (!task) {
    return <div className="container">Loading...</div>;
  }

  const isCustomer = user.role === 'customer';
  const isTaskOwner = task.customer_id === user.id;
  const canBid = !isCustomer && task.status === 'open';
  const myOffer = offers.find(o => o.tasker_id === user.id);

  return (
    <div className="container">
      <button onClick={() => navigate(-1)} className="btn-secondary" style={{ marginBottom: '20px' }}>
        ← Back
      </button>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <h2>{task.title}</h2>
        <p className="budget">${task.budget}</p>
        <p className="location">📍 {task.location}</p>
        <p className="date">📅 {new Date(task.date).toLocaleString()}</p>
        <p><strong>Status:</strong> {task.status}</p>
        <p><strong>Description:</strong></p>
        <p>{task.description}</p>
        {customer && (
          <p><strong>Posted by:</strong> {customer.full_name} ({customer.location})</p>
        )}
      </div>

      {/* Tasker: Place Bid */}
      {canBid && (
        <div className="card">
          <h3>Place Your Bid</h3>
          <form onSubmit={handlePlaceBid}>
            <div className="form-group">
              <label>Your Bid Amount ($)</label>
              <input
                type="number"
                value={bidAmount}
                onChange={(e) => setBidAmount(e.target.value)}
                min="0"
                step="0.01"
                required
              />
            </div>
            <div className="form-group">
              <label>Message to Customer</label>
              <textarea
                value={bidMessage}
                onChange={(e) => setBidMessage(e.target.value)}
                rows="3"
                placeholder="Tell the customer why you're the best fit..."
              />
            </div>
            <button type="submit" className="btn-success">Place Bid</button>
          </form>
        </div>
      )}

      {/* Customer: View Bids */}
      {isTaskOwner && bids.length > 0 && (
        <div className="card">
          <h3>Bids Received ({bids.length})</h3>
          <div className="bid-list">
            {bids.map((bid) => (
              <div key={bid.id} className="bid-item">
                <p><strong>Amount:</strong> ${bid.amount}</p>
                <p><strong>Message:</strong> {bid.message}</p>
                <p><strong>Tasker ID:</strong> {bid.tasker_id}</p>
                {!agreement && task.status === 'open' && (
                  <button 
                    onClick={() => handleAcceptBid(bid.id)} 
                    className="btn-success"
                    style={{ marginTop: '10px' }}
                  >
                    Accept This Bid
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Customer: Make Offer to Tasker */}
      {isTaskOwner && task.status === 'open' && bids.length > 0 && (
        <div className="card">
          <h3>Make an Offer to a Tasker</h3>
          <form onSubmit={handleMakeOffer}>
            <div className="form-group">
              <label>Select Tasker</label>
              <select 
                value={selectedTasker} 
                onChange={(e) => setSelectedTasker(e.target.value)}
                required
              >
                <option value="">Choose a tasker...</option>
                {bids.map((bid) => (
                  <option key={bid.tasker_id} value={bid.tasker_id}>
                    Tasker {bid.tasker_id} (Bid: ${bid.amount})
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Offer Amount ($)</label>
              <input
                type="number"
                value={offerAmount}
                onChange={(e) => setOfferAmount(e.target.value)}
                min="0"
                step="0.01"
                required
              />
            </div>
            <div className="form-group">
              <label>Message</label>
              <textarea
                value={offerMessage}
                onChange={(e) => setOfferMessage(e.target.value)}
                rows="3"
              />
            </div>
            <button type="submit" className="btn-success">Send Offer</button>
          </form>
        </div>
      )}

      {/* Tasker: View Offers */}
      {myOffer && (
        <div className="card">
          <h3>Offer Received</h3>
          <div className="offer-item">
            <p><strong>Amount:</strong> ${myOffer.amount}</p>
            <p><strong>Message:</strong> {myOffer.message}</p>
            {!myOffer.accepted && task.status === 'open' && (
              <button 
                onClick={() => handleAcceptOffer(myOffer.id)} 
                className="btn-success"
                style={{ marginTop: '10px' }}
              >
                Accept This Offer
              </button>
            )}
            {myOffer.accepted && <p className="success">✓ Offer Accepted!</p>}
          </div>
        </div>
      )}

      {/* Agreement Status */}
      {agreement && (
        <div className="card">
          <h3>Agreement</h3>
          <p><strong>Amount:</strong> ${agreement.amount}</p>
          <p><strong>Status:</strong> {agreement.status}</p>
          {agreement.status === 'accepted' && isTaskOwner && task.status === 'in_progress' && (
            <button 
              onClick={handleCompleteTask} 
              className="btn-success"
              style={{ marginTop: '10px' }}
            >
              Mark Task as Complete
            </button>
          )}
        </div>
      )}

      {/* Reviews Section */}
      {task.status === 'completed' && agreement && (
        <div className="card">
          <h3>Submit Review</h3>
          <form onSubmit={handleSubmitReview}>
            <div className="form-group">
              <label>Rating (1-5)</label>
              <select 
                value={reviewRating} 
                onChange={(e) => setReviewRating(parseInt(e.target.value))}
              >
                <option value={5}>5 - Excellent</option>
                <option value={4}>4 - Good</option>
                <option value={3}>3 - Average</option>
                <option value={2}>2 - Below Average</option>
                <option value={1}>1 - Poor</option>
              </select>
            </div>
            <div className="form-group">
              <label>Comment</label>
              <textarea
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                rows="4"
              />
            </div>
            <button type="submit" className="btn-success">Submit Review</button>
          </form>
        </div>
      )}

      {reviews.length > 0 && (
        <div className="card">
          <h3>Reviews</h3>
          {reviews.map((review) => (
            <div key={review.id} className="review-card">
              <div className="rating">{'⭐'.repeat(review.rating)}</div>
              <p>{review.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TaskDetail;