import { useState } from 'react';
import { SearchBar, EmptyState, Pill, useConfirm } from '../components/UI';
import { api } from '../api/apiClient';

const EMPTY_FORM = { nama_lengkap: '', username: '', password: '', role: 'user' };

export default function UsersPage({ users, setUsers, setOrders }) {
  const [search, setSearch]       = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editTarget, setEditTarget] = useState(null); // null = tambah, obj = edit
  const [form, setForm]           = useState(EMPTY_FORM);
  const [formErr, setFormErr]     = useState('');
  const [saving, setSaving]       = useState(false);
  const { confirm, ConfirmDialog } = useConfirm();

  const regUsers = users.filter(u => u.source === 'registered');
  const filtered = regUsers.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.username.toLowerCase().includes(search.toLowerCase())
  );

  function openAdd() {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormErr('');
    setShowModal(true);
  }

  function openEdit(user) {
    setEditTarget(user);
    setForm({ nama_lengkap: user.name, username: user.username, password: '', role: user.role });
    setFormErr('');
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setFormErr('');
  }

  async function handleSave() {
    if (!form.nama_lengkap.trim() || !form.username.trim()) {
      setFormErr('Nama lengkap dan username wajib diisi.');
      return;
    }
    if (!editTarget && !form.password.trim()) {
      setFormErr('Password wajib diisi untuk user baru.');
      return;
    }
    setSaving(true);
    setFormErr('');
    try {
      if (editTarget) {
        const payload = { nama_lengkap: form.nama_lengkap, username: form.username, role: form.role };
        if (form.password.trim()) payload.password = form.password;
        const updated = await api.updateUser(editTarget.id, payload);
        setUsers(prev => prev.map(u => u.id === editTarget.id
          ? { ...u, name: updated.nama_lengkap, username: updated.username, role: updated.role }
          : u
        ));
      } else {
        const created = await api.createUser(form.nama_lengkap, form.username, form.password, form.role);
        setUsers(prev => [...prev, {
          id: created.id, name: created.nama_lengkap, username: created.username,
          role: created.role, source: created.source,
        }]);
      }
      closeModal();
    } catch (err) {
      setFormErr(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(user) {
    const ok = await confirm(`Hapus pengguna "${user.name}"? Data pemesanannya juga akan ikut terhapus.`);
    if (!ok) return;
    try {
      await api.deleteUser(user.id);
      setUsers(prev => prev.filter(u => u.id !== user.id));
      setOrders(prev => prev.filter(o => o.userId !== user.id));
    } catch (err) {
      alert('Gagal menghapus pengguna: ' + err.message);
    }
  }

  return (
    <>
      {ConfirmDialog}

      <div className="page-card">
        <div className="card-header">
          <div className="card-header-title">Daftar Pengguna ({regUsers.length} user)</div>
          <div style={{ display: 'flex', gap: '.5rem', alignItems: 'center' }}>
            <SearchBar value={search} onChange={setSearch} placeholder="Cari pengguna..." />
            <button className="btn btn-primary" style={{ whiteSpace: 'nowrap' }} onClick={openAdd}>
              + Tambah User
            </button>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>No</th><th>Nama</th><th>Username</th><th>Sumber</th><th>Peran</th><th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={6}><EmptyState icon="👤" message="Tidak ada pengguna ditemukan." /></td></tr>
              ) : filtered.map((u, i) => (
                <tr key={u.id}>
                  <td style={{ color: 'var(--gray3)' }}>{i + 1}</td>
                  <td><strong>{u.name}</strong></td>
                  <td><span className="mono">{u.username}</span></td>
                  <td><Pill variant="gold">{u.source || 'registered'}</Pill></td>
                  <td><Pill variant="green">{u.role}</Pill></td>
                  <td style={{ display: 'flex', gap: '.4rem' }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => openEdit(u)}>Edit</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(u)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Tambah / Edit */}
      {showModal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && closeModal()}>
          <div className="modal-box" style={{ maxWidth: 420 }}>
            <div className="modal-title">{editTarget ? '✏️ Edit Pengguna' : '➕ Tambah Pengguna'}</div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
              <div>
                <label className="form-label">Nama Lengkap</label>
                <input
                  className="form-input"
                  value={form.nama_lengkap}
                  onChange={e => setForm(f => ({ ...f, nama_lengkap: e.target.value }))}
                  placeholder="Nama lengkap..."
                />
              </div>
              <div>
                <label className="form-label">Username</label>
                <input
                  className="form-input"
                  value={form.username}
                  onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                  placeholder="Username..."
                />
              </div>
              <div>
                <label className="form-label">
                  Password {editTarget && <span style={{ color: 'var(--gray3)', fontSize: '.75rem' }}>(kosongkan jika tidak ingin diubah)</span>}
                </label>
                <input
                  className="form-input"
                  type="password"
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  placeholder={editTarget ? 'Password baru (opsional)...' : 'Password...'}
                />
              </div>
              <div>
                <label className="form-label">Peran</label>
                <select
                  className="form-select"
                  style={{ width: '100%' }}
                  value={form.role}
                  onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              {formErr && (
                <div style={{ background: '#fdf0f0', border: '1px solid #e74c3c', borderRadius: 8,
                  padding: '.6rem .8rem', fontSize: '.82rem', color: '#c0392b' }}>
                  ⚠️ {formErr}
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={closeModal} disabled={saving}>Batal</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? '⏳ Menyimpan...' : editTarget ? 'Simpan Perubahan' : 'Tambah User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
