import { createContext, useContext, useState } from 'react';
import { USERS_DB } from '../data/initialData';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState(USERS_DB);

  function login(username, password, role) {
    const found = users.find(
      u => u.username === username && u.password === password && u.role === role
    );
    if (!found) return { success: false, message: 'Username/password salah atau peran tidak sesuai.' };
    setCurrentUser(found);
    return { success: true };
  }

  function logout() {
    setCurrentUser(null);
  }

  function register(name, username, password) {
    if (users.find(u => u.username === username))
      return { success: false, message: 'Username sudah digunakan.' };
    const newUser = { id: 'u' + Date.now(), username, password, role: 'user', name };
    setUsers(prev => [...prev, newUser]);
    return { success: true };
  }

  return (
    <AuthContext.Provider value={{ currentUser, users, setUsers, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
