import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../layouts/dashboardlayout';
import './priority.css';

const LEVEL_CLASS = { 위험: 'danger', 경계: 'caution', 주의: 'warning', 안전: 'safe' };

const MOCK_REGIONS = [
  {
    name: '중앙동', type: '동', district: '상당구',
    level: '위험', score: 88, rank: 1, total: 15,
    dispatch: 524, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 94,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 361, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 69,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 94 }, { label: '오전', count: 127 },
      { label: '오후', count: 146 }, { label: '저녁', count: 157 },
    ],
  },
  {
    name: '성안동', type: '동', district: '상당구',
    level: '위험', score: 84, rank: 2, total: 15,
    dispatch: 478, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 86,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 330, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 62,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 86 }, { label: '오전', count: 115 },
      { label: '오후', count: 134 }, { label: '저녁', count: 143 },
    ],
  },
  {
    name: '탑대성동', type: '동', district: '상당구',
    level: '위험', score: 81, rank: 3, total: 15,
    dispatch: 441, mainType: '화재', nightRatio: 20,
    types: [
      { label: '화재', count: 220, pct: 50, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 154, pct: 35, color: 'var(--color-blue)' },
      { label: '구조', count: 67,  pct: 15, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 88 }, { label: '오전', count: 106 },
      { label: '오후', count: 124 }, { label: '저녁', count: 123 },
    ],
  },
  {
    name: '영운동', type: '동', district: '상당구',
    level: '경계', score: 76, rank: 4, total: 15,
    dispatch: 402, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 72,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 277, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 53,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 72 }, { label: '오전', count: 97 },
      { label: '오후', count: 113 }, { label: '저녁', count: 120 },
    ],
  },
  {
    name: '용암2동', type: '동', district: '상당구',
    level: '경계', score: 72, rank: 5, total: 15,
    dispatch: 388, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 70,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 268, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 50,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 70 }, { label: '오전', count: 93 },
      { label: '오후', count: 109 }, { label: '저녁', count: 116 },
    ],
  },
  {
    name: '금천동', type: '동', district: '상당구',
    level: '경계', score: 71, rank: 6, total: 15,
    dispatch: 372, mainType: '화재', nightRatio: 20,
    types: [
      { label: '화재', count: 186, pct: 50, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 130, pct: 35, color: 'var(--color-blue)' },
      { label: '구조', count: 56,  pct: 15, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 74 }, { label: '오전', count: 89 },
      { label: '오후', count: 105 }, { label: '저녁', count: 104 },
    ],
  },
  {
    name: '용암1동', type: '동', district: '상당구',
    level: '경계', score: 69, rank: 7, total: 15,
    dispatch: 360, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 65,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 248, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 47,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 65 }, { label: '오전', count: 86 },
      { label: '오후', count: 101 }, { label: '저녁', count: 108 },
    ],
  },
  {
    name: '분평동', type: '동', district: '상당구',
    level: '경계', score: 64, rank: 8, total: 15,
    dispatch: 318, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 57,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 219, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 42,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 57 }, { label: '오전', count: 76 },
      { label: '오후', count: 89 }, { label: '저녁', count: 96 },
    ],
  },
  {
    name: '용담명암산성동', type: '동', district: '상당구',
    level: '경계', score: 62, rank: 9, total: 15,
    dispatch: 300, mainType: '화재', nightRatio: 20,
    types: [
      { label: '화재', count: 150, pct: 50, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 105, pct: 35, color: 'var(--color-blue)' },
      { label: '구조', count: 45,  pct: 15, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 60 }, { label: '오전', count: 72 },
      { label: '오후', count: 84 }, { label: '저녁', count: 84 },
    ],
  },
  {
    name: '산남동', type: '동', district: '상당구',
    level: '주의', score: 58, rank: 10, total: 15,
    dispatch: 286, mainType: '구급', nightRatio: 18,
    types: [
      { label: '화재', count: 51,  pct: 18, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 197, pct: 69, color: 'var(--color-blue)' },
      { label: '구조', count: 38,  pct: 13, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 51 }, { label: '오전', count: 69 },
      { label: '오후', count: 80 }, { label: '저녁', count: 86 },
    ],
  },
  {
    name: '미원면', type: '면', district: '상당구',
    level: '주의', score: 55, rank: 11, total: 15,
    dispatch: 198, mainType: '산악', nightRatio: 8,
    types: [
      { label: '화재', count: 20,  pct: 10, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 59,  pct: 30, color: 'var(--color-blue)' },
      { label: '구조', count: 119, pct: 60, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 16 }, { label: '오전', count: 68 },
      { label: '오후', count: 72 }, { label: '저녁', count: 42 },
    ],
  },
  {
    name: '남일면', type: '면', district: '상당구',
    level: '주의', score: 47, rank: 12, total: 15,
    dispatch: 156, mainType: '화재', nightRatio: 20,
    types: [
      { label: '화재', count: 78,  pct: 50, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 55,  pct: 35, color: 'var(--color-blue)' },
      { label: '구조', count: 23,  pct: 15, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 31 }, { label: '오전', count: 37 },
      { label: '오후', count: 44 }, { label: '저녁', count: 44 },
    ],
  },
  {
    name: '문의면', type: '면', district: '상당구',
    level: '주의', score: 47, rank: 13, total: 15,
    dispatch: 150, mainType: '산악', nightRatio: 8,
    types: [
      { label: '화재', count: 15,  pct: 10, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 45,  pct: 30, color: 'var(--color-blue)' },
      { label: '구조', count: 90,  pct: 60, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 12 }, { label: '오전', count: 51 },
      { label: '오후', count: 57 }, { label: '저녁', count: 30 },
    ],
  },
  {
    name: '가덕면', type: '면', district: '상당구',
    level: '주의', score: 41, rank: 14, total: 15,
    dispatch: 132, mainType: '화재', nightRatio: 20,
    types: [
      { label: '화재', count: 66,  pct: 50, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 46,  pct: 35, color: 'var(--color-blue)' },
      { label: '구조', count: 20,  pct: 15, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 26 }, { label: '오전', count: 32 },
      { label: '오후', count: 37 }, { label: '저녁', count: 37 },
    ],
  },
  {
    name: '낭성면', type: '면', district: '상당구',
    level: '안전', score: 38, rank: 15, total: 15,
    dispatch: 120, mainType: '산악', nightRatio: 8,
    types: [
      { label: '화재', count: 12,  pct: 10, color: 'var(--color-risk-danger)' },
      { label: '구급', count: 36,  pct: 30, color: 'var(--color-blue)' },
      { label: '구조', count: 72,  pct: 60, color: 'var(--color-risk-caution)' },
    ],
    timeSlots: [
      { label: '심야', count: 10 }, { label: '오전', count: 40 },
      { label: '오후', count: 46 }, { label: '저녁', count: 24 },
    ],
  },
];

