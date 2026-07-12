import { createContext, useContext, useState, useCallback } from 'react';
import { getUnreadNotificationCount } from '../../../api/notifications';

const AlertContext = createContext(null);

export const useAlertCount = () => useContext(AlertContext)?.unreadCount ?? 0;
export const useRefreshAlertCount = () => useContext(AlertContext)?.refreshUnreadCount;

export function AlertProvider({ children }) {
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUnreadCount = useCallback(async () => {
    if (!localStorage.getItem('access_token')) return;
    try {
      const data = await getUnreadNotificationCount();
      setUnreadCount(data.unread_count);
    } catch {
    }
  }, []);

  return (
    <AlertContext.Provider value={{ unreadCount, refreshUnreadCount }}>
      {children}
    </AlertContext.Provider>
  );
}