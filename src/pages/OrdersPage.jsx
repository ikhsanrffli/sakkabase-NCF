import { useState } from 'react';
import { SearchBar, EmptyState } from '../components/UI';

const FILTERS = ['Semua', 'Registered', 'Historical'];

export default function OrdersPage({ orders, users }) {
  const [search, setSearch]   = useState('');
  const [filter, setFilter]   = useState('Semua');

  const usersById = Object.fromEntries(users.map(u => [u.id, u]));

  const filtered = orders.filter(o => {
    const source = usersById[o.userId]?.source || 'historical';
    if (filter === 'Registered' && source !== 'registered') return false;
    if (filter === 'Historical' && source !== 'historical')  return false;
    return (
      (o.userName || '').toLowerCase().includes(search.toLowerCase()) ||
      (o.menuName || '').toLowerCase().includes(search.toLowerCase()) ||
      String(o.id).includes(search)
    );
  });

  const counts = {
    Semua:      orders.length,
    Registered: orders.filter(o => (usersById[o.userId]?.source || 'historical') === 'registered').length,
    Historical: orders.filter(o => (usersById[o.userId]?.source || 'historical') === 'historical').length,
  };

  return (
    <div className="page-card">
      <div className="card-header">
        <div className="card-header-title">Riwayat Pemesanan ({filtered.length} data)</div>
        <SearchBar value={search} onChange={setSearch} placeholder="Cari pemesanan..." />
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: '.4rem', padding: '.75rem 1.3rem 0', borderBottom: '1px solid var(--gray2)', marginBottom: 0 }}>
        {FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '.35rem 1rem',
              border: 'none',
              borderBottom: filter === f ? '2.5px solid var(--green)' : '2.5px solid transparent',
              background: 'none',
              color: filter === f ? 'var(--green)' : 'var(--gray4)',
              fontWeight: filter === f ? 700 : 400,
              fontSize: '.82rem',
              cursor: 'pointer',
              fontFamily: 'var(--font)',
              paddingBottom: '.5rem',
              transition: 'all .15s',
            }}
          >
            {f}
            <span style={{
              marginLeft: '.35rem',
              background: filter === f ? 'var(--green)' : 'var(--gray2)',
              color: filter === f ? 'white' : 'var(--gray4)',
              borderRadius: 99, padding: '1px 7px',
              fontSize: '.72rem', fontWeight: 700,
            }}>
              {counts[f]}
            </span>
          </button>
        ))}
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>No</th>
              <th>ID</th>
              <th>Pengguna</th>
              <th>Menu</th>
              <th>Tanggal</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={5}><EmptyState icon="📋" message="Tidak ada data pemesanan." /></td></tr>
            ) : filtered.map((o, i) => (
              <tr key={`${o.id}-${o.menuId}-${i}`}>
                <td style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                <td><span className="mono">{o.id}</span></td>
                <td style={{ color: (usersById[o.userId]?.source || 'historical') === 'registered' ? 'var(--green-dark)' : 'var(--gray4)' }}>
                  {o.userName}
                </td>
                <td>{o.menuName}</td>
                <td style={{ color: 'var(--gray4)' }}>{o.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
