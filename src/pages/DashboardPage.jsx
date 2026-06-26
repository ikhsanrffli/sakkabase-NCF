import { useAuth } from '../context/AuthContext';
import { StatCard } from '../components/UI';

export default function DashboardPage({ menus, orders, users }) {
  const { currentUser } = useAuth();
  const isAdmin = currentUser.role === 'admin';

  if (isAdmin) {
    const regUsers = users.filter(u => u.role === 'user');
    const recentOrders = [...orders].reverse().slice(0, 5);

    return (
      <>
        <div className="stats-grid">
          <StatCard label="Total Pengguna"  value={regUsers.length}  sub="User terdaftar"       icon="👥" />
          <StatCard label="Total Menu"      value={menus.length}     sub="Item dalam katalog"   icon="🍽️" />
          <StatCard label="Total Pemesanan" value={orders.length}    sub="Interaksi terekam"    icon="📋" />
          <StatCard label="Model NCF"       value="Aktif"            sub="Neural Collaborative Filtering" icon="🤖" />
        </div>

        <div className="dash-2col">
          <div className="page-card">
            <div className="card-header">
              <div className="card-header-title">Pesanan Terbaru</div>
            </div>
            <div>
              {recentOrders.map(o => (
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
            </div>
            <div className="card-body" style={{ fontSize: '.82rem', color: 'var(--gray4)', lineHeight: 2 }}>
              <div>📐 <strong>Embedding Dim:</strong> 32</div>
              <div>🧠 <strong>Hidden Layer:</strong> 64 → 32</div>
              <div>⚡ <strong>Aktivasi:</strong> ReLU + Sigmoid</div>
              <div>📉 <strong>Loss:</strong> Binary Cross-Entropy (BCE)</div>
              <div>🔄 <strong>Optimizer:</strong> Adam (lr = 0.0005)</div>
              <div>📦 <strong>Batch Size:</strong> 256 | Early Stopping</div>
              <div>🔀 <strong>Dataset Split:</strong> Leave-One-Out</div>
              <div>📊 <strong>Hasil Pengujian:</strong> HR@10 = 0,3439 · NDCG@10 = 0,1825</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  /* ── User dashboard ─────────────────────── */
  const myOrders = orders.filter(o => o.userId === currentUser.id);
  const recentMyOrders = [...myOrders].reverse().slice(0, 4);

  return (
    <>
      <div className="stats-grid">
        <StatCard label="Pesanan Saya"  value={myOrders.length} sub="Total interaksi"    icon="📋" />
        <StatCard label="Rekomendasi"   value="10"              sub="Top-N menu untukmu" icon="⭐" />
      </div>

      {/* Quick action buttons */}
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
        {recentMyOrders.length === 0 ? (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--gray3)', fontSize: '.83rem' }}>
            Belum ada pesanan. Yuk mulai pesan! 🍽️
          </div>
        ) : (
          recentMyOrders.map(o => (
            <div key={o.id} style={{
              padding: '.65rem 1.2rem', borderBottom: '1px solid var(--gray2)',
              fontSize: '.82rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <span>
                {menus.find(m => m.id === o.menuId)?.icon}{' '}
                <strong>{o.menuName}</strong>
                {o.qty > 1 && <span style={{ color: 'var(--green)', marginLeft: '.3rem' }}>×{o.qty}</span>}
              </span>
              <span style={{ color: 'var(--gray3)', fontSize: '.72rem' }}>{o.date}</span>
            </div>
          ))
        )}
      </div>
    </>
  );
}
