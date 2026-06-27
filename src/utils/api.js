// Helper pemanggilan backend FastAPI (persistensi MySQL).
// Bersifat best-effort: bila backend mati, aplikasi tetap jalan (data di memori).
export const API_BASE = 'http://localhost:8000';

/** Simpan user baru ke tabel `users` MySQL (source = 'registered'). */
export function persistUserToDB(user) {
  return fetch(`${API_BASE}/db/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nama_lengkap: user.name,
      username: user.username,
      password: user.password,
    }),
  })
    .then(r => r.json())
    .catch(() => null); // diam-diam abaikan bila backend offline
}

/** Simpan pesanan ke `orders` + `order_details` MySQL. */
export function persistOrderToDB(username, menuCodes, tanggal) {
  return fetch(`${API_BASE}/db/order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, menuCodes, tanggal }),
  })
    .then(r => r.json())
    .catch(() => null);
}

/** Helper POST JSON ke backend; mengembalikan {ok:false} bila backend offline. */
function postJSON(path, body) {
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
    .then(r => r.json())
    .catch(() => ({ ok: false, message: 'Backend tidak aktif. Jalankan FastAPI lalu coba lagi.' }));
}

/** Admin: tambah pengguna ke MySQL. */
export function addUserToDB(user) {
  return postJSON('/db/user/add', {
    nama_lengkap: user.name, username: user.username, password: user.password,
  });
}

/** Admin: ubah pengguna di MySQL. password kosong = tidak diubah. */
export function updateUserInDB(user) {
  return postJSON('/db/user/update', {
    id: Number(user.id), nama_lengkap: user.name,
    username: user.username, password: user.password || null,
  });
}

/** Admin: hapus pengguna + riwayat pesanannya di MySQL. */
export function deleteUserFromDB(id) {
  return postJSON('/db/user/delete', { id: Number(id) });
}
