import { useState } from 'react';
import { useUser } from '../contexts/usercontext';
import './inspectionAdd.css';

const INSPECTION_TYPES = ['화재안전', '위험물', '소방시설', '피난시설', '산악대비'];

function InspectionAddModal({ regionName, onClose }) {
  const user = useUser();
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    location: regionName ?? '',
    target: '',
    inspectionType: '화재안전',
    date: today,
    officer: user?.name ?? '',
    note: '',
  });

  function set(key) {
    return (e) => setForm((p) => ({ ...p, [key]: e.target.value }));
  }

  return (
    <div className="ia-overlay" onClick={onClose}>
      <div className="ia-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ia-header">
          <div className="ia-title-row">
            <div className="ia-icon">
              <i className="bi bi-clipboard-check" />
            </div>
            <div>
              <div className="ia-title">점검 등록</div>
              <div className="ia-subtitle">현장 점검 일정을 등록합니다</div>
            </div>
          </div>
          <button className="ia-close" onClick={onClose}>
            <i className="bi bi-x-lg" />
          </button>
        </div>

        <div className="ia-body">
          <div className="ia-field">
            <label className="ia-label">행정구역 <span className="ia-required">*</span></label>
            <div className="ia-input-wrap">
              <i className="bi bi-geo-alt ia-input-icon" />
              <input
                className="ia-input ia-input--icon"
                value={form.location}
                onChange={set('location')}
              />
            </div>
          </div>

          <div className="ia-field">
            <label className="ia-label">점검 대상 <span className="ia-required">*</span></label>
            <input
              className="ia-input"
              placeholder="예) 성안프라자 (복합상가)"
              value={form.target}
              onChange={set('target')}
            />
          </div>

          <div className="ia-field">
            <label className="ia-label">점검 유형</label>
            <div className="ia-chips">
              {INSPECTION_TYPES.map((t) => (
                <button
                  key={t}
                  type="button"
                  className={`ia-chip${form.inspectionType === t ? ' active' : ''}`}
                  onClick={() => setForm((p) => ({ ...p, inspectionType: t }))}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="ia-two-col">
            <div className="ia-field">
              <label className="ia-label">점검 예정일 <span className="ia-required">*</span></label>
              <input type="date" className="ia-input ia-input--readonly" value={form.date} readOnly />
            </div>
            <div className="ia-field">
              <label className="ia-label">담당 대원</label>
              <input className="ia-input ia-input--readonly" value={form.officer} readOnly />
            </div>
          </div>

          <div className="ia-field">
            <label className="ia-label">비고 <span className="ia-label-opt">(선택)</span></label>
            <textarea
              className="ia-textarea"
              placeholder="점검 시 유의사항이나 메모를 입력하세요"
              value={form.note}
              onChange={set('note')}
              style={{resize: 'none'}}
            />
          </div>
        </div>

        <div className="ia-footer">
          <button className="ia-btn-cancel" onClick={onClose}>취소</button>
          <button className="ia-btn-confirm" onClick={onClose}>점검 등록</button>
        </div>
      </div>
    </div>
  );
}

export default InspectionAddModal;
