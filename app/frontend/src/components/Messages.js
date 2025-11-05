import React, { useState, useEffect } from 'react';
import { getMessages, sendMessage, markMessageRead } from '../api';

function Messages({ user }) {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState({});
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadMessages();
  }, []);

  const loadMessages = async () => {
    try {
      const response = await getMessages();
      setMessages(response.data);
      
      // Group messages by conversation
      const grouped = {};
      response.data.forEach(msg => {
        const otherId = msg.sender_id === user.id ? msg.receiver_id : msg.sender_id;
        if (!grouped[otherId]) {
          grouped[otherId] = [];
        }
        grouped[otherId].push(msg);
      });
      setConversations(grouped);
    } catch (err) {
      setError('Failed to load messages');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!selectedUserId || !newMessage.trim()) return;
    
    setError('');
    setSuccess('');
    try {
      await sendMessage({
        receiver_id: selectedUserId,
        content: newMessage
      });
      setNewMessage('');
      setSuccess('Message sent!');
      loadMessages();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message');
    }
  };

  const handleSelectConversation = async (userId) => {
    setSelectedUserId(userId);
    
    // Mark unread messages as read
    const unreadMessages = conversations[userId]?.filter(
      msg => msg.receiver_id === user.id && !msg.read
    );
    
    for (const msg of unreadMessages || []) {
      try {
        await markMessageRead(msg.id);
      } catch (err) {
        console.error('Failed to mark message as read', err);
      }
    }
    
    loadMessages();
  };

  const selectedConversation = selectedUserId ? conversations[selectedUserId] : [];

  return (
    <div className="container">
      <h2>Messages</h2>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        {/* Conversations List */}
        <div className="card">
          <h3>Conversations</h3>
          {Object.keys(conversations).length === 0 ? (
            <p>No messages yet</p>
          ) : (
            <div>
              {Object.keys(conversations).map(userId => {
                const conv = conversations[userId];
                const unreadCount = conv.filter(
                  msg => msg.receiver_id === user.id && !msg.read
                ).length;
                const lastMessage = conv[conv.length - 1];
                
                return (
                  <div
                    key={userId}
                    onClick={() => handleSelectConversation(parseInt(userId))}
                    style={{
                      padding: '10px',
                      margin: '5px 0',
                      backgroundColor: selectedUserId === parseInt(userId) ? '#e3f2fd' : '#f5f5f5',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    <strong>User {userId}</strong>
                    {unreadCount > 0 && (
                      <span style={{ 
                        backgroundColor: '#dc3545', 
                        color: 'white', 
                        padding: '2px 6px', 
                        borderRadius: '10px',
                        fontSize: '12px',
                        marginLeft: '10px'
                      }}>
                        {unreadCount}
                      </span>
                    )}
                    <p style={{ fontSize: '14px', color: '#666', margin: '5px 0 0 0' }}>
                      {lastMessage.content.substring(0, 50)}...
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Message Thread */}
        <div className="card">
          {selectedUserId ? (
            <>
              <h3>Conversation with User {selectedUserId}</h3>
              <div className="message-list" style={{ marginBottom: '20px' }}>
                {selectedConversation.sort((a, b) => 
                  new Date(a.created_at) - new Date(b.created_at)
                ).map(msg => (
                  <div 
                    key={msg.id} 
                    className={`message ${msg.sender_id === user.id ? 'sent' : 'received'}`}
                  >
                    <p style={{ margin: '0 0 5px 0' }}>{msg.content}</p>
                    <small style={{ color: '#666' }}>
                      {new Date(msg.created_at).toLocaleString()}
                    </small>
                  </div>
                ))}
              </div>
              
              <form onSubmit={handleSendMessage}>
                <div className="form-group">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    rows="3"
                    required
                  />
                </div>
                <button type="submit" className="btn-primary">Send Message</button>
              </form>
            </>
          ) : (
            <p>Select a conversation to view messages</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Messages;