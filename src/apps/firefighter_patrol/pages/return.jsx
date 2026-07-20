import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { completeReturn } from '../../../api/incidents';
import './return.css';

const INCIDENT_ICON = {
  화재: 'bi-fire',
  구조: 'bi-life-preserver',
  구급: 'bi-heart-pulse-fill',
  위험물: 'bi-exclamation-triangle-fill',
  기타: 'bi-question-circle-fill',
};

function PatrolReturn() {
  const navigate = useNavigate();
  const location = useLocation();
  const incident = location.state?.incident;
  const isFalseAlarm = location.state?.isFalseAlarm ?? false;

  const [activityNote, setActivityNote] = useState(isFalseAlarm ? '현장 확인 결과 허위 신고로 판단됨' : '');
  const [equipmentUsed, setEquipmentUsed] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!incident) {
      navigate('/firefighter_patrol');
    }
  }, [incident, navigate]);

  if (!incident) return null;

  async function handleSubmit() {
    if (!activityNote.trim()) {
      setError('현장 활동 내용을 입력하세요.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await completeReturn(incident.id, {
        activity_note: activityNote.trim(),
        equipment_used: equipmentUsed.trim() || undefined,
        reported_false_alarm: isFalseAlarm,
      });
      navigate('/firefighter_patrol');
    } catch (err) {
      setError(err.response?.data?.detail || '복귀 처리에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <PatrolLayout>
      <div className="patrol-return">
        <div className="patrol-return-badge">
          <i className="bi bi-check-circle-fill" />
          <span>{isFalseAlarm ? '허위 신고 처리' : '출동 종료 보고'}</span>
        </div>

        <div className="patrol-return-icon-wrap">
          <i className={`bi ${INCIDENT_ICON[incident.incident_type] ?? 'bi-exclamation-triangle-fill'} patrol-return-icon`} />
        </div>

        <h2 className="patrol-return-title">
          {isFalseAlarm ? '허위 신고 확인' : `${incident.incident_type} 출동 종료`}
        </h2>

        <div className="patrol-return-location">
          <span className="patrol-return-location-name">
            <i className="bi bi-geo-alt-fill" /> {incident.dong_name}
          </span>
          <span className="patrol-return-location-sub">{incident.address}</span>
        </div>

        {error && <div className="patrol-return-error">{error}</div>}

        <div className="patrol-return-field">
          <label className="patrol-return-label">
            현장 활동 내용 <span className="patrol-return-required">*</span>
          </label>
          <textarea
            className="patrol-return-textarea"
            placeholder="현장에서 수행한 활동을 입력하세요"
            value={activityNote}
            onChange={(e) => setActivityNote(e.target.value)}
            rows={4}
          />
        </div>

        <div className="patrol-return-field">
          <label className="patrol-return-label">사용 장비</label>
          <input
            className="patrol-return-input"
            placeholder="사용한 장비 (선택)"
            value={equipmentUsed}
            onChange={(e) => setEquipmentUsed(e.target.value)}
          />
        </div>

        <button className="patrol-return-btn" onClick={handleSubmit} disabled={loading}>
          {loading ? '처리 중…' : '복귀 완료'}
        </button>
        <p className="patrol-return-note">
          같이 출동한 인원이 더 있다면, 전원이 복귀 처리해야 신고가 종료됩니다.
        </p>
      </div>
    </PatrolLayout>
  );
}

export default PatrolReturn;
