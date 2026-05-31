import { createContext, useContext, useState, useEffect } from 'react';
import { api, getToken } from '../api/apiClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (getToken()) {
      api.getMe()
        .then(u => setCurrentUser(u))
        .catch(() => api.logout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(username, password) {
    await api.login(username, password);
    const user = await api.getMe();
    setCurrentUser(user);
  }

  function logout() {
    api.logout();
    setCurrentUser(null);
  }

  async function register(nama_lengkap, username, password) {
    await api.register(nama_lengkap, username, password);
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', fontSize: '1rem', color: '#888', fontFamily: 'sans-serif'
      }}>
        Memuat...
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ currentUser, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
