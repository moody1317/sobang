import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import InspectionAddModal from './inspectionAdd';
import InspectionCompleteModal from './inspectionComplete';
import { getInspections, startInspection, completeInspection } from '../../../api/inspections';
import './inspection.css';

const INSPECTION_TYPES = ['화재안전', '위험물', '소방시설', '피난시설', '산악대비'];

const TYPE_CLASS = {
  '화재안전': 'danger', '위험물': 'caution', '소방시설': 'brand', '피난시설': 'warning', '산악대비': 'safe',
};
const STATUS_CLASS = { '예정': 'warning', '진행': 'blue', '완료': 'safe' };

function InspectionPage() {
  const [activeType, setActiveType] = useState('전체');
  const [showModal, setShowModal] = useState(false);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [completingTarget, setCompletingTarget] = useState(null);

  const fetchInspections = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getInspections();
      setInspections(data);
    } catch {
      setInspections([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInspections();
  }, [fetchInspections]);

  const filtered = activeType === '전체'
    ? inspections
    : inspections.filter((r) => r.inspection_type === activeType);

  async function handleStart(id) {
    await startInspection(id);
    fetchInspections();
  }

  function openCompleteModal(inspection) {
    setCompletingTarget(inspection);
  }

  return (
    <DashboardLayout>
      <div className="insp">
        <div className="insp-toolbar">
          <div className="insp-filters">
            <button className={`insp-filter-btn${activeType === '전체' ? ' active' : ''}`} onClick={() => setActiveType('전체')}>전체</button>
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
            <span>일자</span><span>행정구역</span><span>점검 대상</span>
            <span>점검 유형</span><span>담당 대원</span><span className="insp-col--right">상태</span>
          </div>

          {loading ? (
            <div className="insp-empty">불러오는 중…</div>
          ) : filtered.length === 0 ? (
            <div className="insp-empty">해당 유형의 점검 기록이 없습니다.</div>
          ) : (
            filtered.map((r) => (
              <div key={r.id} className="insp-row">
                <span className="insp-date">{r.scheduled_date}</span>
                <span className="insp-region">{r.ward_name}</span>
                <span className="insp-target">{r.target}</span>
                <span className={`insp-type-badge insp-type-badge--${TYPE_CLASS[r.inspection_type]}`}>{r.inspection_type}</span>
                <span className="insp-officer">{r.inspector_name}</span>
                <span className="insp-col--right">
                  <span className={`insp-status-badge insp-status-badge--${STATUS_CLASS[r.status]}`}>{r.status}</span>
                  {r.status === '예정' && (
                    <button className="insp-action-btn" onClick={() => handleStart(r.id)}>시작</button>
                  )}
                  {r.status === '진행' && (
                    <button className="insp-action-btn" onClick={() => openCompleteModal(r)}>완료</button>
                  )}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <InspectionAddModal onClose={() => setShowModal(false)} onCreated={fetchInspections} />
      )}

      {completingTarget && (
        <InspectionCompleteModal
          inspection={completingTarget}
          onClose={() => setCompletingTarget(null)}
          onCompleted={fetchInspections}
        />
      )}
    </DashboardLayout>
  );
}

export default InspectionPage;