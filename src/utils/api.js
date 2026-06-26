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
