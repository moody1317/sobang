// src/apps/firefighter_dashboard/pages/inspectionComplete.jsx
import { useState } from 'react';
import { completeInspection } from '../../../api/inspections';
import './inspectionAdd.css';   // 등록 모달과 스타일 공유

const RESULTS = ['이상없음', '시정필요', '불합격'];

function InspectionCompleteModal({ inspection, onClose, onCompleted }) {
  const [result, setResult] = useState('이상없음');
  const [detail, setDetail] = useState('');
  const [nextDate, setNextDate] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit() {
    setSaving(true);
    setError(null);
    try {
      await completeInspection(inspection.id, {
        result,
        result_detail: detail || null,
        next_inspection_date: nextDate || null,
      });
      onCompleted?.();
      onClose();
    } catch {
      setError('점검 완료 처리에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="ia-overlay" onClick={onClose}>
      <div className="ia-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ia-header">
          <div className="ia-title-row">
            <div className="ia-icon"><i className="bi bi-clipboard-check" /></div>
            <div>
              <div className="ia-title">점검 완료</div>
              <div className="ia-subtitle">{inspection.target} 점검 결과를 입력합니다</div>
            </div>
          </div>
          <button className="ia-close" onClick={onClose}><i className="bi bi-x-lg" /></button>
        </div>

        <div className="ia-body">
          <div className="ia-field">
            <label className="ia-label">점검 결과</label>
            <div className="ia-chips">
              {RESULTS.map((r) => (
                <button
                  key={r}
                  type="button"
                  className={`ia-chip${result === r ? ' active' : ''}`}
                  onClick={() => setResult(r)}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div className="ia-field">
            <label className="ia-label">상세 내용 <span className="ia-label-opt">(선택)</span></label>
            <textarea
              className="ia-textarea"
              placeholder="점검 중 발견한 사항을 입력하세요"
              value={detail}
              onChange={(e) => setDetail(e.target.value)}
              style={{ resize: 'none' }}
            />
          </div>

          <div className="ia-field">
            <label className="ia-label">재점검 예정일 <span className="ia-label-opt">(선택)</span></label>
            <input type="date" className="ia-input" value={nextDate} onChange={(e) => setNextDate(e.target.value)} />
          </div>

          {error && <p className="ia-error">{error}</p>}
        </div>

        <div className="ia-footer">
          <button className="ia-btn-cancel" onClick={onClose}>취소</button>
          <button className="ia-btn-confirm" onClick={handleSubmit} disabled={saving}>
            {saving ? '처리 중…' : '완료 처리'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default InspectionCompleteModal;