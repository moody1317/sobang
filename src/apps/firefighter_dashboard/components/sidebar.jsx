import { NavLink, useNavigate } from 'react-router-dom';
import { logout } from '../../../api/auth';
import { useUser } from '../contexts/usercontext';
import './sidebar.css';

const NAV_SECTIONS = [
  {
    label: '현황',
    items: [
      { to: '/dashboard', icon: 'bi-house', label: '브리핑 홈', end: true },
      { to: '/dashboard/map', icon: 'bi-map', label: '위험 스코어 지도' },
      { to: '/dashboard/priority', icon: 'bi-list-check', label: '점검 우선순위' },
      { to: '/dashboard/stats', icon: 'bi-bar-chart-line', label: '통계' },
    ],
  },
  {
    label: '운영',
    items: [
      { to: '/dashboard/inspection', icon: 'bi-journal-text', label: '점검 일지' },
      { to: '/dashboard/schedule', icon: 'bi-calendar3', label: '근무 일정' },
      { to: '/dashboard/alerts', icon: 'bi-bell', label: '알림 센터', badge: 3 },
    ],
  },
  {
    label: '정보',
    items: [
      { to: '/dashboard/data', icon: 'bi-database', label: '데이터·방법론' },
      { to: '/dashboard/admin', icon: 'bi-shield-check', label: '관리자', adminOnly: true },
    ],
  },
];

function Sidebar() {
  const user = useUser();
  const navigate = useNavigate();
  const isAdmin = user?.rank === '관리자';

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <i className="bi bi-fire" />
        </div>
        <div className="sidebar-logo-text">
          <span className="sidebar-logo-name">위험 관제</span>
          <span className="sidebar-logo-sub">FIRE RISK SCORE</span>
        </div>
      </div>

      {user && (
        <div className="sidebar-station">
          <div className="sidebar-station-name">{user.station_name}</div>
          <div className='sidebar-station-sub'>{user.unit_name}</div>
        </div>
      )}

      <nav className="sidebar-nav">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.filter((item) => !item.adminOnly || isAdmin).map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `sidebar-nav-item${isActive ? ' active' : ''}`
                }
              >
                <i className={`bi ${item.icon}`} />
                <span>{item.label}</span>
                {item.badge != null && (
                  <span className="sidebar-badge">{item.badge}</span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <NavLink
          to="/dashboard/profile"
          className={({ isActive }) =>
            `sidebar-nav-item${isActive ? ' active' : ''}`
          }
        >
          <i className="bi bi-person" />
          <span>마이페이지</span>
        </NavLink>
        <button className="sidebar-nav-item sidebar-nav-btn" onClick={handleLogout}>
          <i className="bi bi-box-arrow-right" />
          <span>로그아웃</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
