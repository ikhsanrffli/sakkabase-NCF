import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/UI';
import { api } from '../api/apiClient';

export default function DashboardPage({ menus, orders, users }) {
  const { currentUser } = useAuth();
  const isAdmin = currentUser.role === 'admin';

  if (isAdmin) {
    return <AdminDashboard menus={menus} orders={orders} users={users} />;
  }
  return <UserDashboard orders={orders} />;
}

function AdminDashboard({ menus, orders, users }) {
  const [modelStatus, setModelStatus] = useState(null);
  const [retraining, setRetraining] = useState(false);

  useEffect(() => {
    api.getModelStatus().then(setModelStatus).catch(() => {});
  }, []);

  async function handleRetrain() {
    setRetraining(true);
    try {
      await api.retrainModel();
      setModelStatus(s => s ? { ...s, status: 'training' } : { status: 'training' });
    } catch (err) {
      alert('Gagal memulai retrain: ' + err.message);
    } finally {
      setRetraining(false);
    }
  }

  const regUsers = users.filter(u => u.role === 'user');
  const recentOrders = [...orders].reverse().slice(0, 5);

  return (
    <>
      <div className="stats-grid">
        <StatCard label="Total Pengguna"  value={regUsers.length}  sub="User terdaftar"              icon="👥" />
        <StatCard label="Total Menu"      value={menus.length}     sub="Item dalam katalog"           icon="🍽️" />
        <StatCard label="Total Pemesanan" value={orders.length}    sub="Interaksi terekam"            icon="📋" />
        <StatCard
          label="Model NCF"
          value={modelStatus ? (modelStatus.status === 'ready' ? 'Siap' : modelStatus.status === 'training' ? 'Training...' : modelStatus.status) : '—'}
          sub={modelStatus?.hr_at_10 != null ? `HR@10: ${modelStatus.hr_at_10.toFixed(4)}` : 'Neural Collaborative Filtering'}
          icon="🤖"
        />
      </div>

      <div className="dash-2col">
        <div className="page-card">
          <div className="card-header">
            <div className="card-header-title">Pesanan Terbaru</div>
          </div>
          <div>
            {recentOrders.length === 0 ? (
              <div style={{ padding: '1.2rem', textAlign: 'center', color: 'var(--gray3)', fontSize: '.83rem' }}>
                Belum ada pesanan.
              </div>
            ) : recentOrders.map(o => (
              <div key={o.id} style={{
                padding: '.6rem 1.2rem', borderBottom: '1px solid var(--gray2)',
                fontSize: '.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
              }}>
                <span><strong>{o.userName}</strong> — {o.menuName}</span>
                <span style={{ color: 'var(--gray3)', fontSize: '.72rem' }}>{o.date}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="page-card">
          <div className="card-header">
            <div className="card-header-title">Konfigurasi Model NCF</div>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleRetrain}
              disabled={retraining || modelStatus?.status === 'training'}
            >
              {retraining || modelStatus?.status === 'training' ? '⏳ Training...' : '🔄 Retrain'}
            </button>
          </div>
          <div className="card-body" style={{ fontSize: '.82rem', color: 'var(--gray4)', lineHeight: 2 }}>
            <div>📐 <strong>Embedding Dim:</strong> 16</div>
            <div>🧠 <strong>Hidden Layer:</strong> 32 → 16 → 8</div>
            <div>⚡ <strong>Aktivasi:</strong> ReLU + Sigmoid</div>
            <div>📉 <strong>Loss:</strong> Binary Cross-Entropy (BCE)</div>
            <div>🔄 <strong>Optimizer:</strong> Adam (lr = 0.001, wd = 1e-5)</div>
            <div>📦 <strong>Dropout:</strong> 0.3 | Epoch: 50</div>
            <div>🔀 <strong>Dataset Split:</strong> Leave-One-Out</div>
            <div>📊 <strong>Evaluasi:</strong> HR@10 &amp; NDCG@10</div>
            {modelStatus?.hr_at_10 != null && (
              <>
                <hr style={{ border: 'none', borderTop: '1px solid var(--gray2)', margin: '.4rem 0' }} />
                <div>✅ <strong>HR@10:</strong> {modelStatus.hr_at_10.toFixed(4)}</div>
                <div>✅ <strong>NDCG@10:</strong> {modelStatus.ndcg_at_10?.toFixed(4) ?? '—'}</div>
                <div style={{ fontSize: '.72rem', color: 'var(--gray3)' }}>
                  Trained: {modelStatus.trained_at ? new Date(modelStatus.trained_at).toLocaleString('id-ID') : '—'}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

function UserDashboard({ orders }) {
  const { currentUser } = useAuth();
  const recentOrders = [...orders].reverse().slice(0, 4);

  return (
    <>
      <div className="stats-grid">
        <StatCard label="Pesanan Saya"  value={orders.length} sub="Total interaksi"    icon="📋" />
        <StatCard label="Rekomendasi"   value="10"            sub="Top-N menu untukmu" icon="⭐" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div className="page-card" style={{ marginBottom: 0 }}>
          <div className="card-body" style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '.5rem' }}>🛒</div>
            <div style={{ fontSize: '.88rem', fontWeight: 700, color: 'var(--gray5)', marginBottom: '.3rem' }}>Pesan Sekarang</div>
            <div style={{ fontSize: '.75rem', color: 'var(--gray4)', marginBottom: '1rem' }}>Pilih menu favoritmu</div>
            <a
              href="#order-menu"
              onClick={e => { e.preventDefault(); document.dispatchEvent(new CustomEvent('navigate', { detail: 'order-menu' })); }}
              className="btn btn-primary"
              style={{ justifyContent: 'center', width: '100%' }}
            >
              Buka Menu
            </a>
          </div>
        </div>
        <div className="page-card" style={{ marginBottom: 0 }}>
          <div className="card-body" style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '.5rem' }}>⭐</div>
            <div style={{ fontSize: '.88rem', fontWeight: 700, color: 'var(--gray5)', marginBottom: '.3rem' }}>Rekomendasiku</div>
            <div style={{ fontSize: '.75rem', color: 'var(--gray4)', marginBottom: '1rem' }}>AI picks khusus untukmu</div>
            <a
              href="#my-recommendations"
              onClick={e => { e.preventDefault(); document.dispatchEvent(new CustomEvent('navigate', { detail: 'my-recommendations' })); }}
              className="btn btn-gold"
              style={{ justifyContent: 'center', width: '100%' }}
            >
              Lihat Rekomendasi
            </a>
          </div>
        </div>
      </div>

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Riwayat Pesanan Terbaru</div>
        </div>
        {recentOrders.length === 0 ? (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--gray3)', fontSize: '.83rem' }}>
            Belum ada pesanan. Yuk mulai pesan! 🍽️
          </div>
        ) : recentOrders.map(o => (
          <div key={o.id} style={{
            padding: '.65rem 1.2rem', borderBottom: '1px solid var(--gray2)',
            fontSize: '.82rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <strong>{o.menuName}</strong>
            <span style={{ color: 'var(--gray3)', fontSize: '.72rem' }}>{o.date}</span>
          </div>
        ))}
      </div>
    </>
  );
}
