import { useState } from 'react';
import { SearchBar, EmptyState, Pill, useConfirm } from '../components/UI';
import { api } from '../api/apiClient';

export default function UsersPage({ users, setUsers, setOrders }) {
  const [search, setSearch] = useState('');
  const { confirm, ConfirmDialog } = useConfirm();

  const regUsers = users.filter(u => u.source === 'registered');
  const filtered = regUsers.filter(u =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.username.toLowerCase().includes(search.toLowerCase())
  );

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
          <SearchBar value={search} onChange={setSearch} placeholder="Cari pengguna..." />
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
                  <td>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(u)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
