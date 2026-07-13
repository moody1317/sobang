import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { loadKakaoMap } from '../utils/loadKakaoMap';
import { RISK_ZONES } from '../data/riskZones';
import './navigation.css';

const DESTINATION = RISK_ZONES.find((zone) => zone.type === '건물붕괴');
const ARRIVAL_THRESHOLD_METERS = 100;

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
  const [arrived, setArrived] = useState(false);

  useEffect(() => {
    let watchId;

    loadKakaoMap().then((kakao) => {
      const destPos = new kakao.maps.LatLng(DESTINATION.lat, DESTINATION.lng);

      const map = new kakao.maps.Map(mapContainerRef.current, {
        center: destPos,
        level: 5,
      });

      new kakao.maps.Marker({ position: destPos, map });

      const currentMarker = new kakao.maps.Marker({
        position: map.getCenter(),
        map,
        zIndex: 10,
      });

      const polyline = new kakao.maps.Polyline({
        path: [map.getCenter(), destPos],
        strokeWeight: 5,
        strokeColor: '#B5333D',
        strokeOpacity: 0.9,
      });
      polyline.setMap(map);

      if (!navigator.geolocation) return;

      watchId = navigator.geolocation.watchPosition((position) => {
        const { latitude, longitude } = position.coords;
        const currentPos = new kakao.maps.LatLng(latitude, longitude);
        currentMarker.setPosition(currentPos);
        polyline.setPath([currentPos, destPos]);

        if (getDistanceMeters(latitude, longitude, DESTINATION.lat, DESTINATION.lng) <= ARRIVAL_THRESHOLD_METERS) {
          setArrived(true);
        }
      });
    });

    return () => {
      if (watchId !== undefined) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, []);

  return (
    <PatrolLayout>
      <div className="patrol-nav">
        <div className="patrol-nav-banner">
          <i className={`bi ${arrived ? 'bi-check-circle-fill' : 'bi-arrow-up-circle-fill'}`} />
          <span className="patrol-nav-banner-text">
            {arrived ? '현장 도착' : `${DESTINATION.name} 방면 직진`}
          </span>
        </div>

        <div ref={mapContainerRef} className="patrol-nav-map" />

        <div className="patrol-nav-card">
          <div className="patrol-nav-card-head">
            <i className="bi bi-building patrol-nav-card-icon" />
            <div>
              <span className="patrol-nav-card-title">{DESTINATION.type} 출동</span>
              <span className="patrol-nav-card-sub">{DESTINATION.name} · 관할 내</span>
            </div>
          </div>

          <div className="patrol-nav-stats">
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">약 4분</span>
              <span className="patrol-nav-stat-label">예상 소요</span>
            </div>
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">1.5km</span>
              <span className="patrol-nav-stat-label">남은 거리</span>
            </div>
            <div className="patrol-nav-stat">
              <span className="patrol-nav-stat-value">14:32</span>
              <span className="patrol-nav-stat-label">도착 예정</span>
            </div>
          </div>

          <div className={`patrol-nav-actions${arrived ? '' : ' patrol-nav-actions--single'}`}>
            <button className="patrol-nav-btn patrol-nav-btn--ghost" onClick={() => navigate('/firefighter_patrol')}>
              순찰 복귀
            </button>
            {arrived && (
              <span className="patrol-nav-arrived-badge">
                <i className="bi bi-check-circle-fill" /> 도착 확인됨
              </span>
            )}
          </div>
        </div>
      </div>
    </PatrolLayout>
  );
}

export default PatrolNavigation;
