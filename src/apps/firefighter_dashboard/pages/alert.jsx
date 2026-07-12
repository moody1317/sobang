import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../layouts/dashboardlayout';
import { useAlertCount, useRefreshAlertCount } from '../contexts/alertcontext';
import { getNotifications, markNotificationRead } from '../../../api/notifications';
import './alert.css';

function toRelativeTime(isoString) {
  const diffMinutes = Math.floor((Date.now() - new Date(isoString).getTime()) / 60000);
  if (diffMinutes < 1) return '방금 전';
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return '어제';
  return `${diffDays}일 전`;
}

const PAGE_SIZE = 20;

function toAlert(notification) {
  return {
    id: notification.id,
    level: notification.level,
    location: notification.title,
    time: toRelativeTime(notification.created_at),
    message: notification.message,
    read: notification.is_read,
  };
}

function Alert() {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const unreadCount = useAlertCount();
  const refreshAlertCount = useRefreshAlertCount();

  const fetchAlerts = useCallback(async (offset) => {
    if (offset === 0) setLoading(true);
    else setLoadingMore(true);
    setError(null);
    try {
      const data = await getNotifications({ limit: PAGE_SIZE, offset });
      setAlerts((prev) => (offset === 0 ? data.items.map(toAlert) : [...prev, ...data.items.map(toAlert)]));
      setTotal(data.total);
    } catch {
      setError('알림을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts(0);
  }, [fetchAlerts]);

  function loadMore() {
    fetchAlerts(alerts.length);
  }

  async function markAllRead() {
    const unreadIds = alerts.filter((a) => !a.read).map((a) => a.id);
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
    await Promise.all(unreadIds.map((id) => markNotificationRead(id)));
    refreshAlertCount?.();
  }

  async function markRead(id) {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, read: true } : a)));
    await markNotificationRead(id);
    refreshAlertCount?.();
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
          {loading ? (
            <div className="alert-item">불러오는 중…</div>
          ) : error ? (
            <div className="alert-item">{error}</div>
          ) : alerts.length === 0 ? (
            <div className="alert-item">알림이 없습니다.</div>
          ) : (
            alerts.map((alert) => (
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
            ))
          )}
        </div>

        {!loading && !error && alerts.length < total && (
          <button className="alert-mark-all-btn" onClick={loadMore} disabled={loadingMore}>
            {loadingMore ? '불러오는 중…' : '더 보기'}
          </button>
        )}
      </div>
    </DashboardLayout>
  );
}

export default Alert;