import { useState } from 'react';
import { SearchBar, EmptyState, Pill } from '../components/UI';

export default function OrdersPage({ orders, users, menus }) {
  const [search, setSearch] = useState('');

  const filtered = orders.filter(o =>
    (o.userName || '').toLowerCase().includes(search.toLowerCase()) ||
    (o.menuName || '').toLowerCase().includes(search.toLowerCase()) ||
    String(o.id).includes(search)
  );

  return (
    <div className="page-card">
      <div className="card-header">
        <div className="card-header-title">Riwayat Pemesanan ({orders.length} data)</div>
        <SearchBar value={search} onChange={setSearch} placeholder="Cari pemesanan..." />
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
              <th>Label</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={6}><EmptyState icon="📋" message="Tidak ada data pemesanan." /></td></tr>
            ) : filtered.map((o, i) => (
              <tr key={o.id}>
                <td style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                <td><span className="mono">{o.id}</span></td>
                <td>{o.userName}</td>
                <td>{o.menuName}</td>
                <td style={{ color: 'var(--gray4)' }}>{o.date}</td>
                <td><Pill variant="green">1 (positif)</Pill></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
