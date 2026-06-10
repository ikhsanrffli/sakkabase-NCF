import { useState } from 'react';
import { SearchBar, EmptyState } from '../components/UI';

function baseName(name) {
  return name
    .replace(/\s*\/\s*(HOT LARGE|HOT REGULAR|COLD LARGE|COLD REGULAR|HOT|COLD|LARGE|REGULAR|SMALL|50K|25K|\d+\s*ML|\d+\s*GR)\s*$/i, '')
    .trim();
}

function variantLabel(name) {
  const m = name.match(/\/\s*(.+)$/);
  return m ? m[1].trim() : null;
}

// ── Detail view ───────────────────────────────────────────────────────────────
function MenuDetail({ menu, menus, onBack }) {
  const base     = baseName(menu.name);
  const variants = menus.filter(m => m.category === menu.category && baseName(m.name) === base);
  const related  = menus
    .filter(m => m.category === menu.category && m.id !== menu.id && baseName(m.name) !== base)
    .slice(0, 6);
  const hasVariants = variants.length > 1;

  const divider = <div style={{ borderTop: '1px solid var(--gray2)', margin: '1.25rem 0' }} />;

  return (
    <div>
      {/* Back */}
      <button
        onClick={onBack}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--green)', fontWeight: 600, fontSize: '.85rem',
          display: 'flex', alignItems: 'center', gap: '.35rem',
          marginBottom: '1.2rem', padding: 0, fontFamily: 'var(--font)',
        }}
      >
        ← Kembali ke Lihat Menu
      </button>

      {/* ── Main detail card ── */}
      <div style={{
        background: 'white', borderRadius: 16, border: '1px solid var(--gray2)',
        padding: '1.75rem 2rem', marginBottom: '1.2rem',
      }}>

        {/* Header: text left, icon right */}
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--green)', letterSpacing: '.05em', marginBottom: '.35rem' }}>
              {menu.category.toUpperCase()}
              <span style={{ color: 'var(--gray3)', fontWeight: 400 }}> • {menu.id}</span>
            </div>
            <h2 style={{ fontSize: '1.55rem', fontWeight: 800, color: 'var(--gray5)', margin: '0 0 .6rem', lineHeight: 1.2 }}>
              {menu.name}
            </h2>
            {menu.keterangan && (
              <p style={{ fontSize: '.83rem', color: 'var(--gray4)', margin: 0, lineHeight: 1.6 }}>
                {menu.keterangan}
              </p>
            )}
          </div>
          <div style={{
            fontSize: '4.5rem', lineHeight: 1,
            background: 'linear-gradient(135deg, #f6faf7, #edf7f0)',
            borderRadius: 16, padding: '1rem 1.2rem',
            flexShrink: 0,
          }}>
            {menu.icon}
          </div>
        </div>

        {divider}

        {/* Harga satuan + Kode */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.75rem', marginBottom: 0 }}>
          <div>
            <div style={{ fontSize: '.7rem', color: 'var(--gray3)', marginBottom: '.3rem' }}>Harga satuan</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--gray5)' }}>
              {menu.price > 0 ? `Rp ${menu.price.toLocaleString('id-ID')}` : '—'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '.7rem', color: 'var(--gray3)', marginBottom: '.3rem' }}>Kategori</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--gray5)' }}>{menu.category}</div>
          </div>
        </div>

        {/* Size / variant options */}
        {hasVariants && (
          <>
            {divider}
            <div style={{ fontSize: '.83rem', fontWeight: 700, color: 'var(--gray5)', marginBottom: '.75rem' }}>
              Pilihan ukuran
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(variants.length, 4)}, 1fr)`, gap: '.6rem' }}>
              {variants.map(v => {
                const label    = variantLabel(v.name) || v.name;
                const isActive = v.id === menu.id;
                return (
                  <div
                    key={v.id}
                    onClick={() => onBack(v)}
                    style={{
                      background: isActive ? 'var(--green-light)' : 'var(--gray1)',
                      border: isActive ? '1.5px solid var(--green)' : '1.5px solid transparent',
                      borderRadius: 12, padding: '1rem 1.1rem',
                      cursor: 'pointer', transition: 'all .15s',
                    }}
                  >
                    <div style={{ fontSize: '.78rem', fontWeight: 700, color: isActive ? 'var(--green-dark)' : 'var(--gray4)', marginBottom: '.3rem' }}>
                      {label}
                    </div>
                    {v.price > 0 && (
                      <div style={{ fontSize: '.9rem', fontWeight: 700, color: isActive ? 'var(--green)' : 'var(--gray5)' }}>
                        Rp {v.price.toLocaleString('id-ID')}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* ── Menu Lainnya ── */}
      {related.length > 0 && (
        <div style={{ background: 'white', borderRadius: 16, border: '1px solid var(--gray2)', padding: '1.5rem 2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem', marginBottom: '1.1rem' }}>
            <span style={{ fontSize: '.72rem', fontWeight: 800, color: 'var(--gray3)', letterSpacing: '.1em', textTransform: 'uppercase' }}>
              Menu Lainnya
            </span>
            <span style={{
              background: '#e74c3c', color: 'white', borderRadius: 99,
              width: 20, height: 20, fontSize: '.65rem', fontWeight: 800,
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {related.length}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: '.75rem' }}>
            {related.map(m => (
              <div
                key={m.id}
                onClick={() => onBack(m)}
                style={{
                  cursor: 'pointer', borderRadius: 12,
                  border: '1px solid var(--gray2)', overflow: 'hidden',
                  transition: 'box-shadow .15s',
                }}
                onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,.08)'}
                onMouseLeave={e => e.currentTarget.style.boxShadow = 'none'}
              >
                <div style={{
                  background: 'linear-gradient(135deg, #f6faf7, #edf7f0)',
                  fontSize: '2.5rem', textAlign: 'center',
                  padding: '.9rem 0',
                }}>
                  {m.icon}
                </div>
                <div style={{ padding: '.75rem' }}>
                  <div style={{ fontSize: '.62rem', fontWeight: 700, color: 'var(--green)', textTransform: 'uppercase', letterSpacing: '.04em', marginBottom: '.25rem' }}>
                    {m.category}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '.4rem' }}>
                    <div style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--gray5)', lineHeight: 1.3 }}>{m.name}</div>
                    <div style={{ fontSize: '.65rem', color: 'var(--gray3)', fontFamily: 'monospace', flexShrink: 0 }}>{m.code}</div>
                  </div>
                  {m.price > 0 && (
                    <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--green-dark)', marginTop: '.35rem' }}>
                      Rp {m.price.toLocaleString('id-ID')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Group by base name (one card per REGULAR/LARGE family) ───────────────────
function groupMenus(menus) {
  const map = new Map();
  for (const m of menus) {
    const key = `${m.category}::${baseName(m.name)}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(m);
  }
  return [...map.values()].map(variants => {
    const rep = variants.find(v => /REGULAR/i.test(v.name)) || variants[0];
    return { ...rep, _base: baseName(rep.name), _variants: variants, _minPrice: Math.min(...variants.map(v => v.price || 0)) };
  });
}

