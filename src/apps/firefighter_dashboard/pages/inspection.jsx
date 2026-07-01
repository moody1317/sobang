import { useState } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import InspectionAddModal from './inspectionAdd';
import './inspection.css';

const INSPECTION_TYPES = ['화재안전', '위험물', '소방시설', '피난시설', '산악대비'];

const MOCK_INSPECTIONS = [
  { id: 1, date: '2026.06.21', region: '중앙동',   target: '성안프라자 (복합상가)',  type: '화재안전', officer: '김도현', status: '예정' },
  { id: 2, date: '2026.06.21', region: '탑대성동', target: '대성여객 차고지',        type: '위험물',   officer: '박서준', status: '예정' },
  { id: 3, date: '2026.06.20', region: '성안동',   target: '중앙시장 B동',           type: '화재안전', officer: '김도현', status: '진행' },
  { id: 4, date: '2026.06.19', region: '금천동',   target: '금천행복아파트 102동',   type: '소방시설', officer: '이하늘', status: '완료' },
  { id: 5, date: '2026.06.18', region: '영운동',   target: '영운초등학교',           type: '피난시설', officer: '김도현', status: '완료' },
  { id: 6, date: '2026.06.17', region: '용암1동',  target: '용암메디컬빌딩',         type: '화재안전', officer: '정유진', status: '완료' },
  { id: 7, date: '2026.06.16', region: '미원면',   target: '미원산림휴양관',         type: '산악대비', officer: '박서준', status: '완료' },
  { id: 8, date: '2026.06.15', region: '분평동',   target: '분평노인복지센터',       type: '화재안전', officer: '김도현', status: '완료' },
];

const TYPE_CLASS = {
  '화재안전': 'danger',
  '위험물':   'caution',
  '소방시설': 'brand',
  '피난시설': 'warning',
  '산악대비': 'safe',
};

const STATUS_CLASS = {
  '예정': 'warning',
  '진행': 'blue',
  '완료': 'safe',
};

function InspectionPage() {
  const [activeType, setActiveType] = useState('전체');
  const [showModal, setShowModal] = useState(false);

  const filtered = activeType === '전체'
    ? MOCK_INSPECTIONS
    : MOCK_INSPECTIONS.filter((r) => r.type === activeType);

  return (
    <DashboardLayout>
      <div className="insp">

        <div className="insp-toolbar">
          <div className="insp-filters">
            <button
              className={`insp-filter-btn${activeType === '전체' ? ' active' : ''}`}
              onClick={() => setActiveType('전체')}
            >
              전체
            </button>
            {INSPECTION_TYPES.map((t) => (
              <button
                key={t}
                className={`insp-filter-btn insp-filter-btn--${TYPE_CLASS[t]}${activeType === t ? ' active' : ''}`}
                onClick={() => setActiveType(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <button className="insp-add-btn" onClick={() => setShowModal(true)}>
            <i className="bi bi-plus-lg" /> 점검 등록
          </button>
        </div>

        <div className="insp-card">
          <div className="insp-head">
            <span>일자</span>
            <span>행정구역</span>
            <span>점검 대상</span>
            <span>점검 유형</span>
            <span>담당 대원</span>
            <span className="insp-col--right">상태</span>
          </div>

          {filtered.length === 0 ? (
            <div className="insp-empty">해당 유형의 점검 기록이 없습니다.</div>
          ) : (
            filtered.map((r) => (
              <div key={r.id} className="insp-row">
                <span className="insp-date">{r.date}</span>
                <span className="insp-region">{r.region}</span>
                <span className="insp-target">{r.target}</span>
                <span className={`insp-type-badge insp-type-badge--${TYPE_CLASS[r.type]}`}>{r.type}</span>
                <span className="insp-officer">{r.officer}</span>
                <span className="insp-col--right">
                  <span className={`insp-status-badge insp-status-badge--${STATUS_CLASS[r.status]}`}>{r.status}</span>
                </span>
              </div>
            ))
          )}
        </div>

      </div>

      {showModal && <InspectionAddModal onClose={() => setShowModal(false)} />}
    </DashboardLayout>
  );
}

export default InspectionPage;
