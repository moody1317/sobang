import { useState } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import Toggle from '../components/toggle';
import { useUser, useRefreshUser } from '../contexts/usercontext';
import { verifyPassword, updateProfile, changePassword } from '../../../api/auth';
import './mypage.css';

const ALERT_KEY = 'dashboard_alert_settings';

const DEFAULT_ALERTS = {
  riskSurge: true,
  weatherAlert: true,
  inspectionReminder: true,
};

function loadAlerts() {
  try {
    const saved = localStorage.getItem(ALERT_KEY);
    return saved ? { ...DEFAULT_ALERTS, ...JSON.parse(saved) } : DEFAULT_ALERTS;
  } catch {
    return DEFAULT_ALERTS;
  }
}

function VerifyStep({ onVerified, onClose }) {
  const [pw, setPw] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleConfirm() {
    if (!pw) { setError('비밀번호를 입력하세요.'); return; }
    setLoading(true);
    setError('');
    try {
      await verifyPassword(pw);
      onVerified(pw);
    } catch {
      setError('비밀번호가 일치하지 않습니다.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="edit-modal-header">
        <span className="edit-modal-title">본인 확인</span>
        <button className="edit-modal-close" onClick={onClose}>
          <i className="bi bi-x-lg" />
        </button>
      </div>
      <div className="edit-modal-body">
        <p className="edit-modal-desc">
          프로필을 수정하려면 현재 비밀번호를 입력하세요.
        </p>
        <div className="edit-modal-field">
          <label className="edit-modal-label">현재 비밀번호</label>
          <div className="edit-modal-input-wrap">
            <input
              type={showPw ? 'text' : 'password'}
              className={`edit-modal-input${error ? ' is-error' : ''}`}
              placeholder="비밀번호를 입력하세요"
              value={pw}
              onChange={(e) => { setPw(e.target.value); setError(''); }}
              onKeyDown={(e) => e.key === 'Enter' && handleConfirm()}
              autoFocus
            />
            <button
              type="button"
              className="edit-modal-eye"
              onClick={() => setShowPw((v) => !v)}
            >
              <i className={`bi bi-eye${showPw ? '' : '-slash'}-fill`} />
            </button>
          </div>
          {error && <span className="edit-modal-error">{error}</span>}
        </div>
      </div>
      <div className="edit-modal-footer">
        <button className="edit-modal-btn-cancel" onClick={onClose}>취소</button>
        <button
          className="edit-modal-btn-confirm"
          onClick={handleConfirm}
          disabled={loading}
        >
          {loading ? '확인 중…' : '확인'}
        </button>
      </div>
    </>
  );
}

function EditStep({ user, savedPw, onClose, onSaved }) {
  const [form, setForm] = useState({
    email: user?.email ?? '',
    phone: user?.phone_number ?? '',
    newPw: '',
    newPwConfirm: '',
  });
  const [showNewPw, setShowNewPw] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function set(key) {
    return (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }

  function handlePhone(e) {
    const digits = e.target.value.replace(/\D/g, '').slice(0, 11);
    let formatted = digits;
    if (digits.length > 7) formatted = `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`;
    else if (digits.length > 3) formatted = `${digits.slice(0, 3)}-${digits.slice(3)}`;
    setForm((prev) => ({ ...prev, phone: formatted }));
  }

  function validate() {
    const e = {};
    if (!form.email) e.email = '이메일을 입력하세요.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      e.email = '올바른 이메일 형식이 아닙니다.';
    if (!form.phone) e.phone = '연락처를 입력하세요.';
    if (form.newPw && form.newPw.length < 8)
      e.newPw = '비밀번호는 8자 이상이어야 합니다.';
    if (form.newPw && form.newPw !== form.newPwConfirm)
      e.newPwConfirm = '비밀번호가 일치하지 않습니다.';
    return e;
  }

  async function handleSave() {
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setLoading(true);
    try {
      await updateProfile({ current_password: savedPw, email: form.email, phone_number: form.phone });
      if (form.newPw) await changePassword(savedPw, form.newPw);
      onSaved();
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || '저장에 실패했습니다.' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="edit-modal-header">
        <span className="edit-modal-title">프로필 수정</span>
        <button className="edit-modal-close" onClick={onClose}>
          <i className="bi bi-x-lg" />
        </button>
      </div>
      <div className="edit-modal-body">
        {errors.general && (
          <div className="edit-modal-error-banner">{errors.general}</div>
        )}

        <div className="edit-modal-field">
          <label className="edit-modal-label">이메일</label>
          <input
            type="email"
            className={`edit-modal-input${errors.email ? ' is-error' : ''}`}
            value={form.email}
            onChange={set('email')}
          />
          {errors.email && <span className="edit-modal-error">{errors.email}</span>}
        </div>

        <div className="edit-modal-field">
          <label className="edit-modal-label">연락처</label>
          <input
            type="tel"
            className={`edit-modal-input${errors.phone ? ' is-error' : ''}`}
            placeholder="010-0000-0000"
            value={form.phone}
            onChange={handlePhone}
          />
          {errors.phone && <span className="edit-modal-error">{errors.phone}</span>}
        </div>

        <div className="edit-modal-divider" />

        <div className="edit-modal-field">
          <label className="edit-modal-label">
            새 비밀번호 <span className="edit-modal-label-opt">(선택)</span>
          </label>
          <div className="edit-modal-input-wrap">
            <input
              type={showNewPw ? 'text' : 'password'}
              className={`edit-modal-input${errors.newPw ? ' is-error' : ''}`}
              placeholder="변경 시에만 입력하세요"
              value={form.newPw}
              onChange={set('newPw')}
            />
            <button
              type="button"
              className="edit-modal-eye"
              onClick={() => setShowNewPw((v) => !v)}
            >
              <i className={`bi bi-eye${showNewPw ? '' : '-slash'}-fill`} />
            </button>
          </div>
          {errors.newPw && <span className="edit-modal-error">{errors.newPw}</span>}
        </div>

        {form.newPw && (
          <div className="edit-modal-field">
            <label className="edit-modal-label">비밀번호 확인</label>
            <input
              type={showNewPw ? 'text' : 'password'}
              className={`edit-modal-input${errors.newPwConfirm ? ' is-error' : ''}`}
              placeholder="새 비밀번호를 한 번 더 입력하세요"
              value={form.newPwConfirm}
              onChange={set('newPwConfirm')}
            />
            {errors.newPwConfirm && (
              <span className="edit-modal-error">{errors.newPwConfirm}</span>
            )}
          </div>
        )}
      </div>
      <div className="edit-modal-footer">
        <button className="edit-modal-btn-cancel" onClick={onClose}>취소</button>
        <button
          className="edit-modal-btn-confirm"
          onClick={handleSave}
          disabled={loading}
        >
          {loading ? '저장 중…' : '저장하기'}
        </button>
      </div>
    </>
  );
}

function MyPage() {
  const user = useUser();
  const refreshUser = useRefreshUser();
  const [alerts, setAlerts] = useState(loadAlerts);
  const [step, setStep] = useState(null); // null | 'verify' | 'edit'
  const [savedPw, setSavedPw] = useState('');
  const initial = user?.name?.[0] ?? '';

  function toggleAlert(key) {
    setAlerts((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      localStorage.setItem(ALERT_KEY, JSON.stringify(next));
      return next;
    });
  }

  function closeModal() {
    setStep(null);
    setSavedPw('');
  }

  function handleVerified(pw) {
    setSavedPw(pw);
    setStep('edit');
  }

  async function handleSaved() {
    closeModal();
    await refreshUser?.();
  }

  return (
    <div className="mypage">
      <div className="mypage-profile-card">
        <div className="mypage-profile-left">
          <div className="mypage-avatar">{initial}</div>
          <div className="mypage-profile-info">
            <div className="mypage-name-row">
              <span className="mypage-name">{user?.name ?? '—'}</span>
              {user?.rank && <span className="mypage-rank-chip">{user.rank}</span>}
            </div>
            <span className="mypage-station">{user?.station_name} - {user?.unit_name}</span>
          </div>
        </div>
        <button className="mypage-edit-btn" onClick={() => setStep('verify')}>
          프로필 수정
        </button>
      </div>

      <div className="mypage-panels">
        <div className="mypage-panel">
          <h3 className="mypage-panel-title">계정 정보</h3>
          <div className="mypage-info-list">
            {[
              { label: '대원번호', value: user?.firefighter_number },
              { label: '이메일',   value: user?.email },
              { label: '연락처',   value: user?.phone_number },
              { label: '가입일',   value: user?.created_at },
            ].map(({ label, value }) => (
              <div key={label} className="mypage-info-row">
                <span className="mypage-info-label">{label}</span>
                <span className="mypage-info-value">{value ?? '—'}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mypage-panel">
          <h3 className="mypage-panel-title">알림 설정</h3>
          <div className="mypage-alert-list">
            {[
              { key: 'riskSurge',           title: '위험도 급상승 알림',  sub: '관할 구역 스코어 변동 시' },
              { key: 'weatherAlert',         title: '기상 특보 알림',      sub: '건조·강풍 특보 발효 시' },
              { key: 'inspectionReminder',   title: '점검 기한 리마인더',  sub: '점검 예정 3일 전 안내' },
            ].map(({ key, title, sub }) => (
              <div key={key} className="mypage-alert-item">
                <div className="mypage-alert-info">
                  <span className="mypage-alert-title">{title}</span>
                  <span className="mypage-alert-sub">{sub}</span>
                </div>
                <Toggle checked={alerts[key]} onChange={() => toggleAlert(key)} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {step && (
        <div className="edit-modal-overlay" onClick={closeModal}>
          <div className="edit-modal" onClick={(e) => e.stopPropagation()}>
            {step === 'verify' && (
              <VerifyStep onVerified={handleVerified} onClose={closeModal} />
            )}
            {step === 'edit' && (
              <EditStep
                user={user}
                savedPw={savedPw}
                onClose={closeModal}
                onSaved={handleSaved}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function MyPagePage() {
  return (
    <DashboardLayout>
      <MyPage />
    </DashboardLayout>
  );
}

export default MyPagePage;
