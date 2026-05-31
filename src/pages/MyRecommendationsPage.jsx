import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/apiClient';
import { formatScore } from '../utils/ncfUtils';

export default function MyRecommendationsPage({ orders }) {
  const { currentUser } = useAuth();
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getMyRecommendations()
      .then(setRecs)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">Rekomendasi Personal untuk {currentUser.name}</div>
          <span className="pill pill-gold">✨ NCF Powered</span>
        </div>
        <div className="card-body" style={{ fontSize: '.83rem', color: 'var(--gray4)', lineHeight: 1.75 }}>
          Model <strong style={{ color: 'var(--green)' }}>Neural Collaborative Filtering</strong> telah menganalisis{' '}
          <strong>{orders.length} riwayat pesanan</strong> Anda dan menghasilkan rekomendasi menu berikut yang
          kemungkinan besar akan Anda sukai.
        </div>
      </div>

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Top-10 Menu Untukmu</div>
          <span style={{ fontSize: '.75rem', color: 'var(--gray3)' }}>Diperbarui otomatis</span>
        </div>
        <div className="card-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray4)', fontSize: '.85rem' }}>
              Memuat rekomendasi...
            </div>
          ) : error ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#c0392b', fontSize: '.85rem' }}>
              ⚠️ {error}
            </div>
          ) : recs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray3)', fontSize: '.85rem' }}>
              Belum ada rekomendasi. Mulai pesan menu untuk mendapatkan rekomendasi personal!
            </div>
          ) : (
            <div className="rec-list">
              {recs.map((item, i) => (
                <div key={item.id + i} className="rec-item">
                  <div className={`rec-rank ${i < 3 ? 'gold' : ''}`}>{item.rank}</div>
                  <div className="rec-icon">{item.icon}</div>
                  <div className="rec-details">
                    <div className="rec-name">{item.name}</div>
                    <div className="rec-cat">{item.category} · <span className="mono">{item.code || item.id}</span></div>
                  </div>
                  <div className="rec-score">{formatScore(item.score)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {orders.length > 0 && (
        <div className="page-card">
          <div className="card-header">
            <div className="card-header-title">Riwayat Pesanan Saya ({orders.length})</div>
          </div>
          <div style={{ padding: '.4rem 0' }}>
            {orders.map(o => (
              <div key={o.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '.6rem 1.3rem', borderBottom: '1px solid var(--gray2)', fontSize: '.81rem'
              }}>
                <strong>{o.menuName}</strong>
                <span style={{ color: 'var(--gray3)' }}>{o.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
