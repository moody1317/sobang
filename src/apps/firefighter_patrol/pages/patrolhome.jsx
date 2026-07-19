import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { loadKakaoMap } from '../utils/loadKakaoMap';
import { RISK_ZONES } from '../data/riskZones';
import { useUser } from '../../firefighter_dashboard/contexts/userHooks';
import { getActiveIncidents } from '../../../api/incidents';
import '../style/markers.css';
import './patrolhome.css';

const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };

const ZONE_ICON = {
  침수: 'bi-droplet-fill',
  화재취약: 'bi-fire',
  건물붕괴: 'bi-building',
  산불: 'bi-fire',
  산사태: 'bi-exclamation-octagon-fill',
};

const INCIDENT_POLL_INTERVAL_MS = 5000;

function createZoneMarkerElement(zone) {
  const el = document.createElement('div');
  el.className = `patrol-marker patrol-marker--${LEVEL_CLASS[zone.level] ?? ''}`;
  el.innerHTML = `<i class="bi ${ZONE_ICON[zone.type] ?? 'bi-exclamation-triangle-fill'}"></i>`;
  return el;
}

function PatrolHome() {
  const mapContainerRef = useRef(null);
  const navigate = useNavigate();
  const user = useUser();

  useEffect(() => {
    if (!user?.station_id) return;

    const interval = setInterval(async () => {
      try {
        const incidents = await getActiveIncidents();
        const newIncident = incidents
          .filter((i) => i.station_id === user.station_id && i.status === '신고접수')
          .sort((a, b) => new Date(a.reported_at) - new Date(b.reported_at))[0];

        if (newIncident) {
          navigate('/firefighter_patrol/dispatch', { state: { incident: newIncident } });
        }
      } catch {
        // 폴링 실패는 조용히 다음 주기에 재시도
      }
    }, INCIDENT_POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [user, navigate]);

  useEffect(() => {
    let watchId;

    loadKakaoMap().then((kakao) => {
      const map = new kakao.maps.Map(mapContainerRef.current, {
        center: new kakao.maps.LatLng(36.6395, 127.4897),
        level: 3,
      });

      RISK_ZONES.forEach((zone) => {
        const position = new kakao.maps.LatLng(zone.lat, zone.lng);
        const markerEl = createZoneMarkerElement(zone);

        new kakao.maps.CustomOverlay({
          position,
          content: markerEl,
          xAnchor: 0.5,
          yAnchor: 0.5,
          map,
        });

        const infoWindow = new kakao.maps.InfoWindow({
          position,
          content: `<div class="patrol-map-infowindow">${zone.type} · ${zone.name}</div>`,
        });

        markerEl.addEventListener('click', () => {
          infoWindow.open(map);
        });
      });

      if (!navigator.geolocation) return;

      const currentMarkerEl = document.createElement('div');
      currentMarkerEl.className = 'patrol-marker patrol-marker--me';

      const currentOverlay = new kakao.maps.CustomOverlay({
        position: map.getCenter(),
        content: currentMarkerEl,
        xAnchor: 0.5,
        yAnchor: 0.5,
        zIndex: 10,
        map,
      });

      watchId = navigator.geolocation.watchPosition((position) => {
        const currentPos = new kakao.maps.LatLng(
          position.coords.latitude,
          position.coords.longitude
        );
        currentOverlay.setPosition(currentPos);
        map.setCenter(currentPos);
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
      <div className="patrol-home">
        <div ref={mapContainerRef} className="patrol-map" />

        <div className="patrol-zone-list">
          {RISK_ZONES.map((zone) => (
            <div key={zone.id} className="patrol-zone-item">
              <span className={`patrol-zone-badge patrol-zone-badge--${LEVEL_CLASS[zone.level] ?? ''}`}>
                {zone.level}
              </span>
              <span className="patrol-zone-type">{zone.type}</span>
              <span className="patrol-zone-name">{zone.name}</span>
            </div>
          ))}
        </div>
      </div>
    </PatrolLayout>
  );
}

export default PatrolHome;
