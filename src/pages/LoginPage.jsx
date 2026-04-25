import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage({ onRegister }) {
  const { login } = useAuth();
  const [role, setRole] = useState('admin');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  function handleLogin(e) {
    e.preventDefault();
    setError('');
    const result = login(username.trim(), password.trim(), role);
    if (!result.success) setError(result.message);
  }

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-brand-icon">S</div>
          <div className="auth-brand-text">
            Sakka Base
            <span>Coffee &amp; Barber — NCF System</span>
          </div>
        </div>

        <h2 className="auth-title">Selamat Datang</h2>
        <p className="auth-sub">Sistem Rekomendasi Menu Neural Collaborative Filtering</p>

        <div className="role-tabs">
          <button
            className={`role-tab ${role === 'admin' ? 'active' : ''}`}
            onClick={() => setRole('admin')}
          >
            👤 Admin
          </button>
          <button
            className={`role-tab ${role === 'user' ? 'active' : ''}`}
            onClick={() => setRole('user')}
          >
            🙋 User
          </button>
        </div>

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Username</label>
            <input
              className="form-input"
              type="text"
              placeholder="Masukkan username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              className="form-input"
              type="password"
              placeholder="Masukkan password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div style={{
              background: '#fdf0f0', color: '#c0392b', borderRadius: 8,
              padding: '.6rem .9rem', fontSize: '.78rem', marginBottom: '.8rem',
              border: '1px solid #f5c6c6'
            }}>
              ⚠️ {error}
            </div>
          )}

          <button type="submit" className="btn btn-login-main btn-lg">Masuk</button>
        </form>

        <p className="auth-hint">
          Belum punya akun?{' '}
          <button onClick={onRegister}>Daftar di sini</button>
        </p>
        <p className="auth-footer-hint">
          Admin: <strong>admin</strong> / <strong>admin123</strong> &nbsp;|&nbsp;
          User: <strong>user1</strong> / <strong>user123</strong>
        </p>
      </div>
    </div>
  );
}
