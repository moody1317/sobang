import { useState, useEffect } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import { useSetAlertCount } from '../contexts/alertcontext';
import './alert.css';

const MOCK_ALERTS = [
  {
    id: 1,
    level: '위험',
    location: '중앙동',
    time: '18분 전',
    message: '최근 30일 출동 급증으로 위험 스코어가 84→88로 상승했습니다.',
    read: false,
  },
  {
    id: 2,
    level: '특보',
    location: '관할 전역',
    time: '1시간 전',
    message: '건조주의보 발효 — 화재 가중치가 일시 상향됩니다.',
    read: false,
  },
  {
    id: 3,
    level: '경계',
    location: '탑대성동',
    time: '3시간 전',
    message: '위험물 취급시설 점검 기한이 3일 남았습니다.',
    read: false,
  },
  {
    id: 4,
    level: '주의',
    location: '미원면',
    time: '어제',
    message: '주말 등산객 증가 예상 — 산악 구조 대비가 필요합니다.',
    read: true,
  },
  {
    id: 5,
    level: '경계',
    location: '금천동',
    time: '2일 전',
    message: '심야 시간대 화재 출동 비중이 상승 추세입니다.',
    read: true,
  },
  {
    id: 6,
    level: '안전',
    location: '산남동',
    time: '3일 전',
    message: '위험 스코어가 62→58로 하락해 경계에서 주의로 변경되었습니다.',
    read: true,
  },
];

function Alert() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS);
  const setAlertCount = useSetAlertCount();

  const unreadCount = alerts.filter((a) => !a.read).length;

  useEffect(() => {
    setAlertCount?.(unreadCount);
  }, [unreadCount, setAlertCount]);

  function markAllRead() {
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
  }

  function markRead(id) {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, read: true } : a)));
  }

  return (
    <DashboardLayout>
      <div className="alert-page">
        <div className="alert-header">
          <span className="alert-unread-summary">
            {unreadCount > 0 ? (
              <><span className="alert-unread-count">{unreadCount}건</span>의 읽지 않은 알림이 있습니다</>
            ) : (
              '모든 알림을 확인했습니다'
            )}
          </span>
          {unreadCount > 0 && (
            <button className="alert-mark-all-btn" onClick={markAllRead}>
              모두 읽음 표시
            </button>
          )}
        </div>

        <div className="alert-list">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`alert-item alert-item--${alert.level}${!alert.read ? ' alert-item--unread' : ''}`}
              onClick={() => markRead(alert.id)}
            >
              <div className={`alert-icon-wrap alert-icon-wrap--${alert.level}`}>
                <i className="bi bi-exclamation-triangle-fill" />
              </div>
              <div className="alert-body">
                <div className="alert-top">
                  <span className={`alert-badge alert-badge--${alert.level}`}>{alert.level}</span>
                  <span className="alert-location">{alert.location}</span>
                  <span className="alert-time">{alert.time}</span>
                </div>
                <p className="alert-message">{alert.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}

export default Alert;
