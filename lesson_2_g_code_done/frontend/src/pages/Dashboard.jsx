import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { taskAPI, bidAPI, agreementAPI } from '../api';

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    tasks: 0,
    bids: 0,
    agreements: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        if (user.user_type === 'customer') {
          const tasksResponse = await taskAPI.list();
          const agreementsResponse = await agreementAPI.list();
          setStats({
            tasks: tasksResponse.data.length,
            agreements: agreementsResponse.data.length
          });
        } else {
          const bidsResponse = await bidAPI.getMyBids();
          const agreementsResponse = await agreementAPI.list();
          setStats({
            bids: bidsResponse.data.length,
            agreements: agreementsResponse.data.length
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, [user]);

  return (
    <div>
      <h1>Welcome, {user.username}!</h1>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        {user.user_type === 'customer' 
          ? 'Find taskers to help with your projects'
          : 'Browse available tasks and start earning'}
      </p>

      <div className="dashboard-grid">
        {user.user_type === 'customer' ? (
          <>
            <div className="dashboard-card">
              <h2>{stats.tasks}</h2>
              <p>My Tasks</p>
            </div>
            <div className="dashboard-card">
              <h2>{stats.agreements}</h2>
              <p>Active Agreements</p>
            </div>
          </>
        ) : (
          <>
            <div className="dashboard-card">
              <h2>{stats.bids}</h2>
              <p>My Bids</p>
            </div>
            <div className="dashboard-card">
              <h2>{stats.agreements}</h2>
              <p>Active Agreements</p>
            </div>
          </>
        )}
      </div>

      <div className="card" style={{ marginTop: '30px' }}>
        <h3>Quick Actions</h3>
        <div style={{ marginTop: '15px' }}>
          {user.user_type === 'customer' ? (
            <>
              <p>• Post a new task to find help</p>
              <p>• Review bids from taskers</p>
              <p>• Manage your active agreements</p>
            </>
          ) : (
            <>
              <p>• Browse available tasks</p>
              <p>• Submit bids on tasks that match your skills</p>
              <p>• Complete tasks and build your reputation</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;