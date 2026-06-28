import { useState } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import './danger.css';

const ACCIDENT_TYPES = ['전체', '화재', '구급', '구조'];
const PERIODS = ['최근 1년', '최근 3년', '전체'];
const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };

const MOCK_REGION = {
  name: '중앙동',
  type: '동',
  level: '위험',
  score: 88,
  rank: 1,
  total: 15,
  dispatch: 524,
  mainType: '구급',
  nightRatio: 18,
  types: [
    { label: '화재', count: 96,  pct: 18, color: 'var(--color-risk-danger)' },
    { label: '구급', count: 360, pct: 69, color: 'var(--color-blue)' },
    { label: '구조', count: 68,  pct: 13, color: 'var(--color-risk-caution)' },
  ],
  timeSlots: [
    { label: '심야', count: 94 },
    { label: '오전', count: 126 },
    { label: '오후', count: 147 },
    { label: '저녁', count: 157 },
  ],
};

function DonutChart({ types, total }) {
  const r = 52;
  const cx = 70;
  const cy = 70;
  const circ = 2 * Math.PI * r;
  const strokeWidth = 14;
  let cumulative = 0;

  return (
    <div className="danger-donut-wrap">
      <svg width={140} height={140} viewBox="0 0 140 140">
        {types.map((t, i) => {
          const dashLen = (t.pct / 100) * circ;
          const rotation = -90 + (cumulative / 100) * 360;
          cumulative += t.pct;
          return (
            <circle
              key={i}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={t.color}
              strokeWidth={strokeWidth}
              strokeDasharray={`${dashLen} ${circ - dashLen}`}
              transform={`rotate(${rotation}, ${cx}, ${cy})`}
            />
          );
        })}
      </svg>
      <div className="danger-donut-center">
        <span className="danger-donut-total">{total.toLocaleString()}</span>
        <span className="danger-donut-unit">건</span>
      </div>
    </div>
  );
}

function RegionPanel({ region }) {
  const maxCount = Math.max(...region.timeSlots.map((s) => s.count));
  const levelCls = LEVEL_CLASS[region.level] ?? 'safe';

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
        <div className="danger-section-title">스코어 근거</div>
        <div className="danger-basis">
          <div className="danger-basis-item">
            <span className="danger-basis-label">연간 출동</span>
            <span className="danger-basis-value">{region.dispatch.toLocaleString()}</span>
          </div>
          <div className="danger-basis-item">
            <span className="danger-basis-label">주요 유형</span>
            <span className="danger-basis-value">{region.mainType}</span>
          </div>
          <div className="danger-basis-item">
            <span className="danger-basis-label">야간 비중</span>
            <span className="danger-basis-value">{region.nightRatio}%</span>
          </div>
        </div>
      </div>

      <div className="danger-divider" />

      <div className="danger-section">
        <div className="danger-section-title">사고 유형 구성</div>
        <div className="danger-composition">
          <DonutChart types={region.types} total={region.dispatch} />
          <div className="danger-type-legend">
            {region.types.map((t) => (
              <div key={t.label} className="danger-type-row">
                <div className="danger-type-left">
                  <span className="danger-type-dot" style={{ background: t.color }} />
                  <span className="danger-type-label">{t.label}</span>
                </div>
                <span className="danger-type-count">{t.count}건</span>
                <span className="danger-type-pct">{t.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="danger-divider" />

      <div className="danger-section">
        <div className="danger-section-title">시간대별 출동 분포</div>
        <div className="danger-time-chart">
          {region.timeSlots.map((s) => (
            <div key={s.label} className="danger-time-col">
              <span className="danger-time-count">{s.count}</span>
              <div className="danger-time-bar-track">
                <div
                  className={`danger-time-bar danger-time-bar--${levelCls}`}
                  style={{ height: `${(s.count / maxCount) * 100}%` }}
                />
              </div>
              <span className="danger-time-label">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="danger-register-btn">
        <i className="bi bi-plus-lg" /> 이 구역 점검 등록
      </button>
    </div>
  );
}

function DangerMap() {
  const [accidentType, setAccidentType] = useState('전체');
  const [period, setPeriod] = useState('최근 1년');
  const selectedRegion = MOCK_REGION;

  return (
    <div className="danger">
      <div className="danger-filter-bar">
        <div className="danger-filter-group">
          <span className="danger-filter-label">사고 유형</span>
          <div className="danger-chips">
            {ACCIDENT_TYPES.map((t) => (
              <button
                key={t}
                className={`danger-chip${accidentType === t ? ' active' : ''}`}
                onClick={() => setAccidentType(t)}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        <div className="danger-filter-group">
          <span className="danger-filter-label">기간</span>
          <div className="danger-chips">
            {PERIODS.map((p) => (
              <button
                key={p}
                className={`danger-chip${period === p ? ' active' : ''}`}
                onClick={() => setPeriod(p)}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="danger-content">
        <div className="danger-map-card">
          <div className="danger-map-header">
            <div>
              <h3 className="danger-map-title">청주시 상당구 위험 스코어</h3>
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
            {/* SVG 또는 지도 API가 들어올 영역 */}
            <div className="danger-map-placeholder">
              <i className="bi bi-map" />
              <span>지도 영역</span>
              <span className="danger-map-placeholder-sub">SVG 또는 지도 API 연동 예정</span>
            </div>
          </div>
        </div>

        <RegionPanel region={selectedRegion} />
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
