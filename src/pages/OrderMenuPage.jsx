import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { persistOrderToDB } from '../utils/api';

// Kategori yang relevan untuk pemesanan (exclude Barber, Tambahan, Lainnya)
const FOOD_DRINK_CATS = [
  'Kopi & Espresso','Non-Kopi','Juice','Minuman',
  'Croissant & Pastry','Pudding','Snack Ringan',
  'Gorengan & Snack','Toast','Nasi Goreng','Nasi Lauk',
  'Mie & Bihun','Pasta','Indomie','Chicken Steak',
  'Salad','Ricebowl','Sayur','Ice Cream','Produk Kopi',
];

export default function OrderMenuPage({ menus, orders, setOrders }) {
  const { currentUser } = useAuth();
  const [category, setCategory] = useState('Semua');
  const [search, setSearch] = useState('');
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [successItems, setSuccessItems] = useState([]);

  // Hanya tampilkan menu makanan & minuman (exclude Barber, Tambahan, dll)
  const orderableMenus = menus.filter(m => FOOD_DRINK_CATS.includes(m.category));
  const dynamicCats = ['Semua', ...new Set(orderableMenus.map(m => m.category))];

  const filtered = orderableMenus.filter(m =>
    (category === 'Semua' || m.category === category) &&
    m.name.toLowerCase().includes(search.toLowerCase())
  );

  function addToCart(menu) {
    setCart(prev => {
      const exists = prev.find(c => c.id === menu.id);
      if (exists) return prev.map(c => c.id === menu.id ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { ...menu, qty: 1 }];
    });
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

  function getTotalItems() {
    return cart.reduce((acc, c) => acc + c.qty, 0);
  }

  function handleCheckout() {
    if (cart.length === 0) return;
    const today = new Date().toISOString().split('T')[0];
    const newOrders = cart.map(item => ({
      id: 'ORD' + String(Date.now() + Math.random()).replace('.', '').slice(-6),
      userId: currentUser.id,
      userName: currentUser.name,
      menuId: item.id,
      menuName: item.name,
      qty: item.qty,
      date: today,
    }));
    setOrders(prev => [...prev, ...newOrders]);
    // simpan pesanan ke MySQL (best-effort): kirim kode menu sesuai urutan keranjang
    persistOrderToDB(currentUser.username, cart.map(c => c.id), today);
    setSuccessItems([...cart]);
    setCart([]);
    setShowCart(false);
    setShowSuccess(true);
  }

  if (showSuccess) {
    return (
      <div style={{ maxWidth: 480, margin: '0 auto', paddingTop: '2rem' }}>
        <div style={{
          background: 'white', borderRadius: 16, border: '1px solid var(--gray2)',
          padding: '2rem', textAlign: 'center'
        }}>
          <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>✅</div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--gray5)', marginBottom: '.4rem' }}>
            Pesanan Berhasil!
          </h2>
          <p style={{ fontSize: '.85rem', color: 'var(--gray4)', marginBottom: '1.5rem' }}>
            Terima kasih, <strong>{currentUser.name}</strong>! Pesanan Anda sedang diproses.
          </p>
          <div style={{ background: 'var(--gray1)', borderRadius: 10, padding: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
            {successItems.map(item => (
              <div key={item.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '.45rem 0', borderBottom: '1px solid var(--gray2)', fontSize: '.83rem'
              }}>
                <span>{item.icon} <strong>{item.name}</strong></span>
                <span style={{ color: 'var(--green)', fontWeight: 700 }}>x{item.qty}</span>
              </div>
            ))}
          </div>
          <button
            className="btn btn-primary"
            style={{ width: '100%', padding: '.75rem', fontSize: '.9rem', justifyContent: 'center' }}
            onClick={() => setShowSuccess(false)}
          >
            Pesan Lagi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>

      {/* ── Search & filter ── */}
      <div style={{ display: 'flex', gap: '.6rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <div className="search-bar" style={{ flex: 1, maxWidth: 300 }}>
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Cari menu..."
          />
        </div>
        <span style={{ fontSize: '.78rem', color: 'var(--gray4)', marginLeft: 'auto' }}>
          {filtered.length} menu tersedia
        </span>
      </div>

      {/* ── Category tabs ── */}
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
              cursor: 'pointer', fontFamily: 'var(--font)',
              transition: 'all .15s'
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* ── Menu grid ── */}
      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>Tidak ada menu ditemukan.</p>
        </div>
      ) : (
        <div className="menu-grid" style={{ marginBottom: '5rem' }}>
          {filtered.map(m => {
            const inCart = cart.find(c => c.id === m.id);
            return (
              <div key={m.id} className="menu-card" style={{ position: 'relative' }}>
                {inCart && (
                  <div style={{
                    position: 'absolute', top: 8, right: 8, zIndex: 1,
                    background: 'var(--green)', color: 'white',
                    width: 22, height: 22, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '.7rem', fontWeight: 800
                  }}>{inCart.qty}</div>
                )}
                <div className="menu-card-img">{m.icon}</div>
                <div className="menu-card-body">
                  <div className="menu-card-cat">{m.category}</div>
                  <div className="menu-card-name">{m.name}</div>
                  <div className="menu-card-id" style={{ marginBottom: '.6rem' }}>{m.id}</div>

                  {inCart ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '.4rem' }}>
                      <button
                        onClick={() => removeFromCart(m.id)}
                        style={{
                          width: 28, height: 28, border: '1.5px solid var(--gray2)',
                          borderRadius: 6, background: 'white', fontSize: '1rem',
                          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 700, color: 'var(--gray5)', lineHeight: 1
                        }}
                      >−</button>
                      <span style={{ flex: 1, textAlign: 'center', fontSize: '.85rem', fontWeight: 700, color: 'var(--green)' }}>
                        {inCart.qty}
                      </span>
                      <button
                        onClick={() => addToCart(m)}
                        style={{
                          width: 28, height: 28, border: 'none',
                          borderRadius: 6, background: 'var(--green)', fontSize: '1rem',
                          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 700, color: 'white', lineHeight: 1
                        }}
                      >+</button>
                    </div>
                  ) : (
                    <button
                      className="btn btn-primary"
                      style={{ width: '100%', justifyContent: 'center', fontSize: '.76rem', padding: '.4rem' }}
                      onClick={() => addToCart(m)}
                    >
                      + Pesan
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Floating cart button ── */}
      {cart.length > 0 && !showCart && (
        <div style={{ position: 'fixed', bottom: '1.5rem', right: '1.5rem', zIndex: 200 }}>
          <button
            onClick={() => setShowCart(true)}
            style={{
              background: 'var(--green)', color: 'white',
              border: 'none', borderRadius: 99,
              padding: '.75rem 1.4rem',
              fontSize: '.88rem', fontWeight: 700,
              cursor: 'pointer', fontFamily: 'var(--font)',
              display: 'flex', alignItems: 'center', gap: '.5rem',
              boxShadow: '0 6px 20px rgba(26,122,62,.4)'
            }}
          >
            🛒 Keranjang
            <span style={{
              background: 'var(--gold)', color: 'var(--green-dark)',
              borderRadius: 99, padding: '1px 8px',
              fontSize: '.75rem', fontWeight: 800
            }}>{getTotalItems()}</span>
          </button>
        </div>
      )}

      {/* ── Cart drawer / modal ── */}
      {showCart && (
        <div
          className="modal-overlay"
          onClick={e => e.target === e.currentTarget && setShowCart(false)}
        >
          <div className="modal-box" style={{ maxWidth: 440 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.2rem' }}>
              <div className="modal-title" style={{ margin: 0 }}>🛒 Keranjang Pesanan</div>
              <button
                onClick={() => setShowCart(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.1rem', cursor: 'pointer', color: 'var(--gray4)' }}
              >✕</button>
            </div>

            {cart.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--gray3)', fontSize: '.85rem' }}>
                Keranjang kosong
              </div>
            ) : (
              <>
                <div style={{ maxHeight: 320, overflowY: 'auto', marginBottom: '1rem' }}>
                  {cart.map(item => (
                    <div key={item.id} style={{
                      display: 'flex', alignItems: 'center', gap: '.75rem',
                      padding: '.7rem 0', borderBottom: '1px solid var(--gray2)'
                    }}>
                      <span style={{ fontSize: '1.5rem' }}>{item.icon}</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '.83rem', fontWeight: 700, color: 'var(--gray5)' }}>{item.name}</div>
                        <div style={{ fontSize: '.7rem', color: 'var(--gray4)' }}>{item.category}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '.35rem' }}>
                        <button
                          onClick={() => removeFromCart(item.id)}
                          style={{
                            width: 26, height: 26, border: '1.5px solid var(--gray2)',
                            borderRadius: 6, background: 'white', cursor: 'pointer',
                            fontSize: '.9rem', fontWeight: 700, color: 'var(--gray5)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', lineHeight: 1
                          }}
                        >−</button>
                        <span style={{ fontSize: '.85rem', fontWeight: 700, color: 'var(--green)', minWidth: 20, textAlign: 'center' }}>
                          {item.qty}
                        </span>
                        <button
                          onClick={() => addToCart(item)}
                          style={{
                            width: 26, height: 26, border: 'none',
                            borderRadius: 6, background: 'var(--green)', cursor: 'pointer',
                            fontSize: '.9rem', fontWeight: 700, color: 'white',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', lineHeight: 1
                          }}
                        >+</button>
                        <button
                          onClick={() => deleteFromCart(item.id)}
                          style={{
                            width: 26, height: 26, border: 'none',
                            borderRadius: 6, background: '#fdf0f0', cursor: 'pointer',
                            fontSize: '.75rem', color: '#e74c3c',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', marginLeft: 2
                          }}
                        >🗑</button>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{
                  background: 'var(--green-light)', borderRadius: 10,
                  padding: '.75rem 1rem', marginBottom: '1rem',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                }}>
                  <span style={{ fontSize: '.83rem', color: 'var(--green-dark)' }}>
                    Total item: <strong>{getTotalItems()} menu</strong>
                  </span>
                  <span style={{ fontSize: '.75rem', color: 'var(--green)', fontWeight: 700 }}>
                    {cart.length} jenis
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '.5rem' }}>
                  <button className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setShowCart(false)}>
                    Lanjut Pilih
                  </button>
                  <button className="btn btn-primary" style={{ flex: 2, justifyContent: 'center', padding: '.65rem' }} onClick={handleCheckout}>
                    ✓ Konfirmasi Pesanan
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
