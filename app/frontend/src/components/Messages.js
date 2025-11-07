import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getMessages, sendMessage, markMessageRead } from '../api';

function Messages({ user }) {
  const location = useLocation();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [error, setError] = useState('');
  
  useEffect(() => {
    loadMessages();
  }, []);
  
  useEffect(() => {
    // Handle pre-selected conversation from navigation
    if (location.state?.preselectedUserId && conversations.length > 0) {
      const preselectedConv = conversations.find(
        conv => conv.partnerId === location.state.preselectedUserId
      );
      if (preselectedConv) {
        handleSelectConversation(preselectedConv);
      } else {
        // Create a new conversation stub for the preselected user
        const newConversation = {
          partnerId: location.state.preselectedUserId,
          partnerName: location.state.preselectedUserName || `User ${location.state.preselectedUserId}`,
          partnerRole: user.role === 'customer' ? 'tasker' : 'customer',
          messages: [],
          lastMessage: null,
          unreadCount: 0
        };
        setSelectedConversation(newConversation);
      }
    }
  }, [location.state, conversations]);
  
  const loadMessages = async () => {
    try {
      const response = await getMessages();
      // Group messages by conversation partner
      const grouped = groupMessagesByPartner(response.data, user.id);
      setConversations(grouped);
    } catch (err) {
      setError('Failed to load messages');
      console.error('Error loading messages:', err);
    }
  };
  
  const groupMessagesByPartner = (messages, currentUserId) => {
    const conversationMap = {};
    
    messages.forEach(msg => {
      const partnerId = msg.sender_id === currentUserId 
        ? msg.receiver_id 
        : msg.sender_id;
      
      if (!conversationMap[partnerId]) {
        conversationMap[partnerId] = {
          partnerId,
          partnerName: msg.sender_id === currentUserId 
            ? msg.receiver_name 
            : msg.sender_name,
          partnerRole: msg.sender_id === currentUserId 
            ? msg.receiver_role 
            : msg.sender_role,
          messages: [],
          lastMessage: msg,
          unreadCount: 0
        };
      }
      
      conversationMap[partnerId].messages.push(msg);
      
      // Count unread messages received by current user
      if (msg.receiver_id === currentUserId && !msg.read) {
        conversationMap[partnerId].unreadCount++;
      }
      
      // Update last message if this one is newer
      if (new Date(msg.created_at) > new Date(conversationMap[partnerId].lastMessage.created_at)) {
        conversationMap[partnerId].lastMessage = msg;
      }
    });
    
    // Sort by most recent message
    return Object.values(conversationMap).sort((a, b) => 
      new Date(b.lastMessage.created_at) - new Date(a.lastMessage.created_at)
    );
  };
  
  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const messageDate = new Date(timestamp);
    const diffMs = now - messageDate;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 24) {
      if (diffHours < 1) {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return diffMins < 1 ? 'Just now' : `${diffMins} min ago`;
      }
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    }
    
    return messageDate.toLocaleDateString() + ' ' + messageDate.toLocaleTimeString();
  };
  
  const truncateMessage = (text, maxLength = 50) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };
  
  const handleSelectConversation = async (conversation) => {
    setSelectedConversation(conversation);
    
    // Mark unread messages as read
    const unreadMessages = conversation.messages.filter(
      msg => msg.receiver_id === user.id && !msg.read
    );
    
    for (const msg of unreadMessages) {
      try {
        await markMessageRead(msg.id);
      } catch (err) {
        console.error('Failed to mark message as read:', err);
      }
    }
    
    // Reload messages to update read status
    await loadMessages();
  };
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageContent.trim() || !selectedConversation) return;
    
    setError('');
    try {
      await sendMessage({
        receiver_id: selectedConversation.partnerId,
        content: messageContent,
        task_id: location.state?.taskId || selectedConversation.lastMessage?.task_id
      });
      
      setMessageContent('');
      await loadMessages();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send message');
      console.error('Error sending message:', err);
    }
  };
  
  return (
    <div className="messages-container">
      <div className="conversations-panel">
        <h2>Messages</h2>
        {error && <div className="error">{error}</div>}
        {conversations.length === 0 ? (
          <p className="empty-state">No messages yet</p>
        ) : (
          <div className="conversation-list">
            {conversations.map(conv => (
              <div
                key={conv.partnerId}
                className={`conversation-item ${
                  selectedConversation?.partnerId === conv.partnerId ? 'active' : ''
                }`}
                onClick={() => handleSelectConversation(conv)}
                role="button"
                tabIndex={0}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleSelectConversation(conv);
                  }
                }}
                aria-label={`Conversation with ${conv.partnerName}, ${conv.partnerRole}`}
              >
                <div className="conversation-header">
                  <span className="partner-name">{conv.partnerName}</span>
                  <span className={`role-badge ${conv.partnerRole.toLowerCase()}`}>
                    {conv.partnerRole}
                  </span>
                  {conv.unreadCount > 0 && (
                    <span className="unread-badge" aria-label={`${conv.unreadCount} unread messages`}>
                      {conv.unreadCount}
                    </span>
                  )}
                </div>
                <p className="last-message">
                  {truncateMessage(conv.lastMessage.content)}
                </p>
                <span className="timestamp">
                  {formatTimestamp(conv.lastMessage.created_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="message-thread-panel">
        {selectedConversation ? (
          <>
            <div className="thread-header">
              <h3>{selectedConversation.partnerName}</h3>
              <span className={`role-badge ${selectedConversation.partnerRole.toLowerCase()}`}>
                {selectedConversation.partnerRole}
              </span>
            </div>
            
            <div className="message-thread">
              {selectedConversation.messages
                .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                .map(msg => (
                  <div
                    key={msg.id}
                    className={`message ${
                      msg.sender_id === user.id ? 'sent' : 'received'
                    }`}
                  >
                    <p>{msg.content}</p>
                    <span className="timestamp">
                      {formatTimestamp(msg.created_at)}
                    </span>
                  </div>
                ))}
            </div>
            
            <form onSubmit={handleSendMessage} className="message-form">
              <input
                type="text"
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
                placeholder="Type your message..."
                aria-label="Message input"
              />
              <button type="submit" className="btn-primary">Send</button>
            </form>
          </>
        ) : (
          <div className="no-conversation-selected">
            <p>Select a conversation to view messages</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Messages;