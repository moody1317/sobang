import { useContext } from 'react';
import { UserContext } from './userContextValue';

export const useUser = () => useContext(UserContext)?.user ?? null;
export const useRefreshUser = () => useContext(UserContext)?.refreshUser;
