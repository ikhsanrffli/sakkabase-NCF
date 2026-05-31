import { useState } from 'react';
import { SearchBar, EmptyState } from '../components/UI';

export default function CatalogPage({ menus }) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  const categories = ['', ...new Set(menus.map(m => m.category))];

  const filtered = menus.filter(m =>
    (!category || m.category === category) &&
    (m.name.toLowerCase().includes(search.toLowerCase()) ||
     m.category.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <>
      <div className="filter-bar">
        <SearchBar value={search} onChange={setSearch} placeholder="Cari menu..." />
        <select
          className="form-select"
          style={{ width: 'auto', minWidth: 150 }}
          value={category}
          onChange={e => setCategory(e.target.value)}
        >
          {categories.map(c => (
            <option key={c} value={c}>{c || 'Semua Kategori'}</option>
          ))}
        </select>
        <span style={{ fontSize: '.78rem', color: 'var(--gray4)', marginLeft: 'auto' }}>
          {filtered.length} menu ditemukan
        </span>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon="🔍" message="Tidak ada menu yang sesuai pencarian." />
      ) : (
        <div className="menu-grid">
          {filtered.map(m => (
            <div key={m.id} className="menu-card">
              <div className="menu-card-img">{m.icon}</div>
              <div className="menu-card-body">
                <div className="menu-card-cat">{m.category}</div>
                <div className="menu-card-name">{m.name}</div>
                <div className="menu-card-id">{m.code || m.id}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