// ── Catalog list ──────────────────────────────────────────────────────────────
export default function CatalogPage({ menus }) {
  const [search, setSearch]     = useState('');
  const [category, setCategory] = useState('');
  const [selected, setSelected] = useState(null);

  const grouped    = groupMenus(menus);
  const categories = ['', ...new Set(grouped.map(m => m.category))];

  const filtered = grouped.filter(m =>
    (!category || m.category === category) &&
    (m._base.toLowerCase().includes(search.toLowerCase()) ||
     m.category.toLowerCase().includes(search.toLowerCase()))
  );

  function handleBack(target) {
    if (target && typeof target === 'object' && target.id) {
      setSelected(target);
    } else {
      setSelected(null);
    }
  }

  if (selected) {
    return <MenuDetail menu={selected} menus={menus} onBack={handleBack} />;
  }

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
            <div key={m._base + m.category} className="menu-card" style={{ cursor: 'pointer' }} onClick={() => setSelected(m)}>
              <div className="menu-card-img">{m.icon}</div>
              <div className="menu-card-body">
                <div className="menu-card-cat">{m.category}</div>
                <div className="menu-card-name">{m._base}</div>
                <div className="menu-card-id">{m.code || m.id}</div>
                {m.keterangan && (
                  <div style={{ fontSize: '.72rem', color: 'var(--gray3)', marginTop: '.3rem', lineHeight: 1.4,
                    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {m.keterangan}
                  </div>
                )}
                {m._variants.length > 1 && (
                  <div style={{ fontSize: '.68rem', color: 'var(--gray3)', marginTop: '.25rem' }}>
                    {m._variants.length} pilihan ukuran
                  </div>
                )}
                {m._minPrice > 0 && (
                  <div style={{ fontSize: '.75rem', color: 'var(--green-dark)', fontWeight: 700, marginTop: '.3rem' }}>
                    {m._variants.length > 1 ? 'Mulai ' : ''}Rp {m._minPrice.toLocaleString('id-ID')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