function PriorityList() {
  const navigate = useNavigate();

  return (
    <div className="priority">
      <div className="priority-warn">
        <i className="bi bi-exclamation-triangle-fill priority-warn-icon" />
        <span>
          위험 스코어가 높은 구역일수록 출동 가능성이 큽니다.
          상위 구역부터 <strong>점검·순찰 우선순위</strong>를 배정하세요.
        </span>
      </div>

      <div className="priority-card">
        <div className="priority-head">
          <span className="priority-col priority-col--rank">순위</span>
          <span className="priority-col priority-col--region">행정구역</span>
          <span className="priority-col priority-col--score">위험 등급 · 스코어</span>
          <span className="priority-col priority-col--type">주요 사고유형</span>
          <span className="priority-col priority-col--dispatch">연간 출동</span>
          <span className="priority-col priority-col--night">야간 비중</span>
          <span className="priority-col priority-col--action" />
        </div>

        {MOCK_REGIONS.map((region) => {
          const levelCls = LEVEL_CLASS[region.level] ?? 'safe';
          return (
            <div key={region.name} className="priority-row">
              <span className={`priority-col priority-col--rank priority-rank${region.rank <= 3 ? ' top' : ''}`}>
                {region.rank}
              </span>

              <div className="priority-col priority-col--region">
                <span className="priority-region-name">{region.name}</span>
                <span className="priority-region-sub">{region.type} · {region.district}</span>
              </div>

              <div className="priority-col priority-col--score">
                <div className="priority-score-row">
                  <span className={`priority-level-badge priority-level-badge--${levelCls}`}>{region.level}</span>
                  <span className={`priority-score-num priority-score-num--${levelCls}`}>{region.score}</span>
                </div>
                <div className="priority-bar-track">
                  <div className={`priority-bar priority-bar--${levelCls}`} style={{ width: `${region.score}%` }} />
                </div>
              </div>

              <span className="priority-col priority-col--type priority-type-text">
                주요 {region.mainType} 중심
              </span>

              <span className="priority-col priority-col--dispatch priority-stat">
                <span className="priority-stat-num">{region.dispatch.toLocaleString()}</span>
                <span className="priority-stat-unit">건</span>
              </span>

              <span className="priority-col priority-col--night priority-stat">
                <span className="priority-stat-num">{region.nightRatio}</span>
                <span className="priority-stat-unit">%</span>
              </span>

              <div className="priority-col priority-col--action">
                <button
                  className="priority-detail-btn"
                  onClick={() => navigate('/dashboard/map', { state: { region } })}
                >
                  상세
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PriorityPage() {
  return (
    <DashboardLayout>
      <PriorityList />
    </DashboardLayout>
  );
}

export default PriorityPage;
