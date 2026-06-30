import { useState } from 'react';
import { SearchBar, EmptyState, Modal, Pill } from '../components/UI';
import { menuPrice, menuDescription, menuServing, popularityLabel, formatRupiah } from '../utils/menuInfo';

export default function CatalogPage({ menus, orders = [] }) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [selected, setSelected] = useState(null); // menu yang diklik (detail)

  // popularitas: berapa kali menu ini dipesan (dari data pemesanan nyata)
  const orderCount = id => orders.filter(o => o.menuId === id).length;

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
            <div
              key={m.id}
              className="menu-card"
              onClick={() => setSelected(m)}
              style={{ cursor: 'pointer' }}
              title="Klik untuk lihat detail"
            >
              <div className="menu-card-img">{m.icon}</div>
              <div className="menu-card-body">
                <div className="menu-card-cat">{m.category}</div>
                <div className="menu-card-name">{m.name}</div>
                <div style={{
                  fontSize: '.74rem', color: 'var(--gray3)', margin: '.25rem 0 .4rem',
                  display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {menuDescription(m)}
                </div>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <span style={{ fontWeight: 700, color: 'var(--green)', fontSize: '.85rem' }}>
                    {formatRupiah(menuPrice(m))}
                  </span>
                  <span className="menu-card-id">{m.id}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Kartu Detail Menu (muncul saat kartu diklik) */}
      {selected && (
        <Modal title="Detail Menu" onClose={() => setSelected(null)}>
          <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
            <div style={{ fontSize: '3.5rem', lineHeight: 1 }}>{selected.icon}</div>
            <h3 style={{ margin: '.6rem 0 .35rem', fontSize: '1.15rem' }}>{selected.name}</h3>
            <span style={{ display: 'inline-flex', gap: '.4rem', flexWrap: 'wrap', justifyContent: 'center' }}>
              <Pill variant="green">{selected.category}</Pill>
              <Pill variant={popularityLabel(orderCount(selected.id)).variant}>
                ⭐ {popularityLabel(orderCount(selected.id)).text}
              </Pill>
            </span>
          </div>

          <div style={{ fontSize: '.85rem', color: 'var(--gray4)', lineHeight: 1.7 }}>
            <div style={{
              padding: '.8rem 1rem', background: 'var(--gray1)', borderRadius: 10, marginBottom: '.8rem',
            }}>
              {menuDescription(selected)}
            </div>

            <div style={detailRow}>
              <span style={detailLabel}>🏷️ Kode Menu</span>
              <span className="mono">{selected.id}</span>
            </div>
            <div style={detailRow}>
              <span style={detailLabel}>📂 Kategori</span>
              <span>{selected.category}</span>
            </div>
            <div style={detailRow}>
              <span style={detailLabel}>💰 Harga</span>
              <span style={{ fontWeight: 700, color: 'var(--green)' }}>
                {formatRupiah(menuPrice(selected))}
              </span>
            </div>
            <div style={detailRow}>
              <span style={detailLabel}>🍽️ Penyajian</span>
              <span>{menuServing(selected)}</span>
            </div>
            <div style={detailRow}>
              <span style={detailLabel}>📈 Popularitas</span>
              <span><strong>{orderCount(selected.id)}</strong> kali dipesan</span>
            </div>
          </div>

          <div className="modal-actions" style={{ marginTop: '1rem' }}>
            <button className="btn btn-primary" onClick={() => setSelected(null)}>Tutup</button>
          </div>
        </Modal>
      )}
    </>
  );
}

const detailRow = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '.55rem .2rem', borderBottom: '1px solid var(--gray2)',
};
const detailLabel = { color: 'var(--gray3)' };
