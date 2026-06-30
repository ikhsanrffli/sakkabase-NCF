import { useState, useEffect } from 'react';
import { getNCFRecommendations, formatScore } from '../utils/ncfUtils';
import { API_BASE } from '../utils/api';

export default function RecommendationsPage({ menus, orders, users }) {
  const regUsers = users.filter(u => u.role === 'user');
  const [selectedUserId, setSelectedUserId] = useState(regUsers[0]?.id || '');
  const [recs, setRecs] = useState([]);

  const selectedUser = users.find(u => u.id === selectedUserId);

  // Ambil Top-10 dari model NCF (backend) untuk user terpilih; fallback lokal bila offline.
  useEffect(() => {
    if (!selectedUserId) { setRecs([]); return; }
    const codes = orders.filter(o => o.userId === selectedUserId).map(o => o.menuId);
    let aktif = true;
    if (codes.length === 0) {
      setRecs(getNCFRecommendations(selectedUserId, menus, orders, 10));
      return;
    }
    fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ orders: codes, evaluate: false, userName: selectedUser?.name }),
    })
      .then(r => r.json())
      .then(d => {
        if (!aktif) return;
        if (d?.top10?.length) {
          setRecs(d.top10.map(r => ({ id: r.menuId, name: r.name, category: r.category, icon: r.icon, score: r.score })));
        } else {
          setRecs(getNCFRecommendations(selectedUserId, menus, orders, 10));
        }
      })
      .catch(() => { if (aktif) setRecs(getNCFRecommendations(selectedUserId, menus, orders, 10)); });
    return () => { aktif = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUserId, orders]);

  return (
    <>
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">Pilih Pengguna</div>
          <select
            className="form-select"
            style={{ minWidth: 220, maxWidth: 320 }}
            value={selectedUserId}
            onChange={e => setSelectedUserId(e.target.value)}
          >
            {regUsers.map(u => (
              <option key={u.id} value={u.id}>{u.name} ({u.username})</option>
            ))}
          </select>
        </div>
      </div>

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">
            Top-10 Rekomendasi — {selectedUser?.name || '—'}
          </div>
          <span className="pill pill-green">Top-10 NCF</span>
        </div>
        <div className="card-body">
          {recs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray3)' }}>
              Pilih pengguna untuk melihat rekomendasi.
            </div>
          ) : (
            <div className="rec-list">
              {recs.map((item, i) => (
                <div key={item.id} className="rec-item">
                  <div className={`rec-rank ${i < 3 ? 'gold' : ''}`}>{i + 1}</div>
                  <div className="rec-icon">{item.icon}</div>
                  <div className="rec-details">
                    <div className="rec-name">{item.name}</div>
                    <div className="rec-cat">{item.category} · <span className="mono">{item.id}</span></div>
                  </div>
                  <div className="rec-score">{formatScore(item.score)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Riwayat Pesanan — {selectedUser?.name}</div>
        </div>
        <div style={{ padding: '.5rem 0' }}>
          {orders.filter(o => o.userId === selectedUserId).length === 0 ? (
            <div style={{ padding: '1.2rem', color: 'var(--gray3)', fontSize: '.82rem', textAlign: 'center' }}>
              Pengguna ini belum memiliki riwayat pesanan.
            </div>
          ) : orders.filter(o => o.userId === selectedUserId).map(o => (
            <div key={o.id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '.6rem 1.3rem', borderBottom: '1px solid var(--gray2)',
              fontSize: '.81rem'
            }}>
              <span>{menus.find(m => m.id === o.menuId)?.icon} <strong>{o.menuName}</strong></span>
              <span style={{ color: 'var(--gray3)' }}>{o.date}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
