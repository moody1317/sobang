import { useState, useEffect } from 'react';
import { useUser } from '../contexts/userHooks';
import { getUsers, bulkRegisterEducation } from '../../../api/admin';
import './inspectionAdd.css';

function dateKey(year, month, day) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function TrainingBulkAddModal({ viewYear, viewMonth, defaultDay, onClose, onRegistered }) {
  const user = useUser();
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

  const [title, setTitle] = useState('');
  const [day, setDay] = useState(defaultDay);
  const [memberCount, setMemberCount] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getUsers().then((users) => setMemberCount(users.length)).catch(() => setMemberCount(null));
  }, []);

  async function handleSubmit() {
    if (!title) return;
    setSaving(true);
    setError(null);
    try {
      await bulkRegisterEducation(title, dateKey(viewYear, viewMonth, day));
      onRegistered?.();
      onClose();
    } catch {
      setError('교육 일괄 등록에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="ia-overlay" onClick={onClose}>
      <div className="ia-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ia-header">
          <div className="ia-title-row">
            <div className="ia-icon">
              <i className="bi bi-people" />
            </div>
            <div>
              <div className="ia-title">교육 일괄 등록</div>
              <div className="ia-subtitle">전체 대원에게 교육 일정을 배정합니다</div>
            </div>
          </div>
          <button className="ia-close" onClick={onClose}>
            <i className="bi bi-x-lg" />
          </button>
        </div>

        <div className="ia-body">
          <div className="ia-field">
            <label className="ia-label">교육명 <span className="ia-required">*</span></label>
            <input
              className="ia-input"
              placeholder="예) 화재진압 전술훈련"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="ia-field">
            <label className="ia-label">교육 일자 <span className="ia-required">*</span></label>
            <select className="ia-input" value={day} onChange={(e) => setDay(Number(e.target.value))}>
              {Array.from({ length: daysInMonth }, (_, i) => i + 1).map((d) => (
                <option key={d} value={d}>{viewMonth + 1}월 {d}일</option>
              ))}
            </select>
          </div>

          <p className="ia-info">
            <i className="bi bi-people" />
            <span>
              <strong>{user?.unit_name ?? '소속'} 소속 대원 {memberCount ?? '...'}명</strong> 전원의 해당 일자에{' '}
              <strong>교육 활동</strong>이 추가되며(근무 형태는 유지), 알림이 전송됩니다.
            </span>
          </p>

          {error && <p className="ia-error">{error}</p>}
        </div>

        <div className="ia-footer">
          <button className="ia-btn-cancel" onClick={onClose}>취소</button>
          <button className="ia-btn-confirm" onClick={handleSubmit} disabled={saving || !title}>
            {saving ? '등록 중…' : '전체 대원에게 등록'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TrainingBulkAddModal;
