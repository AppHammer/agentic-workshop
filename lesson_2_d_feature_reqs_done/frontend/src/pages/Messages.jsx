import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { messageAPI } from '../api';

function Messages() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState({
    receiver_id: '',
    content: '',
    task_id: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await messageAPI.list();
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const messageData = {
        receiver_id: parseInt(newMessage.receiver_id),
        content: newMessage.content
      };
      
      if (newMessage.task_id) {
        messageData.task_id = parseInt(newMessage.task_id);
      }

      await messageAPI.send(messageData);
      setSuccess('Message sent successfully!');
      setNewMessage({ receiver_id: '', content: '', task_id: '' });
      fetchMessages();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message');
    }
  };

  const handleMarkRead = async (messageId) => {
    try {
      await messageAPI.markRead(messageId);
      fetchMessages();
    } catch (error) {
      console.error('Error marking message as read:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading messages...</div>;
  }

  return (
    <div>
      <h1>Messages</h1>

      {/* Send Message Form */}
      <div className="card">
        <h3>Send New Message</h3>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
        
        <form onSubmit={handleSendMessage}>
          <div className="form-group">
            <label>Recipient User ID</label>
            <input
              type="number"
              value={newMessage.receiver_id}
              onChange={(e) => setNewMessage({ ...newMessage, receiver_id: e.target.value })}
              placeholder="Enter user ID"
              required
            />
          </div>
          <div className="form-group">
            <label>Task ID (optional)</label>
            <input
              type="number"
              value={newMessage.task_id}
              onChange={(e) => setNewMessage({ ...newMessage, task_id: e.target.value })}
              placeholder="Related task ID"
            />
          </div>
          <div className="form-group">
            <label>Message</label>
            <textarea
              value={newMessage.content}
              onChange={(e) => setNewMessage({ ...newMessage, content: e.target.value })}
              placeholder="Type your message here..."
              required
            />
          </div>
          <button type="submit" className="btn">Send Message</button>
        </form>
      </div>

      {/* Messages List */}
      <div className="card">
        <h3>All Messages</h3>
        {messages.length === 0 ? (
          <p>No messages yet.</p>
        ) : (
          <div className="message-list">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`message-item ${!message.is_read && message.receiver_id === user.id ? 'unread' : ''}`}
                onClick={() => !message.is_read && message.receiver_id === user.id && handleMarkRead(message.id)}
              >
                <div className="message-header">
                  <span>
                    {message.sender_id === user.id ? 'To' : 'From'}: User #{message.sender_id === user.id ? message.receiver_id : message.sender_id}
                  </span>
                  <span>{new Date(message.created_at).toLocaleString()}</span>
                </div>
                {message.task_id && (
                  <p style={{fontSize: '12px', color: '#666'}}>
                    Related to Task #{message.task_id}
                  </p>
                )}
                <div className="message-content">
                  {message.content}
                </div>
                {!message.is_read && message.receiver_id === user.id && (
                  <span style={{fontSize: '12px', color: '#3498db', marginTop: '5px', display: 'block'}}>
                    Click to mark as read
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Messages;