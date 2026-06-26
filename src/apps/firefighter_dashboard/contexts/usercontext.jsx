import { createContext, useContext, useEffect, useState } from 'react';
import client from '../../../api/client';
import { isLoggedIn } from '../../../api/auth';

export const UserContext = createContext(null);
export const useUser = () => useContext(UserContext)?.user ?? null;
export const useRefreshUser = () => useContext(UserContext)?.refreshUser;

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refreshUser() {
    if (!isLoggedIn()) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const response = await client.get('/auth/me');
      setUser(response.data);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, refreshUser, setUser }}>
      {children}
    </UserContext.Provider>
  );
}