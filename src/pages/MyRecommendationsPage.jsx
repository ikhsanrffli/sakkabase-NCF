import { useAuth } from '../context/AuthContext';
import { getNCFRecommendations, formatScore } from '../utils/ncfUtils';

export default function MyRecommendationsPage({ menus, orders }) {
  const { currentUser } = useAuth();
  const recs = getNCFRecommendations(currentUser.id, menus, orders, 10);
  const myOrders = orders.filter(o => o.userId === currentUser.id);

  return (
    <>
      <div className="page-card" style={{ marginBottom: '1rem' }}>
        <div className="card-header">
          <div className="card-header-title">Rekomendasi Personal untuk {currentUser.name}</div>
          <span className="pill pill-gold">✨ NCF Powered</span>
        </div>
        <div className="card-body" style={{ fontSize: '.83rem', color: 'var(--gray4)', lineHeight: 1.75 }}>
          Model <strong style={{ color: 'var(--green)' }}>Neural Collaborative Filtering</strong> telah menganalisis{' '}
          <strong>{myOrders.length} riwayat pesanan</strong> Anda dan menghasilkan rekomendasi menu berikut yang
          kemungkinan besar akan Anda sukai.
        </div>
      </div>

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Top-10 Menu Untukmu</div>
          <span style={{ fontSize: '.75rem', color: 'var(--gray3)' }}>Diperbarui otomatis</span>
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
