import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import MainLayout from './components/MainLayout';
import { useState } from 'react';

function AppContent() {
  const { currentUser } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (!currentUser) {
    if (showRegister) return <RegisterPage onBack={() => setShowRegister(false)} />;
    return <LoginPage onRegister={() => setShowRegister(true)} />;
  }
  return <MainLayout />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
