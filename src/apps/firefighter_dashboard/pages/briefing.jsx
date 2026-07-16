import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../layouts/dashboardlayout';
import { useUser } from '../contexts/usercontext';
import { getRiskMapDongs } from '../../../api/riskMap';
import { getMySchedule } from '../../../api/schedule';
import { LEVEL_CLASS, LEVEL_BY_KEY, resolveLevel, topBreakdownLabel } from '../utils/riskScore';
import './briefing.css';

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
  const [dongs, setDongs] = useState([]);
  const [status, setStatus] = useState('loading'); // loading | ready | error
  const [todayEducation, setTodayEducation] = useState(undefined); // undefined=loading, null=없음, string=제목

  useEffect(() => {
    let cancelled = false;

    getRiskMapDongs()
      .then((data) => {
        if (cancelled) return;
        setDongs(data);
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const today = new Date();
    const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    getMySchedule(today.getFullYear(), today.getMonth() + 1)
      .then((items) => {
        if (cancelled) return;
        const match = items.find((s) => s.date === todayKey && s.is_education);
        setTodayEducation(match?.title ?? null);
      })
      .catch(() => {
        if (!cancelled) setTodayEducation(null);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const rankedByScore = useMemo(
    () => [...dongs].sort((a, b) => b.risk_score - a.risk_score),
    [dongs]
  );

  const avgScore = useMemo(() => {
    if (dongs.length === 0) return null;
    const sum = dongs.reduce((acc, d) => acc + Number(d.risk_score), 0);
    return Math.round((sum / dongs.length) * 10) / 10;
  }, [dongs]);

  const levelCounts = useMemo(() => {
    const counts = { danger: 0, caution: 0, warning: 0, safe: 0 };
    dongs.forEach((d) => {
      counts[resolveLevel(Number(d.risk_score))] += 1;
    });
    return counts;
  }, [dongs, resolveLevel]);

  const topDong = rankedByScore[0] ?? null;
  const avgLevel = avgScore == null ? null : LEVEL_BY_KEY[resolveLevel(avgScore)];
  const topDongLevel = topDong ? LEVEL_BY_KEY[resolveLevel(Number(topDong.risk_score))] : null;

  const priorityTop3 = rankedByScore.slice(0, 3).map((d, i) => ({
    rank: i + 1,
    name: d.dong_nm,
    score: Math.round(Number(d.risk_score) * 10) / 10,
    level: LEVEL_BY_KEY[resolveLevel(Number(d.risk_score))],
    mainFactor: topBreakdownLabel(d.risk_score_breakdown),
  }));

  const distribution = [
    { label: '위험', cls: 'danger', count: levelCounts.danger, total: dongs.length },
    { label: '경계', cls: 'caution', count: levelCounts.caution, total: dongs.length },
    { label: '주의', cls: 'warning', count: levelCounts.warning, total: dongs.length },
    { label: '안전', cls: 'safe', count: levelCounts.safe, total: dongs.length },
  ];

  const isLoading = status === 'loading';

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
            {isLoading ? '—' : avgScore} <span className="stat-card-unit">/100</span>
          </div>
          <div className="stat-card-footer">
            {avgLevel && (
              <span className={`level-chip level-chip--${LEVEL_CLASS[avgLevel]}`}>{avgLevel}</span>
            )}
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">최고 위험 구역</p>
          <div className="stat-card-value">{isLoading ? '—' : topDong?.dong_nm ?? '-'}</div>
          <div className="stat-card-footer">
            {topDong && (
              <span className={`level-chip level-chip--${LEVEL_CLASS[topDongLevel]}`}>
                {topDongLevel} {Math.round(Number(topDong.risk_score) * 10) / 10}
              </span>
            )}
            {topDong && (
              <span className="stat-card-note">
                주요 요인 · {topBreakdownLabel(topDong.risk_score_breakdown) ?? '-'}
              </span>
            )}
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">오늘 예정 교육</p>
          <div className="stat-card-value stat-card-value--edu">
            {todayEducation === undefined ? '—' : todayEducation ?? '없음'}
          </div>
          <div className="stat-card-footer">
            <Link to="/dashboard/schedule" className="stat-card-link">
              근무 일정 보기 <i className="bi bi-arrow-right" />
            </Link>
          </div>
        </div>

        <div className="stat-card">
          <p className="stat-card-label">위험 등급 구역</p>
          <div className="stat-card-value stat-card-value--danger">
            {isLoading ? '—' : levelCounts.danger} <span className="stat-card-unit">곳</span>
          </div>
          <div className="stat-card-footer">
            <span className="stat-card-note">전체 {dongs.length}개 행정구역 중</span>
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
            {priorityTop3.map((item) => (
              <div key={item.rank} className="priority-item">
                <span className="priority-rank">{item.rank}</span>
                <div className="priority-info">
                  <span className="priority-name">{item.name}</span>
                  <span className="priority-meta">주요 위험요인 · {item.mainFactor ?? '-'}</span>
                </div>
                <ScoreBadge level={item.level} score={item.score} />
              </div>
            ))}
            {!isLoading && priorityTop3.length === 0 && (
              <p className="distribution-note">표시할 관할동 데이터가 없습니다.</p>
            )}
          </div>
        </div>

        <div className="briefing-panel">
          <h3 className="panel-title">관할 위험 등급 분포</h3>
          <div className="distribution-list">
            {distribution.map((item) => (
              <div key={item.label} className="distribution-item">
                <div className="distribution-row">
                  <span className={`distribution-dot distribution-dot--${item.cls}`} />
                  <span className="distribution-label">{item.label}</span>
                  <span className="distribution-count">{item.count}곳</span>
                </div>
                <div className="distribution-bar-track">
                  <div
                    className={`distribution-bar-fill distribution-bar-fill--${item.cls}`}
                    style={{ width: item.total ? `${(item.count / item.total) * 100}%` : '0%' }}
                  />
                </div>
              </div>
            ))}
          </div>
          <p className="distribution-note">
            <i className="bi bi-exclamation-triangle" /> 위험 등급{' '}
            <strong>{levelCounts.danger}개 구역</strong>은 우선 순찰·점검 대상입니다.
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