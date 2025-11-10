import React from 'react';
import { Link } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  return (
    <nav className="nav">
      <div className="nav-container">
        <h1>Tasker Platform</h1>
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/tasks">Browse Tasks</Link>
          <Link to="/messages">Messages</Link>
          <Link to="/profile" style={{ color: 'white', textDecoration: 'none' }}>
            {user.full_name} ({user.role})
          </Link>
          <button onClick={onLogout} className="btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;