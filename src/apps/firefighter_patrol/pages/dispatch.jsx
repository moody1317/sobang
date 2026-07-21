import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { updateIncidentStatus, confirmDispatch } from '../../../api/incidents';
import { getRoute } from '../../../api/navigation';
import { loadKakaoMap } from '../utils/loadKakaoMap';
import { searchNearbyPlaces } from '../utils/nearbyPlaces';
import './dispatch.css';

const AUTO_START_SECONDS = 38;
const NEARBY_SEARCH_RADIUS_M = 1000;

const INCIDENT_ICON = {
  화재: 'bi-fire',
  구조: 'bi-life-preserver',
  구급: 'bi-heart-pulse-fill',
  위험물: 'bi-exclamation-triangle-fill',
  기타: 'bi-question-circle-fill',
};

function PatrolDispatch() {
  const [secondsLeft, setSecondsLeft] = useState(AUTO_START_SECONDS);
  const [route, setRoute] = useState(null);
  const [nearbyPlaces, setNearbyPlaces] = useState([]);
  const [nearbyStatus, setNearbyStatus] = useState('idle'); // idle | loading | ready | error
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

    navigator.geolocation.getCurrentPosition(
      (position) => {
        getRoute(position.coords.latitude, position.coords.longitude, incident.latitude, incident.longitude)
          .then((data) => {
            setRoute({ distanceKm: data.distance_m / 1000, durationMin: Math.round(data.duration_s / 60) });
          })
          .catch(() => {});
      },
      undefined,
      { timeout: 10000, maximumAge: 60000 }
    );
  }, [incident, navigate]);

  useEffect(() => {
    if (!incident || incident.latitude == null || incident.longitude == null) return;

    let cancelled = false;
    Promise.resolve().then(() => { if (!cancelled) setNearbyStatus('loading'); });

    loadKakaoMap()
      .then((kakao) => {
        if (cancelled) return null;
        const position = new kakao.maps.LatLng(incident.latitude, incident.longitude);
        return searchNearbyPlaces(kakao, position, NEARBY_SEARCH_RADIUS_M);
      })
      .then((results) => {
        if (cancelled || !results) return;
        setNearbyPlaces(results.filter((p) => p.count > 0));
        setNearbyStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setNearbyStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [incident]);

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
                <span key={v.id} className="patrol-dispatch-vehicle-chip">
                  {v.vehicle_type}{v.reason ? ` (${v.reason})` : ''}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="patrol-dispatch-vehicles">
          <span className="patrol-dispatch-vehicles-label">
            <i className="bi bi-geo" /> 신고지 주변 시설 (반경 {NEARBY_SEARCH_RADIUS_M}m)
          </span>
          {nearbyStatus === 'loading' && (
            <span className="patrol-dispatch-vehicles-empty">주변 시설 조회 중…</span>
          )}
          {nearbyStatus === 'error' && (
            <span className="patrol-dispatch-vehicles-empty">주변 시설 정보를 불러오지 못했습니다</span>
          )}
          {nearbyStatus === 'ready' && nearbyPlaces.length === 0 && (
            <span className="patrol-dispatch-vehicles-empty">주변에 특이 시설이 없습니다</span>
          )}
          {nearbyStatus === 'ready' && nearbyPlaces.length > 0 && (
            <div className="patrol-dispatch-vehicles-list">
              {nearbyPlaces.map((p) => (
                <span key={p.code} className="patrol-dispatch-vehicle-chip">{p.label} {p.count}</span>
              ))}
            </div>
          )}
        </div>

        <div className="patrol-dispatch-stats">
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">
              {route ? `${route.distanceKm.toFixed(1)}km` : '-'}
            </span>
            <span className="patrol-dispatch-stat-label">현재 위치에서 실주행거리</span>
          </div>
          <div className="patrol-dispatch-stat-divider" />
          <div className="patrol-dispatch-stat">
            <span className="patrol-dispatch-stat-value">
              {route ? `약 ${route.durationMin}분` : '-'}
            </span>
            <span className="patrol-dispatch-stat-label">예상 소요</span>
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
