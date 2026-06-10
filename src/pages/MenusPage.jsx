import { useState } from 'react';
import { SearchBar, EmptyState, Pill } from '../components/UI';

export default function MenusPage({ menus }) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  const categories = ['', ...new Set(menus.map(m => m.category))].sort();

  const filtered = menus.filter(m =>
    (!category || m.category === category) &&
    (m.name.toLowerCase().includes(search.toLowerCase()) ||
     m.category.toLowerCase().includes(search.toLowerCase()) ||
     (m.code || '').toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="page-card">
      <div className="card-header">
        <div className="card-header-title">Katalog Menu ({menus.length} item)</div>
        <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <SearchBar value={search} onChange={setSearch} placeholder="Cari menu..." />
          <select
            className="form-select"
            style={{ width: 'auto', minWidth: 150 }}
            value={category}
            onChange={e => setCategory(e.target.value)}
          >
            {categories.map(c => <option key={c} value={c}>{c || 'Semua Kategori'}</option>)}
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr><th>No</th><th>Kode</th><th>Nama Menu</th><th>Kategori</th></tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={4}><EmptyState icon="🍽️" message="Tidak ada menu ditemukan." /></td></tr>
            ) : filtered.map((m, i) => (
              <tr key={m.id + i}>
                <td style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                <td><span className="mono">{m.code || m.id}</span></td>
                <td><span style={{ marginRight: '.4rem' }}>{m.icon}</span><strong>{m.name}</strong></td>
                <td><Pill variant="gold">{m.category}</Pill></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
