import { useState, useCallback } from 'react';
import { getUnreadNotificationCount } from '../../../api/notifications';
import { AlertContext } from './alertContextValue';

export function AlertProvider({ children }) {
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUnreadCount = useCallback(async () => {
    if (!localStorage.getItem('access_token')) return;
    try {
      const data = await getUnreadNotificationCount();
      setUnreadCount(data.unread_count);
    } catch {
      // 배지 갱신 실패는 조용히 무시
    }
  }, []);

  return (
    <AlertContext.Provider value={{ unreadCount, refreshUnreadCount }}>
      {children}
    </AlertContext.Provider>
  );
}