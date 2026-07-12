import { useEffect } from 'react';
import Sidebar from '../components/sidebar';
import Header from '../components/header';
import { useRefreshAlertCount } from '../contexts/alertcontext';
import './dashboardlayout.css';

function DashboardLayout({ children }) {
  const refreshAlertCount = useRefreshAlertCount();

  useEffect(() => {
    refreshAlertCount?.();
  }, [refreshAlertCount]);

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-body">
        <Header />
        <main className="dashboard-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;