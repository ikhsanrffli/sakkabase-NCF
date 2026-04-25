/**
 * Simulasi skor NCF (Neural Collaborative Filtering).
 * Pada produksi, ganti fungsi ini dengan pemanggilan API backend Python/PyTorch.
 *
 * Contoh pemanggilan API nyata:
 *   const res = await fetch(`/api/recommend?userId=${userId}&topN=10`);
 *   const data = await res.json();
 *   return data.recommendations; // [{menuId, menuName, score}, ...]
 */

function pseudoHash(str) {
  return [...str].reduce((acc, c) => ((acc << 5) - acc + c.charCodeAt(0)) | 0, 0);
}

/**
 * Hasilkan Top-N rekomendasi untuk userId tertentu.
 * @param {string} userId
 * @param {Array}  menus   - array menu lengkap
 * @param {Array}  orders  - array orders (implicit feedback)
 * @param {number} topN    - jumlah rekomendasi (default 10)
 * @returns {Array} menu yang direkomendasikan beserta skor prediksi
 */
export function getNCFRecommendations(userId, menus, orders, topN = 10) {
  const orderedMenuIds = new Set(
    orders.filter(o => o.userId === userId).map(o => o.menuId)
  );

  const candidates = menus.filter(m => !orderedMenuIds.has(m.id));

  const scored = candidates.map(m => {
    const raw = Math.abs(pseudoHash(userId + m.id)) % 10000;
    const score = parseFloat((0.55 + (raw / 10000) * 0.44).toFixed(4));
    return { ...m, score };
  });

  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, topN);
}

/**
 * Format skor sebagai persentase string, misal 0.8734 → "87.3%"
 */
export function formatScore(score) {
  return (score * 100).toFixed(1) + '%';
}
