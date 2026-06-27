import { useState } from 'react';
import { Modal, SearchBar, EmptyState, Pill, useConfirm } from '../components/UI';
import { addUserToDB, updateUserInDB, deleteUserFromDB } from '../utils/api';

const PER_PAGE = 25; // jumlah pengguna yang ditampilkan per halaman

export default function UsersPage({ users, setUsers }) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [modal, setModal] = useState(null); // null | 'add' | {edit: user}
  const [form, setForm] = useState({ name: '', username: '', password: '' });
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const { confirm, ConfirmDialog } = useConfirm();

  const regUsers = users.filter(u => u.role === 'user');
  const filtered = regUsers.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.username.toLowerCase().includes(search.toLowerCase())
  );

  // Paginasi: pecah data agar tidak merender ratusan baris sekaligus.
  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const safePage = Math.min(page, totalPages);            // jaga-jaga bila data menyusut
  const start = (safePage - 1) * PER_PAGE;
  const pageData = filtered.slice(start, start + PER_PAGE);

  function onSearch(v) { setSearch(v); setPage(1); }       // kembali ke halaman 1 saat mencari

  function openAdd() {
    setForm({ name: '', username: '', password: '' });
    setFormError('');
    setModal('add');
  }

  function openEdit(user) {
    setForm({ name: user.name, username: user.username, password: '' });
    setFormError('');
    setModal({ edit: user });
  }

  async function handleSave() {
    const { name, username, password } = form;
    if (!name.trim() || !username.trim()) { setFormError('Nama dan username wajib diisi.'); return; }
    setFormError('');
    setSaving(true);

    if (modal === 'add') {
      if (!password.trim()) { setFormError('Password wajib diisi.'); setSaving(false); return; }
      if (users.find(u => u.username === username.trim())) { setFormError('Username sudah digunakan.'); setSaving(false); return; }
      const res = await addUserToDB({ name: name.trim(), username: username.trim(), password: password.trim() });
      setSaving(false);
      if (!res || !res.ok) { setFormError(res?.message || 'Gagal menyimpan ke database.'); return; }
      // pakai id asli dari MySQL agar Edit/Hapus berikutnya tepat sasaran
      setUsers(prev => [...prev, { id: String(res.id), username: username.trim(), password: password.trim(), role: 'user', name: name.trim() }]);
    } else {
      const res = await updateUserInDB({ id: modal.edit.id, name: name.trim(), username: username.trim(), password: password.trim() });
      setSaving(false);
      if (!res || !res.ok) { setFormError(res?.message || 'Gagal menyimpan ke database.'); return; }
      setUsers(prev => prev.map(u =>
        u.id === modal.edit.id ? { ...u, name: name.trim(), username: username.trim() } : u
      ));
    }
    setModal(null);
  }

  async function handleDelete(user) {
    const ok = await confirm(`Hapus pengguna "${user.name}"? Data pemesanannya juga akan ikut terhapus.`);
    if (!ok) return;
    const res = await deleteUserFromDB(user.id);
    if (!res || !res.ok) { alert(res?.message || 'Gagal menghapus dari database.'); return; }
    setUsers(prev => prev.filter(u => u.id !== user.id));
  }

  return (
    <>
      {ConfirmDialog}

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Daftar Pengguna ({regUsers.length} user)</div>
          <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <SearchBar value={search} onChange={onSearch} placeholder="Cari pengguna..." />
            <button className="btn btn-primary" onClick={openAdd}>+ Tambah</button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>No</th><th>Nama</th><th>Username</th><th>Peran</th><th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={5}><EmptyState icon="👤" message="Tidak ada pengguna ditemukan." /></td></tr>
              ) : pageData.map((u, i) => (
                <tr key={u.id}>
                  <td style={{ color: 'var(--gray3)' }}>{start + i + 1}</td>
                  <td><strong>{u.name}</strong></td>
                  <td><span className="mono">{u.username}</span></td>
                  <td><Pill variant="green">{u.role}</Pill></td>
                  <td>
                    <button className="btn btn-outline btn-sm" onClick={() => openEdit(u)}>Edit</button>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: '.4rem' }} onClick={() => handleDelete(u)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filtered.length > 0 && (
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            flexWrap: 'wrap', gap: '.5rem', padding: '.8rem 1.3rem',
            borderTop: '1px solid var(--gray2)', fontSize: '.81rem', color: 'var(--gray4)'
          }}>
            <span>
              Menampilkan {start + 1}–{Math.min(start + PER_PAGE, filtered.length)} dari {filtered.length} pengguna
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setPage(safePage - 1)}
                disabled={safePage <= 1}
              >‹ Sebelumnya</button>
              <span>Halaman {safePage} dari {totalPages}</span>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setPage(safePage + 1)}
                disabled={safePage >= totalPages}
              >Berikutnya ›</button>
            </div>
          </div>
        )}
      </div>

      {modal && (
        <Modal title={modal === 'add' ? 'Tambah Pengguna Baru' : 'Edit Pengguna'} onClose={() => setModal(null)}>
          <div className="form-group">
            <label>Nama Lengkap</label>
            <input className="form-input" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Nama lengkap" />
          </div>
          <div className="form-group">
            <label>Username</label>
            <input className="form-input" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} placeholder="Username" />
          </div>
          {modal === 'add' && (
            <div className="form-group">
              <label>Password</label>
              <input className="form-input" type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="Password" />
            </div>
          )}
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
