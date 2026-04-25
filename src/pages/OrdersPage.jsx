import { useState } from 'react';
import { Modal, SearchBar, EmptyState, Pill, useConfirm } from '../components/UI';

export default function OrdersPage({ orders, setOrders, users, menus }) {
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ userId: '', menuId: '', date: new Date().toISOString().split('T')[0] });
  const [formError, setFormError] = useState('');
  const { confirm, ConfirmDialog } = useConfirm();

  const regUsers = users.filter(u => u.role === 'user');

  const filtered = orders.filter(o =>
    o.userName.toLowerCase().includes(search.toLowerCase()) ||
    o.menuName.toLowerCase().includes(search.toLowerCase()) ||
    o.id.toLowerCase().includes(search.toLowerCase())
  );

  function openAdd() {
    setForm({ userId: regUsers[0]?.id || '', menuId: menus[0]?.id || '', date: new Date().toISOString().split('T')[0] });
    setFormError('');
    setModal(true);
  }

  function handleSave() {
    const { userId, menuId, date } = form;
    if (!userId || !menuId || !date) { setFormError('Lengkapi semua field.'); return; }
    const u = users.find(x => x.id === userId);
    const m = menus.find(x => x.id === menuId);
    setOrders(prev => [...prev, {
      id: 'ORD' + String(Date.now()).slice(-6),
      userId, userName: u.name,
      menuId, menuName: m.name,
      date
    }]);
    setModal(false);
  }

  async function handleDelete(order) {
    const ok = await confirm(`Hapus data pemesanan "${order.id}"?`);
    if (ok) setOrders(prev => prev.filter(o => o.id !== order.id));
  }

  return (
    <>
      {ConfirmDialog}

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Riwayat Pemesanan ({orders.length} data)</div>
          <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <SearchBar value={search} onChange={setSearch} placeholder="Cari pemesanan..." />
            <button className="btn btn-primary" onClick={openAdd}>+ Tambah</button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>ID Transaksi</th>
                <th>Pengguna</th>
                <th>Menu</th>
                <th>Tanggal</th>
                <th>Label</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={7}><EmptyState icon="📋" message="Tidak ada data pemesanan." /></td></tr>
              ) : filtered.map((o, i) => (
                <tr key={o.id}>
                  <td style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                  <td><span className="mono">{o.id}</span></td>
                  <td>{o.userName}</td>
                  <td>{o.menuName}</td>
                  <td style={{ color: 'var(--gray4)' }}>{o.date}</td>
                  <td><Pill variant="green">1 (positif)</Pill></td>
                  <td>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(o)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <Modal title="Tambah Data Pemesanan" onClose={() => setModal(false)}>
          <div className="form-group">
            <label>Pengguna</label>
            <select className="form-select" value={form.userId} onChange={e => setForm(f => ({ ...f, userId: e.target.value }))}>
              {regUsers.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Menu</label>
            <select className="form-select" value={form.menuId} onChange={e => setForm(f => ({ ...f, menuId: e.target.value }))}>
              {menus.map(m => <option key={m.id} value={m.id}>{m.icon} {m.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Tanggal</label>
            <input className="form-input" type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} />
          </div>
          {formError && <p style={{ color: 'var(--danger)', fontSize: '.78rem', marginBottom: '.5rem' }}>⚠️ {formError}</p>}
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={() => setModal(false)}>Batal</button>
            <button className="btn btn-primary" onClick={handleSave}>Simpan</button>
          </div>
        </Modal>
      )}
    </>
  );
}
