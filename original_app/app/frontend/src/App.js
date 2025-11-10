import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import CustomerDashboard from './components/CustomerDashboard';
import TaskerDashboard from './components/TaskerDashboard';
import TaskList from './components/TaskList';
import TaskDetail from './components/TaskDetail';
import Messages from './components/Messages';
import Navbar from './components/Navbar';
import Profile from './components/Profile';
import { getCurrentUser } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await getCurrentUser();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const handleLogin = async (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        {user && <Navbar user={user} onLogout={handleLogout} />}
        <Routes>
          <Route 
            path="/login" 
            element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />} 
          />
          <Route 
            path="/register" 
            element={!user ? <Register onLogin={handleLogin} /> : <Navigate to="/" />} 
          />
          <Route 
            path="/" 
            element={
              user ? (
                user.role === 'customer' ? (
                  <CustomerDashboard user={user} />
                ) : (
                  <TaskerDashboard user={user} />
                )
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/tasks" 
            element={user ? <TaskList user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/tasks/:id" 
            element={user ? <TaskDetail user={user} /> : <Navigate to="/login" />} 
          />
          <Route
            path="/messages"
            element={user ? <Messages user={user} /> : <Navigate to="/login" />}
          />
          <Route
            path="/profile"
            element={user ? <Profile /> : <Navigate to="/login" />}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;