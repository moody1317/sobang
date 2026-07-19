import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { loadKakaoMap } from '../utils/loadKakaoMap';
import { getRoute } from '../../../api/navigation';
import { updateIncidentStatus } from '../../../api/incidents';
import '../style/markers.css';
import './navigation.css';

const ARRIVAL_THRESHOLD_METERS = 100;
const GUIDE_ADVANCE_THRESHOLD_METERS = 30;
const FOLLOW_ZOOM_LEVEL = 4;

function getDistanceMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function PatrolNavigation() {
  const mapContainerRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();
  const incident = location.state?.incident;
  const [arrived, setArrived] = useState(false);
  const [route, setRoute] = useState(null);
  const [eta, setEta] = useState(null);
  const [guideIndex, setGuideIndex] = useState(1);

  useEffect(() => {
    if (!incident || incident.latitude == null || incident.longitude == null) {
      navigate('/firefighter_patrol');
      return;
    }

    let watchId;
    let arrivedNotified = false;
    const guidesRef = { current: [] };
    const guideIndexRef = { current: 1 };
    const followingRef = { current: false };

    loadKakaoMap().then((kakao) => {
      const destPos = new kakao.maps.LatLng(incident.latitude, incident.longitude);

      const map = new kakao.maps.Map(mapContainerRef.current, {
        center: destPos,
        level: 5,
      });

      const destEl = document.createElement('div');
      destEl.className = 'patrol-marker patrol-marker--danger';
      destEl.innerHTML = '<i class="bi bi-building"></i>';
      new kakao.maps.CustomOverlay({ position: destPos, content: destEl, xAnchor: 0.5, yAnchor: 0.5, map });

      const currentEl = document.createElement('div');
      currentEl.className = 'patrol-marker patrol-marker--me';
      const currentOverlay = new kakao.maps.CustomOverlay({
        position: destPos,
        content: currentEl,
        xAnchor: 0.5,
        yAnchor: 0.5,
        zIndex: 10,
        map,
      });

      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;

        getRoute(latitude, longitude, incident.latitude, incident.longitude).then((data) => {
          setRoute(data);
          setEta(new Date(Date.now() + data.duration_s * 1000));
          guidesRef.current = data.guides;

          const path = data.path.map((p) => new kakao.maps.LatLng(p.lat, p.lng));
          const polyline = new kakao.maps.Polyline({
            path,
            strokeWeight: 5,
            strokeColor: '#B5333D',
            strokeOpacity: 0.9,
          });
          polyline.setMap(map);

          const currentPos = new kakao.maps.LatLng(latitude, longitude);
          map.setLevel(FOLLOW_ZOOM_LEVEL);
          map.setCenter(currentPos);
          followingRef.current = true;
        });
      });

      if (!navigator.geolocation) return;

      watchId = navigator.geolocation.watchPosition((position) => {
        const { latitude, longitude } = position.coords;
        const currentPos = new kakao.maps.LatLng(latitude, longitude);
        currentOverlay.setPosition(currentPos);

        if (followingRef.current) {
          map.setLevel(FOLLOW_ZOOM_LEVEL);
          map.panTo(currentPos);
        }

        const guides = guidesRef.current;
        const nextGuide = guides[guideIndexRef.current];
        if (
          nextGuide &&
          guideIndexRef.current < guides.length - 1 &&
          getDistanceMeters(latitude, longitude, nextGuide.lat, nextGuide.lng) <= GUIDE_ADVANCE_THRESHOLD_METERS
        ) {
          guideIndexRef.current += 1;
          setGuideIndex(guideIndexRef.current);
        }

        if (
          !arrivedNotified &&
          getDistanceMeters(latitude, longitude, incident.latitude, incident.longitude) <= ARRIVAL_THRESHOLD_METERS
        ) {
          arrivedNotified = true;
          setArrived(true);
          updateIncidentStatus(incident.id, '현장도착').catch(() => {});
        }
      });
    });

    return () => {
      if (watchId !== undefined) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, [incident, navigate]);

  if (!incident) return null;

  const currentGuide = route?.guides?.[guideIndex];

  return (
    <PatrolLayout>
      <div className="patrol-nav">
        <div className="patrol-nav-banner">
          <i className={`bi ${arrived ? 'bi-check-circle-fill' : 'bi-arrow-up-circle-fill'}`} />
          <span className="patrol-nav-banner-text">
            {arrived ? '현장 도착' : currentGuide?.name ?? '경로 탐색 중...'}
          </span>
        </div>

        <div ref={mapContainerRef} className="patrol-nav-map" />

        <div className="patrol-nav-card">
          <div className="patrol-nav-card-head">
            <i className="bi bi-building patrol-nav-card-icon" />
            <div>
              <span className="patrol-nav-card-title">{incident.incident_type} 출동</span>
              <span className="patrol-nav-card-sub">{incident.dong_name} · 관할 내</span>
            </div>
          </div>

          <div className="patrol-nav-stats">
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">
                {route ? `약 ${Math.round(route.duration_s / 60)}분` : '-'}
              </span>
              <span className="patrol-nav-stat-label">예상 소요</span>
            </div>
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">
                {route ? `${(route.distance_m / 1000).toFixed(1)}km` : '-'}
              </span>
              <span className="patrol-nav-stat-label">남은 거리</span>
            </div>
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">
                {eta ? `${String(eta.getHours()).padStart(2, '0')}:${String(eta.getMinutes()).padStart(2, '0')}` : '-'}
              </span>
              <span className="patrol-nav-stat-label">도착 예정</span>
            </div>
          </div>

          <div className={`patrol-nav-actions${arrived ? '' : ' patrol-nav-actions--single'}`}>
            {arrived ? (
              <>
                <button
                  className="patrol-nav-btn patrol-nav-btn--ghost"
                  onClick={() => navigate('/firefighter_patrol/return', { state: { incident, isFalseAlarm: true } })}
                >
                  허위 신고
                </button>
                <button
                  className="patrol-nav-btn patrol-nav-btn--primary"
                  onClick={() => navigate('/firefighter_patrol/return', { state: { incident, isFalseAlarm: false } })}
                >
                  출동 종료
                </button>
              </>
            ) : (
              <button
                className="patrol-nav-btn patrol-nav-btn--ghost"
                onClick={() => navigate('/firefighter_patrol/return', { state: { incident, isFalseAlarm: false } })}
              >
                순찰 복귀
              </button>
            )}
          </div>
        </div>
      </div>
    </PatrolLayout>
  );
}

export default PatrolNavigation;
