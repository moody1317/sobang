import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import DashboardLayout from '../layouts/dashboardlayout';
import InspectionAddModal from './inspectionAdd';
import { loadKakaoMap } from '../../firefighter_patrol/utils/loadKakaoMap';
import { getRiskMapDongs } from '../../../api/riskMap';
import { LEVEL_CLASS, LEVEL_BY_KEY, BREAKDOWN_LABELS, resolveLevel } from '../utils/riskScore';
import './danger.css';

const ACCIDENT_TYPES = ['전체', '화재', '구급'];
const PERIODS = ['최근 1년', '최근 3년', '전체'];

function dongToRegion(dong, levelKey, rank, total) {
  return {
    admin_code: dong.admin_code,
    name: dong.dong_nm,
    type: '',
    level: LEVEL_BY_KEY[levelKey] ?? '안전',
    score: Math.round(Number(dong.risk_score) * 10) / 10,
    rank,
    total,
    breakdown: dong.risk_score_breakdown ?? {},
  };
}

function RegionPanel({ region }) {
  const [showModal, setShowModal] = useState(false);
  const levelCls = LEVEL_CLASS[region.level] ?? 'safe';

  const breakdownRows = useMemo(() => {
    return Object.entries(region.breakdown)
      .map(([key, value]) => ({ key, label: BREAKDOWN_LABELS[key] ?? key, value: Number(value) }))
      .sort((a, b) => b.value - a.value);
  }, [region.breakdown]);

  return (
    <div className="danger-panel">
      <div className="danger-panel-header">
        <div className="danger-panel-name-row">
          <span className="danger-panel-name">{region.name}</span>
          <span className="danger-panel-type">{region.type}</span>
        </div>
        <span className={`danger-level-badge danger-level-badge--${levelCls}`}>{region.level}</span>
      </div>

      <div className="danger-score-row">
        <span className={`danger-score danger-score--${levelCls}`}>{region.score}</span>
        <div className="danger-rank">
          <span className="danger-rank-label">관할 내 위험 순위</span>
          <span className="danger-rank-value">{region.rank}위 / {region.total}개 구역</span>
        </div>
      </div>

      <div className="danger-divider" />

      <div className="danger-section">
        <div className="danger-section-title">스코어 세부 근거</div>
        <div className="danger-breakdown">
          {breakdownRows.map((row) => (
            <div key={row.key} className="danger-breakdown-row">
              <span className="danger-breakdown-label">{row.label}</span>
              <span className="danger-breakdown-value">{row.value}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="danger-register-btn" onClick={() => setShowModal(true)}>
        <i className="bi bi-plus-lg" /> 이 구역 점검 등록
      </button>

      {showModal && <InspectionAddModal regionName={region.name} onClose={() => setShowModal(false)} />}
    </div>
  );
}

function DangerMap() {
  const [accidentType, setAccidentType] = useState('전체');
  const [period, setPeriod] = useState('최근 1년');
  const { state } = useLocation();

  const [dongs, setDongs] = useState([]);
  const [status, setStatus] = useState('loading'); // loading | ready | error
  const [selectedAdminCode, setSelectedAdminCode] = useState(null);

  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const polygonsByAdminCodeRef = useRef({});
  const boundsByAdminCodeRef = useRef({});
  const latestSelectedRef = useRef(null);
  latestSelectedRef.current = selectedAdminCode;

  useEffect(() => {
    let cancelled = false;

    getRiskMapDongs()
      .then((data) => {
        if (cancelled) return;
        setDongs(data);
        setStatus('ready');

        const preselectName = state?.region?.name;
        const preselect = data.find((d) => d.dong_nm === preselectName);
        const highestScored = [...data].sort((a, b) => b.risk_score - a.risk_score)[0];
        setSelectedAdminCode((preselect ?? highestScored)?.admin_code ?? null);
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const rankedByScore = useMemo(
    () => [...dongs].sort((a, b) => b.risk_score - a.risk_score),
    [dongs]
  );

  const headerTitle = useMemo(() => {
    const sigunguSet = new Set(dongs.map((d) => d.sigungu_nm));
    if (sigunguSet.size === 1) return `${[...sigunguSet][0]} 위험 스코어`;
    return '관할구역 위험 스코어';
  }, [dongs]);

  const selectedRegion = useMemo(() => {
    if (!selectedAdminCode) return null;
    const dong = dongs.find((d) => d.admin_code === selectedAdminCode);
    if (!dong) return null;
    const rank = rankedByScore.findIndex((d) => d.admin_code === selectedAdminCode) + 1;
    return dongToRegion(dong, resolveLevel(Number(dong.risk_score)), rank, dongs.length);
  }, [selectedAdminCode, dongs, rankedByScore, resolveLevel]);

  const focusOnDong = (adminCode) => {
    const map = mapRef.current;
    if (!map) return;

    Object.entries(polygonsByAdminCodeRef.current).forEach(([code, polygons]) => {
      const isSelected = code === adminCode;
      polygons.forEach((polygon) => {
        polygon.setOptions({
          fillOpacity: isSelected ? 0.85 : 0.55,
          strokeWeight: isSelected ? 2.5 : 1.2,
        });
      });
    });

    const dongBounds = boundsByAdminCodeRef.current[adminCode];
    if (dongBounds) {
      map.setBounds(dongBounds, 40);
    }
  };

  useEffect(() => {
    if (status !== 'ready' || dongs.length === 0 || !mapContainerRef.current) return;

    let disposed = false;

    loadKakaoMap().then((kakao) => {
      if (disposed) return;

      const map = new kakao.maps.Map(mapContainerRef.current, {
        center: new kakao.maps.LatLng(36.6424, 127.489),
        level: 6,
      });
      mapRef.current = map;

      const style = getComputedStyle(document.documentElement);
      const fillColorByLevel = {
        safe: style.getPropertyValue('--color-risk-safe').trim(),
        warning: style.getPropertyValue('--color-risk-warning').trim(),
        caution: style.getPropertyValue('--color-risk-caution').trim(),
        danger: style.getPropertyValue('--color-risk-danger').trim(),
      };

      const bounds = new kakao.maps.LatLngBounds();
      polygonsByAdminCodeRef.current = {};
      boundsByAdminCodeRef.current = {};

      dongs.forEach((dong) => {
        if (!dong.geometry?.coordinates) return;
        const level = resolveLevel(Number(dong.risk_score));
        const dongBounds = new kakao.maps.LatLngBounds();
        const dongPolygons = [];

        dong.geometry.coordinates.forEach((polygonCoords) => {
          const rings = polygonCoords.map((ring) =>
            ring.map(([lng, lat]) => {
              const point = new kakao.maps.LatLng(lat, lng);
              bounds.extend(point);
              dongBounds.extend(point);
              return point;
            })
          );

          const polygon = new kakao.maps.Polygon({
            map,
            path: rings.length === 1 ? rings[0] : rings,
            fillColor: fillColorByLevel[level],
            fillOpacity: 0.55,
            strokeWeight: 1.2,
            strokeColor: '#ffffff',
            strokeOpacity: 0.9,
          });

          kakao.maps.event.addListener(polygon, 'click', () => {
            setSelectedAdminCode(dong.admin_code);
          });

          dongPolygons.push(polygon);
        });

        polygonsByAdminCodeRef.current[dong.admin_code] = dongPolygons;
        boundsByAdminCodeRef.current[dong.admin_code] = dongBounds;
      });

      map.setBounds(bounds);

      if (latestSelectedRef.current) {
        focusOnDong(latestSelectedRef.current);
      }
    });

    return () => {
      disposed = true;
      Object.values(polygonsByAdminCodeRef.current).forEach((polygons) =>
        polygons.forEach((p) => p.setMap(null))
      );
      polygonsByAdminCodeRef.current = {};
    };
  }, [status, dongs, resolveLevel]);

  useEffect(() => {
    if (!selectedAdminCode) return;
    focusOnDong(selectedAdminCode);
  }, [selectedAdminCode]);

  return (
    <div className="danger">
      <div className="danger-content">
        <div className="danger-map-card">
          <div className="danger-map-header">
            <div>
              <h3 className="danger-map-title">{headerTitle}</h3>
              <p className="danger-map-sub">행정구역을 클릭하면 상세 근거를 확인할 수 있습니다</p>
            </div>
            <div className="danger-legend">
              <span className="danger-legend-label">낮음</span>
              <span className="danger-legend-dot danger-legend-dot--safe" />
              <span className="danger-legend-dot danger-legend-dot--warning" />
              <span className="danger-legend-dot danger-legend-dot--caution" />
              <span className="danger-legend-dot danger-legend-dot--danger" />
              <span className="danger-legend-label">높음</span>
            </div>
          </div>
          <div className="danger-map-body">
            {status === 'error' && (
              <div className="danger-map-placeholder">
                <i className="bi bi-exclamation-triangle" />
                <span>지도를 불러오지 못했습니다</span>
                <span className="danger-map-placeholder-sub">잠시 후 다시 시도해주세요</span>
              </div>
            )}
            {status === 'loading' && (
              <div className="danger-map-placeholder">
                <i className="bi bi-map" />
                <span>위험 스코어 지도를 불러오는 중</span>
              </div>
            )}
            <div ref={mapContainerRef} className="danger-map-kakao" style={{ display: status === 'ready' ? 'block' : 'none' }} />
          </div>
        </div>

        {selectedRegion && <RegionPanel region={selectedRegion} />}
      </div>
    </div>
  );
}

function DangerPage() {
  return (
    <DashboardLayout>
      <DangerMap />
    </DashboardLayout>
  );
}

export default DangerPage;