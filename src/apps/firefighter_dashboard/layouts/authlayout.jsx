import './authlayout.css';

function AuthLayout({ children }) {
  return (
    <div className="auth-layout">
      <div className="auth-panel-left">
        <div className="auth-left-header">
          <div className="auth-logo-icon">
            <i className="bi bi-fire" />
          </div>
          <span className="auth-logo-text">화재 위험 관제 플랫폼</span>
        </div>

        <div className="auth-left-content">
          <p className="auth-left-eyebrow">출동 데이터 기반 위험 스코어 시스템</p>
          <h1 className="auth-left-heading">
            관할 구역의 위험을<br />한눈에 파악하세요
          </h1>
          <p className="auth-left-description">
            화재·구급·구조 출동 데이터를 통합한 단일 위험 스코어로 점검과
            순찰의 우선순위를 정합니다.
          </p>
        </div>

        <div className="auth-left-stats">
          <div className="auth-stat">
            <span className="auth-stat-value">15</span>
            <span className="auth-stat-label">관할 행정구역</span>
          </div>
          <div className="auth-stat">
            <span className="auth-stat-value">4,623</span>
            <span className="auth-stat-label">누적 출동 데이터</span>
          </div>
          <div className="auth-stat">
            <span className="auth-stat-value">실시간</span>
            <span className="auth-stat-label">스코어 갱신</span>
          </div>
        </div>

        <div className="auth-deco auth-deco-1" />
        <div className="auth-deco auth-deco-2" />
      </div>

      <div className="auth-panel-right">
        {children}
      </div>
    </div>
  );
}

export default AuthLayout;