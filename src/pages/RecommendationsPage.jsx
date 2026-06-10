import { useState, useEffect } from 'react';
import { api } from '../api/apiClient';
import { formatScore } from '../utils/ncfUtils';

export default function RecommendationsPage({ users, orders, menus }) {
  const regUsers = users.filter(u => u.source === 'registered');
  const [selectedUserId, setSelectedUserId] = useState(regUsers[0]?.id ?? '');
  const [recs, setRecs] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [recsError, setRecsError] = useState('');
  const [retraining, setRetraining] = useState(false);
  const [retrainMsg, setRetrainMsg] = useState('');

  useEffect(() => {
    if (!selectedUserId) return;
    setRecs([]);
    setRecsError('');
    setRecsLoading(true);
    api.getUserRecommendations(selectedUserId)
      .then(setRecs)
      .catch(e => setRecsError(e.message))
      .finally(() => setRecsLoading(false));
  }, [selectedUserId]);

  async function handleRetrain() {
    setRetraining(true);
    setRetrainMsg('');
    try {
      const res = await api.retrainModel();
      setRetrainMsg(`✅ Retrain dimulai (status_id: ${res.status_id}). Proses berjalan di background.`);
    } catch (err) {
      setRetrainMsg('⚠️ ' + err.message);
    } finally {
      setRetraining(false);
    }
  }

  const selectedUser = users.find(u => u.id === selectedUserId);
  const userOrders = orders.filter(o => o.userId === selectedUserId);

  return (
    <>
      {/* Retrain section */}
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">🤖 Model NCF</div>
          <button
            className="btn btn-primary"
            onClick={handleRetrain}
            disabled={retraining}
          >
            {retraining ? '⏳ Memproses...' : '🔄 Retrain Model'}
          </button>
        </div>
        {retrainMsg && (
          <div className="card-body" style={{ fontSize: '.83rem', color: 'var(--gray4)', paddingTop: 0 }}>
            {retrainMsg}
          </div>
        )}
      </div>

      {/* User selector */}
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">Pilih Pengguna</div>
          <select
            className="form-select"
            style={{ minWidth: 220, maxWidth: 320 }}
            value={selectedUserId}
            onChange={e => setSelectedUserId(Number(e.target.value))}
          >
            {regUsers.map(u => (
              <option key={u.id} value={u.id}>{u.name} ({u.username})</option>
            ))}
          </select>
        </div>
      </div>

      {/* Recommendations */}
      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">
            Top-10 Rekomendasi — {selectedUser?.name || '—'}
          </div>
          <span className="pill pill-green">NCF · HR@10 &amp; NDCG@10</span>
        </div>
        <div className="card-body">
          {recsLoading ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray4)', fontSize: '.85rem' }}>
              Memuat rekomendasi...
            </div>
          ) : recsError ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#c0392b', fontSize: '.85rem' }}>
              ⚠️ {recsError}
            </div>
          ) : recs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray3)', fontSize: '.85rem' }}>
              Belum ada rekomendasi untuk pengguna ini.
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

      {/* Order history */}
      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Riwayat Pesanan — {selectedUser?.name}</div>
        </div>
        <div style={{ padding: '.5rem 0' }}>
          {userOrders.length === 0 ? (
            <div style={{ padding: '1.2rem', color: 'var(--gray3)', fontSize: '.82rem', textAlign: 'center' }}>
              Pengguna ini belum memiliki riwayat pesanan.
            </div>
          ) : userOrders.map(o => (
            <div key={o.id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '.6rem 1.3rem', borderBottom: '1px solid var(--gray2)',
              fontSize: '.81rem'
            }}>
              <strong>{o.menuName}</strong>
              <span style={{ color: 'var(--gray3)' }}>{o.date}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
