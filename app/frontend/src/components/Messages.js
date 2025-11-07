import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { getMessages, sendMessage, markMessageRead, getUserTasks } from '../api';

function Messages({ user }) {
  const location = useLocation();
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [error, setError] = useState('');
  const [selectedTaskFilter, setSelectedTaskFilter] = useState(null);
  const [userTasks, setUserTasks] = useState([]);
  const [lastMessageId, setLastMessageId] = useState(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  
  const messageThreadRef = useRef(null);
  const pollingIntervalRef = useRef(null);
  
  // Initial load
  useEffect(() => {
    loadMessages();
    loadUserTasks();
    
    // Set up polling for new messages
    setupPolling();
    
    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, []);
  
  // Track scroll position to determine auto-scroll behavior
  useEffect(() => {
    const messageThread = messageThreadRef.current;
    if (messageThread) {
      const handleScroll = () => {
        const threshold = 50; // pixels from bottom
        const atBottom = messageThread.scrollHeight - messageThread.scrollTop
          <= messageThread.clientHeight + threshold;
        setIsAtBottom(atBottom);
      };
      
      messageThread.addEventListener('scroll', handleScroll);
      return () => messageThread.removeEventListener('scroll', handleScroll);
    }
  }, [selectedConversation]);
  
  // Setup polling with Page Visibility API
  const setupPolling = () => {
    // Poll every 5 seconds
    pollingIntervalRef.current = setInterval(() => {
      // Only poll if tab is visible
      if (document.visibilityState === 'visible') {
        loadMessages(true); // Pass true for incremental/polling load
      }
    }, 5000);
  };
  
  useEffect(() => {
    // Apply filter whenever conversations or filter changes
    if (selectedTaskFilter === null) {
      setFilteredConversations(conversations);
    } else {
      const filtered = conversations.filter(conv =>
        conv.messages.some(msg => msg.task_id === selectedTaskFilter)
      );
      setFilteredConversations(filtered);
    }
  }, [conversations, selectedTaskFilter]);
  
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
  
  const loadMessages = async (incremental = false) => {
    try {
      const response = await getMessages();
      const messages = response.data;
      
      if (messages.length > 0) {
        const newLastMessageId = messages[0].id;
        
        // Only update if we have new messages (or if not incremental)
        if (!incremental || newLastMessageId !== lastMessageId) {
          const grouped = groupMessagesByPartner(messages, user.id);
          setConversations(grouped);
          setLastMessageId(newLastMessageId);
          
          // Reset retry count on success
          if (retryCount > 0) {
            setRetryCount(0);
          }
          
          // Auto-scroll if user was at bottom
          if (isAtBottom && messageThreadRef.current) {
            setTimeout(() => {
              if (messageThreadRef.current) {
                messageThreadRef.current.scrollTop = messageThreadRef.current.scrollHeight;
              }
            }, 100);
          }
        }
      }
    } catch (err) {
      console.error('Error loading messages:', err);
      
      // Implement exponential backoff for repeated failures
      if (incremental) {
        const newRetryCount = retryCount + 1;
        setRetryCount(newRetryCount);
        
        // Don't show error on first few retries during polling
        if (newRetryCount > 3) {
          setError('Having trouble loading new messages. Will keep trying...');
        }
        
        // If too many failures, clear interval and show persistent error
        if (newRetryCount > 10) {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          setError('Connection lost. Please refresh the page.');
        }
      } else {
        setError('Failed to load messages');
      }
    }
  };
  
  const loadUserTasks = async () => {
    try {
      const response = await getUserTasks();
      setUserTasks(response.data);
    } catch (err) {
      console.error('Error loading tasks:', err);
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
    
    // Scroll to bottom of new conversation
    if (messageThreadRef.current) {
      setTimeout(() => {
        if (messageThreadRef.current) {
          messageThreadRef.current.scrollTop = messageThreadRef.current.scrollHeight;
          setIsAtBottom(true);
        }
      }, 100);
    }
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
  
  const handleTaskFilterChange = (e) => {
    const taskId = e.target.value ? parseInt(e.target.value) : null;
    setSelectedTaskFilter(taskId);
  };
  
  return (
    <div className="messages-container">
      <div className="conversations-panel">
        <div className="messages-header">
          <h2>Messages</h2>
          <div className="task-filter">
            <label htmlFor="task-filter">Filter by Task:</label>
            <select
              id="task-filter"
              value={selectedTaskFilter || ''}
              onChange={handleTaskFilterChange}
              className="task-filter-dropdown"
              aria-label="Filter messages by task"
            >
              <option value="">All Tasks</option>
              {userTasks.map(task => (
                <option key={task.id} value={task.id}>
                  {task.title} ({task.status})
                </option>
              ))}
            </select>
          </div>
        </div>
        {error && <div className="error">{error}</div>}
        {filteredConversations.length === 0 ? (
          <p className="empty-state">
            {selectedTaskFilter
              ? 'No conversations found for this task'
              : 'No messages yet'}
          </p>
        ) : (
          <div className="conversation-list">
            {filteredConversations.map(conv => (
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
            
            <div className="message-thread" ref={messageThreadRef}>
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