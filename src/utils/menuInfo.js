// Helper deskripsi & harga menu untuk halaman katalog/detail.
// Harga memakai kolom `price` dari database bila tersedia (>0); jika tidak,
// dibuat estimasi deterministik per kategori (silakan ganti dengan harga asli).

const CAT_PRICE = {
  'Kopi & Espresso': [18000, 30000], 'Non-Kopi': [20000, 30000], 'Juice': [18000, 25000],
  'Minuman': [5000, 20000], 'Croissant & Pastry': [15000, 30000], 'Pudding': [15000, 20000],
  'Snack Ringan': [10000, 25000], 'Gorengan & Snack': [15000, 30000], 'Toast': [20000, 30000],
  'Nasi Goreng': [22000, 35000], 'Nasi Lauk': [25000, 45000], 'Mie & Bihun': [20000, 32000],
  'Pasta': [30000, 45000], 'Indomie': [15000, 25000], 'Chicken Steak': [35000, 55000],
  'Salad': [30000, 40000], 'Ricebowl': [30000, 40000], 'Sayur': [10000, 20000],
  'Ice Cream': [18000, 22000], 'Barber': [35000, 150000], 'Tambahan': [3000, 15000],
  'Lainnya': [5000, 30000],
};

function hashStr(s) {
  let a = 0;
  for (const c of String(s)) a = (a * 31 + c.charCodeAt(0)) >>> 0;
  return a;
}

export function menuPrice(m) {
  if (m.price && m.price > 0) return m.price;          // pakai harga DB bila ada
  const [lo, hi] = CAT_PRICE[m.category] || [15000, 30000];
  const span = Math.floor((hi - lo) / 1000) + 1;
  return lo + (hashStr(m.id) % span) * 1000;
}

export function formatRupiah(n) {
  return 'Rp ' + Number(n).toLocaleString('id-ID');
}

const CAT_DESC = {
  'Kopi & Espresso': 'Racikan kopi khas Sakka Base dengan aroma dan cita rasa yang nikmat.',
  'Non-Kopi': 'Minuman non-kopi creamy yang menyegarkan, cocok untuk segala suasana.',
  'Juice': 'Jus buah segar tanpa pengawet, menyehatkan dan menyegarkan.',
  'Minuman': 'Minuman penyegar untuk menemani aktivitas Anda.',
  'Croissant & Pastry': 'Pastry renyah berlapis mentega, dipanggang segar setiap hari.',
  'Pudding': 'Puding lembut dengan tekstur yang lumer di mulut.',
  'Snack Ringan': 'Camilan ringan yang pas untuk teman ngobrol.',
  'Gorengan & Snack': 'Gorengan hangat dan renyah, nikmat disantap kapan saja.',
  'Toast': 'Roti panggang dengan topping melimpah dan gurih.',
  'Nasi Goreng': 'Nasi goreng dengan bumbu khas yang menggugah selera.',
  'Nasi Lauk': 'Hidangan nasi lengkap dengan lauk pilihan yang mengenyangkan.',
  'Mie & Bihun': 'Olahan mie/bihun dengan bumbu kaya rasa.',
  'Pasta': 'Pasta ala Western dengan saus pilihan yang lezat.',
  'Indomie': 'Mie instan favorit dengan racikan spesial Sakka Base.',
  'Chicken Steak': 'Steak ayam juicy dengan saus dan pelengkap istimewa.',
  'Salad': 'Salad segar dengan dressing pilihan, sehat dan ringan.',
  'Ricebowl': 'Ricebowl praktis dengan topping melimpah.',
  'Sayur': 'Olahan sayur segar yang sehat dan lezat.',
  'Ice Cream': 'Es krim lembut dengan cita rasa manis yang menyegarkan.',
  'Barber': 'Layanan barber profesional khas Sakka Base.',
  'Tambahan': 'Menu tambahan pelengkap pesanan Anda.',
  'Lainnya': 'Produk pilihan dari Sakka Base.',
};

export function menuDescription(m) {
  return CAT_DESC[m.category] || `Menu ${m.name} pilihan dari Sakka Base.`;
}

// Estimasi penyajian / porsi per kategori (untuk info tambahan di detail).
const CAT_SERVING = {
  'Kopi & Espresso': 'Disajikan panas/dingin · 1 cangkir',
  'Non-Kopi': 'Disajikan dingin · 1 gelas',
  'Juice': 'Segar dingin · 1 gelas (±300 ml)',
  'Minuman': 'Disajikan dingin · 1 botol/gelas',
  'Croissant & Pastry': 'Dipanggang segar · 1 porsi',
  'Pudding': 'Disajikan dingin · 1 cup',
  'Snack Ringan': 'Camilan · 1 bungkus/porsi',
  'Gorengan & Snack': 'Disajikan hangat · 1 porsi',
  'Toast': 'Disajikan hangat · 1 porsi',
  'Nasi Goreng': 'Disajikan hangat · 1 piring',
  'Nasi Lauk': 'Disajikan hangat · 1 piring + nasi',
  'Mie & Bihun': 'Disajikan hangat · 1 porsi',
  'Pasta': 'Disajikan hangat · 1 piring',
  'Indomie': 'Disajikan hangat · 1 porsi',
  'Chicken Steak': 'Disajikan hangat · 1 porsi + pelengkap',
  'Salad': 'Disajikan segar · 1 mangkuk',
  'Ricebowl': 'Disajikan hangat · 1 mangkuk',
  'Sayur': 'Disajikan hangat · 1 porsi',
  'Ice Cream': 'Disajikan beku · 1 scoop/cup',
  'Barber': 'Layanan · per sesi',
  'Tambahan': 'Pelengkap · 1 porsi',
  'Lainnya': '1 item',
};

export function menuServing(m) {
  return CAT_SERVING[m.category] || '1 porsi';
}

/** Label popularitas dari jumlah pesanan. */
export function popularityLabel(count) {
  if (count >= 50) return { text: 'Sangat Populer', variant: 'gold' };
  if (count >= 15) return { text: 'Populer', variant: 'green' };
  if (count >= 1) return { text: 'Reguler', variant: 'green' };
  return { text: 'Menu Baru', variant: 'green' };
}
