import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PatrolLayout from '../layouts/patrollayout';
import { login, getMustChangePassword } from '../../../api/auth';
import { useRefreshUser } from '../../firefighter_dashboard/contexts/usercontext';
import './login.css';

function PatrolLogin() {
  const [firefighterNumber, setFirefighterNumber] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
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
        navigate('/firefighter_patrol');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '로그인에 실패했습니다.');
    }
  }

  return (
    <PatrolLayout>
      <div className="patrol-login">
        <div className="patrol-login-header">
          <i className="bi bi-fire patrol-login-icon" />
          <h2 className="patrol-login-title">순찰 로그인</h2>
        </div>

        <form className="patrol-login-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="patrol-login-input"
            placeholder="대원번호"
            value={firefighterNumber}
            onChange={(e) => setFirefighterNumber(e.target.value)}
          />
          <input
            type="password"
            className="patrol-login-input"
            placeholder="비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="patrol-login-error">{error}</p>}

          <button type="submit" className="patrol-login-btn">로그인</button>
        </form>
      </div>
    </PatrolLayout>
  );
}

export default PatrolLogin;
