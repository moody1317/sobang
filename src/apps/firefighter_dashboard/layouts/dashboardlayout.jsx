import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/sidebar';
import Header from '../components/header';
import { UserContext } from '../contexts/usercontext';
import { isLoggedIn, getMe } from '../../../api/auth';
import './dashboardlayout.css';

function DashboardLayout({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate('/');
      return;
    }
    getMe().then(setUser).catch(() => {});
  }, []);

  return (
    <UserContext.Provider value={user}>
      <div className="dashboard-layout">
        <Sidebar />
        <div className="dashboard-body">
          <Header />
          <main className="dashboard-content">
            {children}
          </main>
        </div>
      </div>
    </UserContext.Provider>
  );
}

export default DashboardLayout;
