import { useState } from 'react';
import { SearchBar, EmptyState } from '../components/UI';

// Strip trailing size/variant suffix to get the "base name" for grouping
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
  const base   = baseName(menu.name);
  const variants = menus.filter(m => m.category === menu.category && baseName(m.name) === base);
  const related  = menus.filter(m => m.category === menu.category && m.id !== menu.id && baseName(m.name) !== base).slice(0, 6);

  const hasVariants = variants.length > 1;

  return (
    <div>
      {/* Back button */}
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

      {/* Detail card */}
      <div style={{ background: 'white', borderRadius: 16, border: '1px solid var(--gray2)', overflow: 'hidden', marginBottom: '1.5rem' }}>

        {/* Hero icon */}
        <div style={{
          background: 'linear-gradient(135deg, #f6faf7 0%, #edf7f0 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '2rem 0', fontSize: '5rem',
        }}>
          {menu.icon}
        </div>

        <div style={{ padding: '1.5rem' }}>
          {/* Category + code */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.5rem' }}>
            <span style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--green)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
              {menu.category}
            </span>
            <span style={{ color: 'var(--gray3)', fontSize: '.72rem' }}>•</span>
            <span style={{ fontSize: '.72rem', color: 'var(--gray3)', fontFamily: 'monospace' }}>{menu.code}</span>
          </div>

          {/* Name */}
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--gray5)', margin: '0 0 1.2rem', lineHeight: 1.25 }}>
            {menu.name}
          </h2>

          {/* Price + (no serving time in DB) */}
          <div style={{ display: 'grid', gridTemplateColumns: menu.price > 0 ? '1fr 1fr' : '1fr', gap: '.75rem', marginBottom: '1.2rem' }}>
            {menu.price > 0 && (
              <div style={{ background: 'var(--gray1)', borderRadius: 10, padding: '.75rem 1rem' }}>
                <div style={{ fontSize: '.7rem', color: 'var(--gray3)', marginBottom: '.2rem' }}>Harga satuan</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--green-dark)' }}>
                  Rp {menu.price.toLocaleString('id-ID')}
                </div>
              </div>
            )}
            <div style={{ background: 'var(--gray1)', borderRadius: 10, padding: '.75rem 1rem' }}>
              <div style={{ fontSize: '.7rem', color: 'var(--gray3)', marginBottom: '.2rem' }}>Kode item</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--gray5)', fontFamily: 'monospace' }}>{menu.id}</div>
            </div>
          </div>

          {/* Size / variant options */}
          {hasVariants && (
            <div style={{ marginBottom: '1.2rem' }}>
              <div style={{ fontSize: '.78rem', fontWeight: 600, color: 'var(--gray4)', marginBottom: '.55rem' }}>Pilihan varian</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '.5rem' }}>
                {variants.map(v => {
                  const label   = variantLabel(v.name) || v.name;
                  const isActive = v.id === menu.id;
                  return (
                    <div
                      key={v.id}
                      onClick={() => onBack(v)}
                      style={{
                        padding: '.45rem 1rem',
                        border: isActive ? '2px solid var(--green)' : '1.5px solid var(--gray2)',
                        borderRadius: 10,
                        background: isActive ? 'var(--green-light)' : 'white',
                        color: isActive ? 'var(--green-dark)' : 'var(--gray4)',
                        fontSize: '.78rem', fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      <div>{label}</div>
                      {v.price > 0 && (
                        <div style={{ fontSize: '.7rem', color: isActive ? 'var(--green)' : 'var(--gray3)', marginTop: 2 }}>
                          Rp {v.price.toLocaleString('id-ID')}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related menus */}
      {related.length > 0 && (
        <>
          <div style={{ fontSize: '.72rem', fontWeight: 700, color: 'var(--gray3)', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: '.75rem' }}>
            Menu Lainnya
          </div>
          <div className="menu-grid">
            {related.map(m => (
              <div key={m.id} className="menu-card" style={{ cursor: 'pointer' }} onClick={() => onBack(m)}>
                <div className="menu-card-img">{m.icon}</div>
                <div className="menu-card-body">
                  <div className="menu-card-cat">{m.category}</div>
                  <div className="menu-card-name">{m.name}</div>
                  <div className="menu-card-id">{m.code || m.id}</div>
                  {m.price > 0 && (
                    <div style={{ fontSize: '.75rem', color: 'var(--green-dark)', fontWeight: 700, marginTop: '.3rem' }}>
                      Rp {m.price.toLocaleString('id-ID')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ── Catalog list ──────────────────────────────────────────────────────────────
export default function CatalogPage({ menus }) {
  const [search, setSearch]       = useState('');
  const [category, setCategory]   = useState('');
  const [selected, setSelected]   = useState(null);

  const categories = ['', ...new Set(menus.map(m => m.category))];

  const filtered = menus.filter(m =>
    (!category || m.category === category) &&
    (m.name.toLowerCase().includes(search.toLowerCase()) ||
     m.category.toLowerCase().includes(search.toLowerCase()))
  );

  // onBack(menu?) — if called with a menu object, open that menu's detail instead
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
            <div key={m.id} className="menu-card" style={{ cursor: 'pointer' }} onClick={() => setSelected(m)}>
              <div className="menu-card-img">{m.icon}</div>
              <div className="menu-card-body">
                <div className="menu-card-cat">{m.category}</div>
                <div className="menu-card-name">{m.name}</div>
                <div className="menu-card-id">{m.code || m.id}</div>
                {m.price > 0 && (
                  <div style={{ fontSize: '.75rem', color: 'var(--green-dark)', fontWeight: 700, marginTop: '.3rem' }}>
                    Rp {m.price.toLocaleString('id-ID')}
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
