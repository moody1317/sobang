import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthLayout from '../layouts/authlayout';
import { changePassword } from '../../../api/auth';
import { useRefreshUser } from '../contexts/userHooks';
import './login.css';

function ChangePassword() {
  const [form, setForm] = useState({ current: '', next: '', confirm: '' });
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNext, setShowNext] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const refreshUser = useRefreshUser();

  function set(key) {
    return (e) => {
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
      setErrors((prev) => ({ ...prev, [key]: undefined, general: undefined }));
    };
  }

  function validate() {
    const e = {};
    if (!form.current) e.current = '임시 비밀번호를 입력하세요.';
    if (!form.next) e.next = '새 비밀번호를 입력하세요.';
    else if (form.next.length < 8) e.next = '비밀번호는 8자 이상이어야 합니다.';
    if (form.next !== form.confirm) e.confirm = '비밀번호가 일치하지 않습니다.';
    return e;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const e2 = validate();
    if (Object.keys(e2).length) { setErrors(e2); return; }
    setLoading(true);
    try {
      await changePassword(form.current, form.next);
      await refreshUser();
      navigate('/dashboard');
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || '비밀번호 변경에 실패했습니다.' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <div className="login-container">
        <div className="login-header">
          <span className="login-eyebrow">최초 로그인</span>
          <h2 className="login-title">비밀번호 변경</h2>
          <p className="login-subtitle">발급받은 임시 비밀번호를 새 비밀번호로 변경하세요.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label className="form-label">임시 비밀번호</label>
            <div className="input-wrapper">
              <input
                type={showCurrent ? 'text' : 'password'}
                className={`form-input${errors.current ? ' is-error' : ''}`}
                placeholder="발급받은 임시 비밀번호"
                value={form.current}
                onChange={set('current')}
              />
              <button type="button" className="pw-toggle" onClick={() => setShowCurrent((v) => !v)}>
                <i className={`bi bi-eye${showCurrent ? '' : '-slash'}-fill`} />
              </button>
            </div>
            {errors.current && <span className="form-error">{errors.current}</span>}
          </div>

          <div className="form-field">
            <label className="form-label">새 비밀번호</label>
            <div className="input-wrapper">
              <input
                type={showNext ? 'text' : 'password'}
                className={`form-input${errors.next ? ' is-error' : ''}`}
                placeholder="8자 이상"
                value={form.next}
                onChange={set('next')}
              />
              <button type="button" className="pw-toggle" onClick={() => setShowNext((v) => !v)}>
                <i className={`bi bi-eye${showNext ? '' : '-slash'}-fill`} />
              </button>
            </div>
            {errors.next && <span className="form-error">{errors.next}</span>}
          </div>

          <div className="form-field">
            <label className="form-label">새 비밀번호 확인</label>
            <div className="input-wrapper">
              <input
                type={showNext ? 'text' : 'password'}
                className={`form-input${errors.confirm ? ' is-error' : ''}`}
                placeholder="새 비밀번호를 한 번 더 입력"
                value={form.confirm}
                onChange={set('confirm')}
              />
            </div>
            {errors.confirm && <span className="form-error">{errors.confirm}</span>}
          </div>

          {errors.general && (
            <div className="login-error">
              <i className="bi bi-exclamation-circle-fill" />
              <span>{errors.general}</span>
            </div>
          )}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? '변경 중…' : '비밀번호 변경하기'}
          </button>
        </form>
      </div>
    </AuthLayout>
  );
}

export default ChangePassword;
