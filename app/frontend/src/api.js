import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (userData) => api.post('/register', userData);

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  return api.post('/token', formData);
};

export const getCurrentUser = () => api.get('/users/me');

export const getUser = (userId) => api.get(`/users/${userId}`);

// Tasks
export const createTask = (taskData) => api.post('/tasks', taskData);

export const getTasks = (status) => {
  const params = status ? { status } : {};
  return api.get('/tasks', { params });
};

export const getTask = (taskId) => api.get(`/tasks/${taskId}`);

export const updateTask = (taskId, taskData) => api.put(`/tasks/${taskId}`, taskData);

export const getMyTasks = () => api.get('/tasks/user/my-tasks');

export const getUserTasks = () => api.get('/tasks/my-tasks');

// Bids
export const createBid = (bidData) => api.post('/bids', bidData);

export const getTaskBids = (taskId) => api.get(`/tasks/${taskId}/bids`);

export const acceptBid = (bidId) => api.post(`/bids/${bidId}/accept`);

// Offers
export const createOffer = (offerData) => api.post('/offers', offerData);

export const acceptOffer = (offerId) => api.post(`/offers/${offerId}/accept`);

export const getMyOffers = () => api.get('/offers/my-offers');

// Agreements
export const completeAgreement = (agreementId) => api.post(`/agreements/${agreementId}/complete`);

export const getAgreements = () => api.get('/agreements');

// Messages
export const sendMessage = (messageData) => api.post('/messages', messageData);

export const getMessages = () => api.get('/messages');

export const markMessageRead = (messageId) => api.put(`/messages/${messageId}/read`);

// Task Messages
export const getTaskMessages = (taskId) => api.get(`/tasks/${taskId}/messages`);

export const sendTaskMessage = (taskId, content) => api.post(`/tasks/${taskId}/messages`, { content });

// Reviews
export const createReview = (reviewData) => api.post('/reviews', reviewData);

export const getUserReviews = (userId) => api.get(`/users/${userId}/reviews`);

export default api;