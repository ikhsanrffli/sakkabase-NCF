import { useState } from 'react';
import { Modal, SearchBar, EmptyState, Pill, useConfirm } from '../components/UI';
import { MENU_CATEGORIES, CATEGORY_ICONS } from '../data/initialData';
import { addMenuToDB, updateMenuInDB, deleteMenuFromDB } from '../utils/api';
import { menuPrice, formatRupiah } from '../utils/menuInfo';

export default function MenusPage({ menus, setMenus }) {
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ id: '', name: '', category: MENU_CATEGORIES[0], price: '' });
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const { confirm, ConfirmDialog } = useConfirm();

  const filtered = menus.filter(m =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.id.toLowerCase().includes(search.toLowerCase()) ||
    m.category.toLowerCase().includes(search.toLowerCase())
  );

  function openAdd() {
    setForm({ id: '', name: '', category: MENU_CATEGORIES[0], price: '' });
    setFormError('');
    setModal('add');
  }

  function openEdit(menu) {
    setForm({ id: menu.id, name: menu.name, category: menu.category, price: menuPrice(menu) });
    setFormError('');
    setModal({ edit: menu });
  }

  async function handleSave() {
    const { id, name, category, price } = form;
    if (!name.trim()) { setFormError('Nama menu wajib diisi.'); return; }
    const harga = Math.max(0, parseInt(price, 10) || 0);
    setFormError('');
    setSaving(true);

    if (modal === 'add') {
      if (!id.trim()) { setFormError('ID item wajib diisi.'); setSaving(false); return; }
      const code = id.trim().toUpperCase();
      if (menus.find(m => m.id === code)) { setFormError('ID item sudah digunakan.'); setSaving(false); return; }
      const res = await addMenuToDB({ id: code, name: name.trim(), category, price: harga });
      setSaving(false);
      if (!res || !res.ok) { setFormError(res?.message || 'Gagal menyimpan ke database.'); return; }
      setMenus(prev => [...prev, {
        id: code, name: name.trim(), category, price: harga,
        icon: CATEGORY_ICONS[category] || '🍽️',
      }]);
    } else {
      const res = await updateMenuInDB({ id: modal.edit.id, name: name.trim(), category, price: harga });
      setSaving(false);
      if (!res || !res.ok) { setFormError(res?.message || 'Gagal menyimpan ke database.'); return; }
      setMenus(prev => prev.map(m =>
        m.id === modal.edit.id
          ? { ...m, name: name.trim(), category, price: harga, icon: CATEGORY_ICONS[category] || '🍽️' }
          : m
      ));
    }
    setModal(null);
  }

  async function handleDelete(menu) {
    const ok = await confirm(`Hapus menu "${menu.name}"?`);
    if (!ok) return;
    const res = await deleteMenuFromDB(menu.id);
    if (!res || !res.ok) { alert(res?.message || 'Gagal menghapus dari database.'); return; }
    setMenus(prev => prev.filter(m => m.id !== menu.id));
  }

  return (
    <>
      {ConfirmDialog}

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Katalog Menu ({menus.length} item)</div>
          <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <SearchBar value={search} onChange={setSearch} placeholder="Cari menu..." />
            <button className="btn btn-primary" onClick={openAdd}>+ Tambah</button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr><th>No</th><th>ID Item</th><th>Nama Menu</th><th>Kategori</th><th>Harga</th><th>Aksi</th></tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={6}><EmptyState icon="🍽️" message="Tidak ada menu ditemukan." /></td></tr>
              ) : filtered.map((m, i) => (
                <tr key={m.id}>
                  <td data-label="No" style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                  <td data-label="ID Item"><span className="mono">{m.id}</span></td>
                  <td data-label="Nama Menu"><span style={{ marginRight: '.4rem' }}>{m.icon}</span><strong>{m.name}</strong></td>
                  <td data-label="Kategori"><Pill variant="gold">{m.category}</Pill></td>
                  <td data-label="Harga" style={{ fontWeight: 600, color: 'var(--green)' }}>{formatRupiah(menuPrice(m))}</td>
                  <td data-label="Aksi">
                    <button className="btn btn-outline btn-sm" onClick={() => openEdit(m)}>Edit</button>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: '.4rem' }} onClick={() => handleDelete(m)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <Modal title={modal === 'add' ? 'Tambah Menu Baru' : 'Edit Menu'} onClose={() => setModal(null)}>
          <div className="form-group">
            <label>ID Item</label>
            <input
              className="form-input"
              value={form.id}
              onChange={e => setForm(f => ({ ...f, id: e.target.value }))}
              placeholder="Contoh: A01H"
              disabled={modal !== 'add'}
            />
          </div>
          <div className="form-group">
            <label>Nama Menu</label>
            <input className="form-input" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Nama menu" />
          </div>
          <div className="form-group">
            <label>Kategori</label>
            <select className="form-select" value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}>
              {MENU_CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Harga (Rp)</label>
            <input
              className="form-input"
              type="number"
              min="0"
              step="1000"
              value={form.price}
              onChange={e => setForm(f => ({ ...f, price: e.target.value }))}
              placeholder="Contoh: 25000"
            />
          </div>
          {formError && <p style={{ color: 'var(--danger)', fontSize: '.78rem', marginBottom: '.5rem' }}>⚠️ {formError}</p>}
          <div className="modal-actions">
            <button className="btn btn-ghost" onClick={() => setModal(null)} disabled={saving}>Batal</button>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? 'Menyimpan…' : 'Simpan'}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
