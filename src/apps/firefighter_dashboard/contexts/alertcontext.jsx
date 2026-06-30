import { createContext, useContext, useState } from 'react';

const AlertContext = createContext(null);

export const useAlertCount = () => useContext(AlertContext)?.unreadCount ?? 0;
export const useSetAlertCount = () => useContext(AlertContext)?.setUnreadCount;

export function AlertProvider({ children }) {
  const [unreadCount, setUnreadCount] = useState(3); // MOCK_ALERTS 미읽음 초기값
  return (
    <AlertContext.Provider value={{ unreadCount, setUnreadCount }}>
      {children}
    </AlertContext.Provider>
  );
}
