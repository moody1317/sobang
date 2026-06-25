import Sidebar from '../components/sidebar';
import Header from '../components/header';
import './dashboardlayout.css';

function DashboardLayout({ children }) {
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