import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { RISK_ZONES } from '../data/riskZones';
import './dispatch.css';

const DESTINATION = RISK_ZONES.find((zone) => zone.type === '건물붕괴');
const AUTO_START_SECONDS = 38;

function PatrolDispatch() {
  const [secondsLeft, setSecondsLeft] = useState(AUTO_START_SECONDS);
  const navigate = useNavigate();

  useEffect(() => {
    if (secondsLeft <= 0) {
      navigate('/firefighter_patrol/navigation');
      return;
    }

    const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [secondsLeft, navigate]);

  return (
    <PatrolLayout>
      <div className="patrol-dispatch">
        <div className="patrol-dispatch-badge">
          <i className="bi bi-bell-fill" />
          <span>긴급 출동 지령</span>
        </div>

        <div className="patrol-dispatch-icon-wrap">
          <i className="bi bi-building patrol-dispatch-icon" />
        </div>

        <h2 className="patrol-dispatch-title">{DESTINATION.type}</h2>

        <div className="patrol-dispatch-location">
          <span className="patrol-dispatch-location-name">
            <i className="bi bi-geo-alt-fill" /> {DESTINATION.name}
          </span>
          <span className="patrol-dispatch-location-sub">관할 중앙119안전센터 · 출동코드 C3</span>
        </div>

        <div className="patrol-dispatch-stats">
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">1.8km</span>
            <span className="patrol-dispatch-stat-label">현재 위치에서</span>
          </div>
          <div className="patrol-dispatch-stat-divider" />
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">약 4분</span>
            <span className="patrol-dispatch-stat-label">예상 도착</span>
          </div>
        </div>

        <div className="patrol-dispatch-countdown">
          <div className="patrol-dispatch-countdown-circle">{secondsLeft}</div>
          <span className="patrol-dispatch-countdown-text">
            {secondsLeft}초 후 자동으로 경로 안내가 시작됩니다
          </span>
        </div>

        <button
          className="patrol-dispatch-btn"
          onClick={() => navigate('/firefighter_patrol/navigation')}
        >
          <i className="bi bi-arrow-right" /> 즉시 출동 · 경로 안내
        </button>

        <button
          className="patrol-dispatch-hold-btn"
          onClick={() => navigate('/firefighter_patrol')}
        >
          지령 보류
        </button>
      </div>
    </PatrolLayout>
  );
}

export default PatrolDispatch;
