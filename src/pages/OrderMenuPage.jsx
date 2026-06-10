import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/apiClient';

// ── helpers ───────────────────────────────────────────────────────────────────
function stripVariant(name) {
  return name
    .replace(/\s*\/\s*(HOT LARGE|HOT REGULAR|COLD LARGE|COLD REGULAR|HOT|COLD|LARGE|REGULAR|SMALL|50K|25K|\d+\s*ML|\d+\s*GR)\s*$/i, '')
    .trim();
}

function variantLabel(name) {
  const m = name.match(/\/\s*(.+)$/);
  return m ? m[1].trim() : null;
}

function groupMenus(menus) {
  const map = new Map();
  for (const m of menus) {
    const key = `${m.category}::${stripVariant(m.name)}`;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(m);
  }
  return [...map.values()].map(variants => {
    const rep = variants.find(v => /REGULAR/i.test(v.name)) || variants[0];
    const minPrice = Math.min(...variants.map(v => v.price || 0));
    return { ...rep, _base: stripVariant(rep.name), _variants: variants, _minPrice: minPrice };
  });
}

// ── Variant picker modal ──────────────────────────────────────────────────────
function VariantPicker({ item, onSelect, onClose }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box" style={{ maxWidth: 360 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <div style={{ fontSize: '.68rem', color: 'var(--green)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '.2rem' }}>
              {item.category}
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--gray5)' }}>{item._base}</div>
          </div>
          <span style={{ fontSize: '2rem' }}>{item.icon}</span>
        </div>

        <div style={{ fontSize: '.78rem', fontWeight: 600, color: 'var(--gray4)', marginBottom: '.6rem' }}>
          Pilih ukuran / varian:
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '.5rem', marginBottom: '1rem' }}>
          {item._variants.map(v => {
            const label = variantLabel(v.name) || v.name;
            return (
              <button
                key={v.id}
                onClick={() => onSelect(v)}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '.75rem 1rem', border: '1.5px solid var(--gray2)',
                  borderRadius: 10, background: 'white', cursor: 'pointer',
                  fontFamily: 'var(--font)', transition: 'all .12s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--green)'; e.currentTarget.style.background = 'var(--green-light)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--gray2)'; e.currentTarget.style.background = 'white'; }}
              >
                <span style={{ fontSize: '.85rem', fontWeight: 600, color: 'var(--gray5)' }}>{label}</span>
                {v.price > 0 && (
                  <span style={{ fontSize: '.82rem', fontWeight: 700, color: 'var(--green-dark)' }}>
                    Rp {v.price.toLocaleString('id-ID')}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <button className="btn btn-ghost" style={{ width: '100%', justifyContent: 'center' }} onClick={onClose}>
          Batal
        </button>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function OrderMenuPage({ menus, orders, setOrders }) {
  const { currentUser } = useAuth();
  const [category, setCategory]           = useState('Semua');
  const [search, setSearch]               = useState('');
  const [cart, setCart]                   = useState([]);
  const [showCart, setShowCart]           = useState(false);
  const [showSuccess, setShowSuccess]     = useState(false);
  const [successItems, setSuccessItems]   = useState([]);
  const [submitting, setSubmitting]       = useState(false);
  const [variantPicker, setVariantPicker] = useState(null);

  const grouped     = groupMenus(menus);
  const dynamicCats = ['Semua', ...new Set(grouped.map(m => m.category))];

  const filtered = grouped.filter(m =>
    (category === 'Semua' || m.category === category) &&
    (m._base.toLowerCase().includes(search.toLowerCase()) ||
     m.name.toLowerCase().includes(search.toLowerCase()))
  );

  function addToCart(menu) {
    setCart(prev => {
      const exists = prev.find(c => c.id === menu.id);
      if (exists) return prev.map(c => c.id === menu.id ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { ...menu, qty: 1 }];
    });
  }

  function handlePesan(item) {
    if (item._variants.length > 1) {
      setVariantPicker(item);
    } else {
      addToCart(item);
    }
  }

  function handleVariantSelect(variant) {
    addToCart(variant);
    setVariantPicker(null);
  }

  function removeFromCart(menuId) {
    setCart(prev => {
      const exists = prev.find(c => c.id === menuId);
      if (exists && exists.qty > 1) return prev.map(c => c.id === menuId ? { ...c, qty: c.qty - 1 } : c);
      return prev.filter(c => c.id !== menuId);
    });
  }

  function deleteFromCart(menuId) {
    setCart(prev => prev.filter(c => c.id !== menuId));
  }

  function getTotalItems() { return cart.reduce((a, c) => a + c.qty, 0); }
  function getTotalPrice() { return cart.reduce((a, c) => a + (c.price || 0) * c.qty, 0); }

  async function handleCheckout() {
    if (cart.length === 0 || submitting) return;
    setSubmitting(true);
    try {
      await api.createOrder(cart);
      const updatedOrders = await api.getMyOrders();
      setOrders(updatedOrders);
      setSuccessItems([...cart]);
      setCart([]);
      setShowCart(false);
      setShowSuccess(true);
    } catch (err) {
      alert('Gagal memesan: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (showSuccess) {
    return (
      <div style={{ maxWidth: 480, margin: '0 auto', paddingTop: '2rem' }}>
        <div style={{ background: 'white', borderRadius: 16, border: '1px solid var(--gray2)', padding: '2rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>✅</div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--gray5)', marginBottom: '.4rem' }}>Pesanan Berhasil!</h2>
          <p style={{ fontSize: '.85rem', color: 'var(--gray4)', marginBottom: '1.5rem' }}>
            Terima kasih, <strong>{currentUser.name}</strong>! Pesanan Anda sedang diproses.
          </p>
          <div style={{ background: 'var(--gray1)', borderRadius: 10, padding: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
            {successItems.map(item => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '.45rem 0', borderBottom: '1px solid var(--gray2)', fontSize: '.83rem' }}>
                <span>{item.icon} <strong>{item.name}</strong> ×{item.qty}</span>
                {item.price > 0 && <span style={{ color: 'var(--green-dark)', fontWeight: 700 }}>Rp {(item.price * item.qty).toLocaleString('id-ID')}</span>}
              </div>
            ))}
            {successItems.reduce((a, i) => a + (i.price || 0) * i.qty, 0) > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '.5rem', fontSize: '.85rem', fontWeight: 700 }}>
                <span>Total</span>
                <span style={{ color: 'var(--green)' }}>Rp {successItems.reduce((a, i) => a + (i.price || 0) * i.qty, 0).toLocaleString('id-ID')}</span>
              </div>
            )}
          </div>
          <button className="btn btn-primary" style={{ width: '100%', padding: '.75rem', fontSize: '.9rem', justifyContent: 'center' }} onClick={() => setShowSuccess(false)}>
            Pesan Lagi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      {variantPicker && (
        <VariantPicker
          item={variantPicker}
          onSelect={handleVariantSelect}
          onClose={() => setVariantPicker(null)}
        />
      )}

      <div style={{ display: 'flex', gap: '.6rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <div className="search-bar" style={{ flex: 1, maxWidth: 300 }}>
          <span className="search-icon">🔍</span>
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Cari menu..." />
        </div>
        <span style={{ fontSize: '.78rem', color: 'var(--gray4)', marginLeft: 'auto' }}>
          {filtered.length} menu tersedia
        </span>
      </div>

      <div style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap', marginBottom: '1.2rem' }}>
        {dynamicCats.map(cat => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            style={{
              padding: '.35rem .85rem',
              border: category === cat ? '1.5px solid var(--green)' : '1.5px solid var(--gray2)',
              borderRadius: 99,
              background: category === cat ? 'var(--green)' : 'white',
              color: category === cat ? 'white' : 'var(--gray4)',
              fontSize: '.76rem', fontWeight: 600,
              cursor: 'pointer', fontFamily: 'var(--font)', transition: 'all .15s',
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state"><div className="empty-icon">🔍</div><p>Tidak ada menu ditemukan.</p></div>
      ) : (
        <div className="menu-grid" style={{ marginBottom: '5rem' }}>
          {filtered.map(m => {
            const cartQty = m._variants.reduce((sum, v) => {
              const c = cart.find(ci => ci.id === v.id);
              return sum + (c ? c.qty : 0);
            }, 0);
            const hasVariants = m._variants.length > 1;

            return (
              <div key={m._base + m.category} className="menu-card" style={{ position: 'relative' }}>
                {cartQty > 0 && (
                  <div style={{
                    position: 'absolute', top: 8, right: 8, zIndex: 1,
                    background: 'var(--green)', color: 'white',
                    width: 22, height: 22, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '.7rem', fontWeight: 800,
                  }}>{cartQty}</div>
                )}
                <div className="menu-card-img">{m.icon}</div>
                <div className="menu-card-body">
                  <div className="menu-card-cat">{m.category}</div>
                  <div className="menu-card-name">{m._base}</div>
                  <div className="menu-card-id">{m.code || m.id}</div>
                  {hasVariants && (
                    <div style={{ fontSize: '.68rem', color: 'var(--gray3)', marginTop: '.2rem' }}>
                      {m._variants.length} pilihan ukuran
                    </div>
                  )}
                  {m._minPrice > 0 && (
                    <div style={{ fontSize: '.78rem', color: 'var(--green-dark)', fontWeight: 700, marginBottom: '.6rem' }}>
                      {hasVariants ? 'Mulai ' : ''}Rp {m._minPrice.toLocaleString('id-ID')}
                    </div>
                  )}
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', justifyContent: 'center', fontSize: '.76rem', padding: '.4rem', marginTop: 'auto' }}
                    onClick={() => handlePesan(m)}
                  >
                    + Pesan
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {cart.length > 0 && !showCart && (
        <div style={{ position: 'fixed', bottom: '1.5rem', right: '1.5rem', zIndex: 200 }}>
          <button
            onClick={() => setShowCart(true)}
            style={{
              background: 'var(--green)', color: 'white', border: 'none', borderRadius: 99,
              padding: '.75rem 1.4rem', fontSize: '.88rem', fontWeight: 700,
              cursor: 'pointer', fontFamily: 'var(--font)',
              display: 'flex', alignItems: 'center', gap: '.5rem',
              boxShadow: '0 6px 20px rgba(26,122,62,.4)',
            }}
          >
            🛒 Keranjang
            <span style={{ background: 'var(--gold)', color: 'var(--green-dark)', borderRadius: 99, padding: '1px 8px', fontSize: '.75rem', fontWeight: 800 }}>
              {getTotalItems()}
            </span>
          </button>
        </div>
      )}

      {showCart && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setShowCart(false)}>
          <div className="modal-box" style={{ maxWidth: 440, maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.2rem' }}>
              <div className="modal-title" style={{ margin: 0 }}>🛒 Keranjang Pesanan</div>
              <button onClick={() => setShowCart(false)} style={{ background: 'none', border: 'none', fontSize: '1.1rem', cursor: 'pointer', color: 'var(--gray4)' }}>✕</button>
            </div>

            {cart.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray3)', fontSize: '.85rem' }}>Keranjang kosong</div>
            ) : (
              <>
                <div style={{ maxHeight: 320, overflowY: 'auto', marginBottom: '1rem' }}>
                  {cart.map(item => (
                    <div key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '.75rem', padding: '.7rem 0', borderBottom: '1px solid var(--gray2)' }}>
                      <span style={{ fontSize: '1.5rem' }}>{item.icon}</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '.83rem', fontWeight: 700, color: 'var(--gray5)' }}>{item.name}</div>
                        <div style={{ fontSize: '.7rem', color: 'var(--gray4)' }}>{item.category}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '.35rem' }}>
                        <button onClick={() => removeFromCart(item.id)} style={{ width: 26, height: 26, border: '1.5px solid var(--gray2)', borderRadius: 6, background: 'white', cursor: 'pointer', fontSize: '.9rem', fontWeight: 700, color: 'var(--gray5)', display: 'flex', alignItems: 'center', justifyContent: 'center', lineHeight: 1 }}>−</button>
                        <span style={{ fontSize: '.85rem', fontWeight: 700, color: 'var(--green)', minWidth: 20, textAlign: 'center' }}>{item.qty}</span>
                        <button onClick={() => addToCart(item)} style={{ width: 26, height: 26, border: 'none', borderRadius: 6, background: 'var(--green)', cursor: 'pointer', fontSize: '.9rem', fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', lineHeight: 1 }}>+</button>
                        <button onClick={() => deleteFromCart(item.id)} style={{ width: 26, height: 26, border: 'none', borderRadius: 6, background: '#fdf0f0', cursor: 'pointer', fontSize: '.75rem', color: '#e74c3c', display: 'flex', alignItems: 'center', justifyContent: 'center', marginLeft: 2 }}>🗑</button>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ background: 'var(--green-light)', borderRadius: 10, padding: '.75rem 1rem', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '.3rem' }}>
                    <span style={{ fontSize: '.83rem', color: 'var(--green-dark)' }}>Total item: <strong>{getTotalItems()} menu</strong></span>
                    <span style={{ fontSize: '.75rem', color: 'var(--green)', fontWeight: 700 }}>{cart.length} jenis</span>
                  </div>
                  {getTotalPrice() > 0 && (
                    <div style={{ fontSize: '.88rem', color: 'var(--green-dark)', fontWeight: 700 }}>
                      Total: Rp {getTotalPrice().toLocaleString('id-ID')}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '.5rem' }}>
                  <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setShowCart(false)}>Lanjut Pilih</button>
                  <button className="btn btn-primary" style={{ flex: 2, justifyContent: 'center', padding: '.65rem' }} onClick={handleCheckout} disabled={submitting}>
                    {submitting ? '⏳ Memproses...' : '✓ Konfirmasi Pesanan'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
