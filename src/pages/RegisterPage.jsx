import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage({ onBack }) {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleRegister(e) {
    e.preventDefault();
    setError('');
    if (!name.trim() || !username.trim() || !password.trim()) {
      setError('Lengkapi semua field terlebih dahulu.');
      return;
    }
    setLoading(true);
    try {
      await register(name.trim(), username.trim(), password.trim());
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Registrasi gagal.');
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
            <span>Daftar Akun Baru</span>
          </div>
        </div>

        {success ? (
          <>
            <div style={{
              background: 'var(--green-light)', borderRadius: 10, padding: '1.2rem',
              textAlign: 'center', marginBottom: '1.2rem'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '.5rem' }}>✅</div>
              <p style={{ fontSize: '.85rem', color: 'var(--green-dark)', fontWeight: 600 }}>
                Registrasi berhasil!
              </p>
              <p style={{ fontSize: '.78rem', color: 'var(--gray4)', marginTop: '.3rem' }}>
                Silakan login dengan akun Anda.
              </p>
            </div>
            <button className="btn btn-primary btn-lg" onClick={onBack}>Ke Halaman Login</button>
          </>
        ) : (
          <>
            <div className="register-info">
              Daftar sebagai <strong>User</strong> untuk melihat menu dan mendapatkan rekomendasi personal dari sistem NCF kami.
            </div>

            <form onSubmit={handleRegister}>
              <div className="form-group">
                <label>Nama Lengkap</label>
                <input className="form-input" type="text" placeholder="Nama lengkap Anda"
                  value={name} onChange={e => setName(e.target.value)} disabled={loading} />
              </div>
              <div className="form-group">
                <label>Username</label>
                <input className="form-input" type="text" placeholder="Buat username unik"
                  value={username} onChange={e => setUsername(e.target.value)}
                  autoComplete="username" disabled={loading} />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input className="form-input" type="password" placeholder="Buat password"
                  value={password} onChange={e => setPassword(e.target.value)}
                  autoComplete="new-password" disabled={loading} />
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
                {loading ? 'Memproses...' : 'Daftar Sekarang'}
              </button>
            </form>

            <p className="auth-hint">
              Sudah punya akun? <button onClick={onBack} disabled={loading}>Masuk di sini</button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
