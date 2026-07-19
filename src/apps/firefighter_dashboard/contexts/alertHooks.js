import { useContext } from 'react';
import { AlertContext } from './alertContextValue';

export const useAlertCount = () => useContext(AlertContext)?.unreadCount ?? 0;
export const useRefreshAlertCount = () => useContext(AlertContext)?.refreshUnreadCount;
