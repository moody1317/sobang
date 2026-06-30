import { useLocation, NavLink } from 'react-router-dom';
import { useUser } from '../contexts/usercontext';
import { useAlertCount } from '../contexts/alertcontext';
import './header.css';

const PAGE_LABELS = {
  '/dashboard': '브리핑 홈',
  '/dashboard/map': '위험 스코어 지도',
  '/dashboard/priority': '점검 우선순위',
  '/dashboard/stats': '통계',
  '/dashboard/inspection': '점검 일지',
  '/dashboard/schedule': '근무 일정',
  '/dashboard/alerts': '알림 센터',
  '/dashboard/data': '데이터·방법론',
  '/dashboard/admin': '관리자',
  '/dashboard/profile': '마이페이지',
};

const PAGE_SUB = {
  '/dashboard': '교대 시작 전 관할 위험 현황을 확인하세요',
  '/dashboard/map': '행정구역별 통합 위험 스코어',
  '/dashboard/priority': '위험 스코어 기반 점검 대상 정렬',
  '/dashboard/stats': '출동·위험 데이터 분석',
  '/dashboard/inspection': '현장 점검 기록 및 이력',
  '/dashboard/schedule': '교대·순찰 일정과 출동 기록',
  '/dashboard/alerts': '위험도 변동 및 특보 알림',
  '/dashboard/data': '위험 스코어 산출 근거와 출처',
  '/dashboard/admin': '소방서 코드 및 대원 승인 관리',
  '/dashboard/profile': '계정 및 환경 설정',
}

function Header() {
  const user = useUser();
  const { pathname } = useLocation();
  const unreadCount = useAlertCount();
  const initial = user?.name?.[0] ?? '';
  const pageLabel = PAGE_LABELS[pathname] ?? '';
  const pageSub = PAGE_SUB[pathname] ?? '';

  return (
    <header className="dashboard-header">
      <div className='header-left'>
        <span className="header-page-title">{pageLabel}</span> <br/>
        <span className='header-page-subtitle'>{pageSub}</span>
      </div>

      <div className="header-right">
        <div className="header-search">
          <i className="bi bi-search header-search-icon" />
          <input
            type="text"
            className="header-search-input"
            placeholder="구역·건물·주소 검색"
          />
        </div>

        <NavLink to="/dashboard/alerts" className="header-icon-btn header-bell-wrap" aria-label="알림">
          <i className="bi bi-bell" />
          {unreadCount > 0 && <span className="header-bell-dot" />}
        </NavLink>

        <NavLink to="/dashboard/profile" className="header-user">
          <div className="header-avatar">{initial}</div>
          {user && (
            <div className="header-user-info">
              <span className="header-user-name">{user.name}</span>
              <span className="header-user-role">
                {user.rank}
              </span>
            </div>
          )}
        </NavLink>
      </div>
    </header>
  );
}

export default Header;
