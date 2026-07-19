import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { updateIncidentStatus, confirmDispatch } from '../../../api/incidents';
import './dispatch.css';

const AUTO_START_SECONDS = 38;
const AVERAGE_PATROL_SPEED_KMH = 30; // 실도로 경로 계산 전 대략적인 예상 소요시간 산출용

const INCIDENT_ICON = {
  화재: 'bi-fire',
  구조: 'bi-life-preserver',
  구급: 'bi-heart-pulse-fill',
  위험물: 'bi-exclamation-triangle-fill',
  기타: 'bi-question-circle-fill',
};

function getDistanceKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function PatrolDispatch() {
  const [secondsLeft, setSecondsLeft] = useState(AUTO_START_SECONDS);
  const [distanceKm, setDistanceKm] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const incident = location.state?.incident;
  const vehicles = incident?.vehicles ?? [];

  useEffect(() => {
    if (!incident) {
      navigate('/firefighter_patrol');
      return;
    }
    if (incident.latitude == null || incident.longitude == null) return;

    navigator.geolocation.getCurrentPosition((position) => {
      setDistanceKm(
        getDistanceKm(position.coords.latitude, position.coords.longitude, incident.latitude, incident.longitude)
      );
    });
  }, [incident, navigate]);

  function handleDispatch() {
    updateIncidentStatus(incident.id, '출동중').catch(() => {});
    confirmDispatch(incident.id).catch(() => {});
    navigate('/firefighter_patrol/navigation', { state: { incident } });
  }

  useEffect(() => {
    if (!incident) return;

    if (secondsLeft <= 0) {
      handleDispatch();
      return;
    }

    const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [secondsLeft, incident]);

  if (!incident) return null;

  return (
    <PatrolLayout>
      <div className="patrol-dispatch">
        <div className="patrol-dispatch-badge">
          <i className="bi bi-bell-fill" />
          <span>긴급 출동 지령</span>
        </div>

        <div className="patrol-dispatch-icon-wrap">
          <i className={`bi ${INCIDENT_ICON[incident.incident_type] ?? 'bi-exclamation-triangle-fill'} patrol-dispatch-icon`} />
        </div>

        <h2 className="patrol-dispatch-title">{incident.incident_type}</h2>

        <div className="patrol-dispatch-location">
          <span className="patrol-dispatch-location-name">
            <i className="bi bi-geo-alt-fill" /> {incident.dong_name}
          </span>
          <span className="patrol-dispatch-location-sub">{incident.address}</span>
        </div>

        <div className="patrol-dispatch-vehicles">
          <span className="patrol-dispatch-vehicles-label">
            <i className="bi bi-truck" /> 배정 차량
          </span>
          {vehicles.length === 0 ? (
            <span className="patrol-dispatch-vehicles-empty">배정된 차량이 없습니다</span>
          ) : (
            <div className="patrol-dispatch-vehicles-list">
              {vehicles.map((v) => (
                <span key={v.id} className="patrol-dispatch-vehicle-chip">{v.vehicle_type}</span>
              ))}
            </div>
          )}
        </div>

        <div className="patrol-dispatch-stats">
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">
              {distanceKm !== null ? `${distanceKm.toFixed(1)}km` : '-'}
            </span>
            <span className="patrol-dispatch-stat-label">현재 위치에서 직선거리</span>
          </div>
          <div className="patrol-dispatch-stat-divider" />
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">
              {distanceKm !== null ? `약 ${Math.max(1, Math.round((distanceKm / AVERAGE_PATROL_SPEED_KMH) * 60))}분` : '-'}
            </span>
            <span className="patrol-dispatch-stat-label">예상 소요 (실도로 경로는 다음 화면에서 확인)</span>
          </div>
        </div>

        <div className="patrol-dispatch-countdown">
          <div className="patrol-dispatch-countdown-circle">{secondsLeft}</div>
          <span className="patrol-dispatch-countdown-text">
            {secondsLeft}초 후 자동으로 경로 안내가 시작됩니다
          </span>
        </div>

        <button className="patrol-dispatch-btn" onClick={handleDispatch}>
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
