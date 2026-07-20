import { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../layouts/authlayout';
import { login, getMustChangePassword } from '../../../api/auth';
import { useRefreshUser } from '../contexts/userHooks';
import './login.css';

function Login() {
  const [showPW, setShowPW] = useState(false);
  const [firefighterNumber, setFirefighterNumber] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const errorTimerRef = useRef(null);
  const navigate = useNavigate();
  const refreshUser = useRefreshUser();

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    try {
      await login(firefighterNumber, password);
      await refreshUser();

      if (getMustChangePassword()) {
        navigate('/change-password');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      if (errorTimerRef.current) clearTimeout(errorTimerRef.current);
      setError(err.response?.data?.detail || '로그인에 실패했습니다.');
      errorTimerRef.current = setTimeout(() => setError(''), 4000);
    }
  }

  return (
    <AuthLayout>
      <div className="login-container">
        <div className="login-header">
          <span className="login-eyebrow">소방대원 통합 인증</span>
          <h2 className="login-title">로그인</h2>
          <p className="login-subtitle">배정된 대원번호로 접속하세요.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label className="form-label">대원번호</label>
            <input
              type="text"
              className="form-input"
              placeholder="대원번호를 입력하세요."
              value={firefighterNumber}
              onChange={(e) => setFirefighterNumber(e.target.value)}
            />
          </div>

          <div className="form-field">
            <label className="form-label">비밀번호</label>
            <div className="input-wrapper">
              <input
                type={showPW ? 'text' : 'password'}
                className="form-input"
                placeholder='비밀번호를 입력하세요.'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className='pw-toggle'
                onClick={() => setShowPW(!showPW)}
              >
                <i className={`bi bi-eye${showPW ? '' : '-slash'}-fill`} />
              </button>
            </div>
          </div>

          {error && (
            <div className="login-error">
              <i className="bi bi-exclamation-circle-fill" />
              <span>{error}</span>
            </div>
          )}

          <Link to="/findpw" className="forgot-link">비밀번호 찾기</Link>

          <button type="submit" className="login-btn">로그인</button>
        </form>

        <div className="login-notice">
          <i className="bi bi-info-circle login-notice-icon" />
          <p>
            본 시스템은 소방 공무 목적의 내부망 전용입니다. 인증 정보는 소속
            소방서 관리자에게 발급받으세요.
          </p>
        </div>
      </div>
    </AuthLayout>
  );
}

export default Login;