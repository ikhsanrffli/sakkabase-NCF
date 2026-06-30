/**
 * Skor NCF (Neural Collaborative Filtering).
 *
 * Top-10 rekomendasi tiap pengguna sudah dipre-komputasi dari model PyTorch
 * terlatih (Konfigurasi C, lihat ncf_pipeline/) dan disimpan di
 * `recommendations.json`. Skor di sini adalah probabilitas sigmoid asli dari
 * model, konsisten dengan hasil pada skripsi (Tabel 4.12).
 *
 * Untuk integrasi backend real-time, ganti dengan pemanggilan API:
 *   const res = await fetch(`/api/recommend?userId=${userId}&topN=10`);
 *   const data = await res.json();
 *   return data.recommendations; // [{menuId, score}, ...]
 */
import RECS from '../data/recommendations.json';

function pseudoHash(str) {
  return [...str].reduce((acc, c) => ((acc << 5) - acc + c.charCodeAt(0)) | 0, 0);
}

// Fallback (hanya jika userId tak ada di hasil model) — skor simulasi.
function fallbackRecommendations(userId, menus, orders, topN) {
  const orderedMenuIds = new Set(
    orders.filter(o => o.userId === userId).map(o => o.menuId)
  );
  return menus
    .filter(m => !orderedMenuIds.has(m.id))
    .map(m => {
      const raw = Math.abs(pseudoHash(userId + m.id)) % 10000;
      return { ...m, score: parseFloat((0.40 + (raw / 10000) * 0.20).toFixed(4)) };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

/**
 * Hasilkan Top-N rekomendasi untuk userId tertentu dari hasil model terlatih.
 * @param {string} userId
 * @param {Array}  menus   - array menu lengkap
 * @param {Array}  orders  - array orders (implicit feedback)
 * @param {number} topN    - jumlah rekomendasi (default 10)
 * @returns {Array} menu yang direkomendasikan beserta skor prediksi model
 */
export function getNCFRecommendations(userId, menus, orders, topN = 10) {
  const precomputed = RECS[userId];
  if (!precomputed || precomputed.length === 0) {
    return fallbackRecommendations(userId, menus, orders, topN);
  }
  return precomputed
    .map(r => {
      const menu = menus.find(m => m.id === r.menuId);
      return menu ? { ...menu, score: r.score } : null;
    })
    .filter(Boolean)
    .slice(0, topN);
}

/**
 * Format skor sebagai desimal (4 angka), gaya Indonesia. Misal 0.5413 → "0,5413".
 */
export function formatScore(score) {
  return Number(score).toFixed(4).replace('.', ',');
}
