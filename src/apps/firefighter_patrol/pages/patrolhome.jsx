import { useEffect, useRef } from 'react';
import PatrolLayout from '../layouts/patrollayout';
import { loadKakaoMap } from '../utils/loadKakaoMap';
import { RISK_ZONES } from '../data/riskZones';
import './patrolhome.css';

const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };

function PatrolHome() {
  const mapContainerRef = useRef(null);

  useEffect(() => {
    let watchId;

    loadKakaoMap().then((kakao) => {
      const map = new kakao.maps.Map(mapContainerRef.current, {
        center: new kakao.maps.LatLng(36.6395, 127.4897),
        level: 6,
      });

      RISK_ZONES.forEach((zone) => {
        const marker = new kakao.maps.Marker({
          position: new kakao.maps.LatLng(zone.lat, zone.lng),
          map,
        });

        const infoWindow = new kakao.maps.InfoWindow({
          content: `<div class="patrol-map-infowindow">${zone.type} · ${zone.name}</div>`,
        });

        kakao.maps.event.addListener(marker, 'click', () => {
          infoWindow.open(map, marker);
        });
      });

      if (!navigator.geolocation) return;

      const currentMarker = new kakao.maps.Marker({
        position: map.getCenter(),
        map,
        zIndex: 10,
      });

      watchId = navigator.geolocation.watchPosition((position) => {
        const currentPos = new kakao.maps.LatLng(
          position.coords.latitude,
          position.coords.longitude
        );
        currentMarker.setPosition(currentPos);
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
