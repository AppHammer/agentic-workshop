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

export const authAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/token', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    transformRequest: [(data) => {
      const params = new URLSearchParams();
      params.append('username', data.username);
      params.append('password', data.password);
      return params;
    }]
  }),
  getCurrentUser: () => api.get('/users/me'),
};

export const taskAPI = {
  create: (data) => api.post('/tasks', data),
  list: (status) => api.get('/tasks', { params: { status } }),
  get: (id) => api.get(`/tasks/${id}`),
  updateStatus: (id, status) => api.put(`/tasks/${id}/status`, null, { params: { status } }),
};

export const bidAPI = {
  create: (data) => api.post('/bids', data),
  getMyBids: () => api.get('/bids/my-bids'),
  accept: (id) => api.put(`/bids/${id}/accept`),
};

export const agreementAPI = {
  list: () => api.get('/agreements'),
  markPaid: (id) => api.put(`/agreements/${id}/pay`),
};

export const reviewAPI = {
  create: (data) => api.post('/reviews', data),
  getTaskerReviews: (taskerId) => api.get(`/reviews/tasker/${taskerId}`),
};

export const messageAPI = {
  send: (data) => api.post('/messages', data),
  list: () => api.get('/messages'),
  markRead: (id) => api.put(`/messages/${id}/read`),
};

export default api;