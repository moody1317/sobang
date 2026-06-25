import { Link } from 'react-router-dom';
import DashboardLayout from '../layouts/dashboardlayout';
import { useUser } from '../contexts/usercontext';
import './briefing.css';

const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };

const MOCK_PRIORITY = [
  { rank: 1, name: '중앙동', type: '구급', dispatch: 524, score: 88, level: '위험' },
  { rank: 2, name: '성안동', type: '구급', dispatch: 478, score: 84, level: '위험' },
  { rank: 3, name: '탑대성동', type: '화재', dispatch: 441, score: 81, level: '위험' },
];

const MOCK_DISTRIBUTION = [
  { label: '위험', cls: 'danger', count: 3, total: 15 },
  { label: '경계', cls: 'caution', count: 6, total: 15 },
  { label: '주의', cls: 'warning', count: 5, total: 15 },
  { label: '안전', cls: 'safe', count: 1, total: 15 },
];

const SCORE_LEVEL = '경계';

function formatDate() {
  const days = ['일', '월', '화', '수', '목', '금', '토'];
  const now = new Date();
  return `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${now.getDate()}일 (${days[now.getDay()]})`;
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return '좋은 아침입니다';
  if (h < 18) return '좋은 오후입니다';
  return '좋은 저녁입니다';
}

function ScoreBadge({ level, score }) {
  return (
    <span className={`score-badge score-badge--${LEVEL_CLASS[level] ?? ''}`}>
      {level} <strong>{score}</strong>
    </span>
  );
}

function Briefing() {
  const user = useUser();

  return (
    <div className="briefing">
      <div className="briefing-greeting-row">
        <div>
          <h1 className="briefing-greeting">
            {user?.name ?? '대원'}님, {getGreeting()}
          </h1>
          <p className="briefing-meta">{formatDate()}</p>
        </div>
        <Link to="/dashboard/map" className="btn-map">
          위험 지도 열기 <i className="bi bi-arrow-right" />
        </Link>
      </div>

      <div className="briefing-stat-cards">
        <div className="stat-card">
          <p className="stat-card-label">관할 평균 위험 스코어</p>
          <div className="stat-card-value">
            64 <span className="stat-card-unit">/100</span>
          </div>
          <div className="stat-card-footer">
            <span className={`level-chip level-chip--${LEVEL_CLASS[SCORE_LEVEL]}`}>
              {SCORE_LEVEL}
            </span>
            <span className="stat-card-change up">
              <i className="bi bi-caret-up-fill" /> 3.2 vs 지난달
            </span>
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">최고 위험 구역</p>
          <div className="stat-card-value">중앙동</div>
          <div className="stat-card-footer">
            <span className="level-chip level-chip--danger">위험 88</span>
            <span className="stat-card-note">구급 출동 집중</span>
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">오늘 점검 예정</p>
          <div className="stat-card-value">
            2 <span className="stat-card-unit">건</span>
          </div>
          <div className="stat-card-footer">
            <Link to="/dashboard/inspection" className="stat-card-link">
              점검 일지 보기 <i className="bi bi-arrow-right" />
            </Link>
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">위험 등급 구역</p>
          <div className="stat-card-value stat-card-value--danger">
            3 <span className="stat-card-unit">곳</span>
          </div>
          <div className="stat-card-footer">
            <span className="stat-card-note">전체 15개 행정구역 중</span>
          </div>
        </div>
      </div>

      <div className="briefing-panels">
        <div className="briefing-panel">
          <div className="panel-header">
            <h3 className="panel-title">오늘의 점검 우선순위</h3>
            <Link to="/dashboard/priority" className="panel-link">
              전체 보기 <i className="bi bi-arrow-right" />
            </Link>
          </div>
          <div className="priority-list">
            {MOCK_PRIORITY.map((item) => (
              <div key={item.rank} className="priority-item">
                <span className="priority-rank">{item.rank}</span>
                <div className="priority-info">
                  <span className="priority-name">{item.name}</span>
                  <span className="priority-meta">
                    주요 사고유형 · {item.type} · 연 {item.dispatch.toLocaleString()}건 출동
                  </span>
                </div>
                <ScoreBadge level={item.level} score={item.score} />
              </div>
            ))}
          </div>
        </div>

        <div className="briefing-panel">
          <h3 className="panel-title">관할 위험 등급 분포</h3>
          <div className="distribution-list">
            {MOCK_DISTRIBUTION.map((item) => (
              <div key={item.label} className="distribution-item">
                <div className="distribution-row">
                  <span className={`distribution-dot distribution-dot--${item.cls}`} />
                  <span className="distribution-label">{item.label}</span>
                  <span className="distribution-count">{item.count}곳</span>
                </div>
                <div className="distribution-bar-track">
                  <div
                    className={`distribution-bar-fill distribution-bar-fill--${item.cls}`}
                    style={{ width: `${(item.count / item.total) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <p className="distribution-note">
            <i className="bi bi-exclamation-triangle" /> 위험 등급{' '}
            <strong>3개 구역</strong>은 우선 순찰·점검 대상입니다.
          </p>
        </div>
      </div>
    </div>
  );
}

function BriefingPage() {
  return (
    <DashboardLayout>
      <Briefing />
    </DashboardLayout>
  );
}

export default BriefingPage;
