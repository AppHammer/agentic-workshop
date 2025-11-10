import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

function Navigation() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="nav">
      <div className="nav-content">
        <h1>Tasker Marketplace</h1>
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/tasks">Tasks</Link>
          {user.user_type === 'customer' && (
            <Link to="/create-task">Create Task</Link>
          )}
          {user.user_type === 'tasker' && (
            <Link to="/my-bids">My Bids</Link>
          )}
          <Link to="/agreements">Agreements</Link>
          <Link to="/messages">Messages</Link>
          <Link to="/profile" style={{color: 'white'}}>
            {user.username} ({user.user_type})
          </Link>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;