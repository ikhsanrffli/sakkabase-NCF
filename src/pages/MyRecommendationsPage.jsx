import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getNCFRecommendations, formatScore } from '../utils/ncfUtils';

// Alamat backend FastAPI (jalankan: cd backend && uvicorn main:app --port 8000)
const API_BASE = 'http://localhost:8000';

export default function MyRecommendationsPage({ menus, orders }) {
  const { currentUser } = useAuth();
  const myOrders = orders.filter(o => o.userId === currentUser.id);
  const orderCodes = myOrders.map(o => o.menuId);

  const [resp, setResp] = useState(null);
  const [status, setStatus] = useState('loading'); // loading | ok | offline | insufficient

  useEffect(() => {
    if (orderCodes.length < 2) { setStatus('insufficient'); return; }
    let aktif = true;
    setStatus('loading');
    fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ orders: orderCodes, evaluate: true, userName: currentUser.name }),
    })
      .then(r => r.json())
      .then(d => { if (aktif) { setResp(d); setStatus('ok'); } })
      .catch(() => { if (aktif) setStatus('offline'); });
    return () => { aktif = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser.id, orderCodes.length]);

  // Daftar rekomendasi: dari backend (model asli) bila tersedia, jika tidak fallback lokal.
  const recs = (status === 'ok' && resp?.top10?.length)
    ? resp.top10.map(r => ({ id: r.menuId, name: r.name, category: r.category, icon: r.icon, score: r.score }))
    : getNCFRecommendations(currentUser.id, menus, orders, 10);

  const ev = resp?.evaluation;

  return (
    <>
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">Rekomendasi Personal untuk {currentUser.name}</div>
          <span className="pill pill-gold">✨ NCF Powered</span>
        </div>
        <div className="card-body" style={{ fontSize: '.83rem', color: 'var(--gray4)', lineHeight: 1.75 }}>
          Model <strong style={{ color: 'var(--green)' }}>Neural Collaborative Filtering</strong> menganalisis{' '}
          <strong>{myOrders.length} riwayat pesanan</strong> Anda untuk menghasilkan rekomendasi berikut.
        </div>
      </div>

      {/* Status koneksi backend / data */}
      {status === 'loading' && (
        <div className="page-card" style={{ marginBottom: '1rem' }}>
          <div className="card-body" style={{ fontSize: '.82rem', color: 'var(--gray4)' }}>
            ⏳ Menghitung rekomendasi & evaluasi dari model NCF...
          </div>
        </div>
      )}
      {status === 'insufficient' && (
        <div className="page-card" style={{ marginBottom: '1rem' }}>
          <div className="card-body" style={{ fontSize: '.82rem', color: 'var(--gray4)' }}>
            ℹ️ Pesan minimal <strong>2 menu</strong> untuk menjalankan pengujian NCF (1 untuk profil, 1 disembunyikan sebagai uji).
          </div>
        </div>
      )}
      {status === 'offline' && (
        <div className="page-card" style={{ marginBottom: '1rem' }}>
          <div className="card-body" style={{ fontSize: '.82rem', color: 'var(--danger)' }}>
            ⚠️ Backend pengujian (FastAPI) belum aktif — menampilkan rekomendasi tanpa evaluasi HR/NDCG.<br />
            Jalankan: <span className="mono">cd backend &amp;&amp; uvicorn main:app --port 8000</span>
          </div>
        </div>
      )}

      {/* Panel hasil evaluasi HR@10 & NDCG@10 (hanya saat pengujian user) */}
      {ev && (
        <div className="page-card" style={{ marginBottom: '1rem' }}>
          <div className="card-header">
            <div className="card-header-title">Hasil Pengujian (Leave-One-Out)</div>
            <span className={`pill ${ev.hit ? 'pill-green' : 'pill-gold'}`}>
              {ev.hit ? '✓ HIT' : '✗ MISS'}
            </span>
          </div>
          <div className="card-body" style={{ fontSize: '.84rem', lineHeight: 1.9 }}>
            <div>
              🎯 Menu uji (disembunyikan): <strong>{ev.groundTruthName}</strong>{' '}
              <span className="mono">({ev.groundTruth})</span>
            </div>
            <div>
              📍 Posisi di hasil prediksi: peringkat <strong>{ev.rank ?? '—'}</strong>
              {ev.hit ? ' (masuk Top-10)' : ' (di luar Top-10)'}
            </div>
            <div style={{ display: 'flex', gap: '2rem', marginTop: '.4rem' }}>
              <div>📊 <strong>HR@10</strong> = {ev.hr_at_10}</div>
              <div>📈 <strong>NDCG@10</strong> = {ev.ndcg_at_10}</div>
            </div>
            <div style={{ fontSize: '.74rem', color: 'var(--gray3)', marginTop: '.4rem' }}>
              Untuk satu pengguna, HR/NDCG bernilai hit (1) atau miss (0). Rata-rata seluruh
              data uji menghasilkan HR@10 = 0,3500 dan NDCG@10 = 0,1822.
            </div>
          </div>
        </div>
      )}

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Top-10 Menu Untukmu</div>
          <span className="pill pill-green">Top-10 NCF</span>
        </div>
        <div className="card-body">
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
        </div>
      </div>

      {myOrders.length > 0 && (
        <div className="page-card">
          <div className="card-header">
            <div className="card-header-title">Riwayat Pesanan Saya ({myOrders.length})</div>
          </div>
          <div style={{ padding: '.4rem 0' }}>
            {myOrders.map(o => (
              <div key={o.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '.6rem 1.3rem', borderBottom: '1px solid var(--gray2)', fontSize: '.81rem'
              }}>
                <span>
                  {menus.find(m => m.id === o.menuId)?.icon}{' '}
                  <strong>{o.menuName}</strong>
                </span>
                <span style={{ color: 'var(--gray3)' }}>{o.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
