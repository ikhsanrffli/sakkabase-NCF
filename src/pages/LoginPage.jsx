import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage({ onRegister }) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setError('');
    if (!username.trim() || !password.trim()) { setError('Username dan password wajib diisi.'); return; }
    setLoading(true);
    try {
      await login(username.trim(), password.trim());
    } catch (err) {
      setError(err.message || 'Login gagal, periksa username dan password.');
    } finally {
      setLoading(false);
    }
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
              disabled={loading}
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
              disabled={loading}
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

          <button type="submit" className="btn btn-login-main btn-lg" disabled={loading}>
            {loading ? 'Memuat...' : 'Masuk'}
          </button>
        </form>

        <p className="auth-hint">
          Belum punya akun?{' '}
          <button onClick={onRegister} disabled={loading}>Daftar di sini</button>
        </p>
        <p className="auth-footer-hint">
          Admin: <strong>admin</strong> / <strong>admin123</strong>
        </p>
      </div>
    </div>
  );
}
