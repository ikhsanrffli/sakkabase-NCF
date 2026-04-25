# Sakka Base — Sistem Rekomendasi Menu NCF

Aplikasi frontend React JS untuk sistem rekomendasi menu berbasis **Neural Collaborative Filtering (NCF)** di Sakka Base Coffee & Barber.

---

## Struktur File

```
sakka-base-app/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx                        ← Entry point
    ├── App.jsx                         ← Root component
    ├── index.css                       ← Global styles (tema hijau-putih-emas)
    ├── context/
    │   └── AuthContext.jsx             ← State autentikasi global
    ├── data/
    │   └── initialData.js              ← Data awal (users, menus, orders)
    ├── utils/
    │   └── ncfUtils.js                 ← Simulasi skor NCF (ganti dengan API call)
    ├── components/
    │   ├── MainLayout.jsx              ← Sidebar + topbar + routing halaman
    │   └── UI.jsx                      ← Komponen reusable (Modal, SearchBar, dll)
    └── pages/
        ├── LoginPage.jsx               ← Halaman login (Admin & User)
        ├── RegisterPage.jsx            ← Halaman registrasi user baru
        ├── DashboardPage.jsx           ← Dashboard Admin & User
        ├── UsersPage.jsx               ← CRUD Data Pengguna (Admin)
        ├── MenusPage.jsx               ← CRUD Data Menu (Admin)
        ├── OrdersPage.jsx              ← CRUD Data Pemesanan (Admin)
        ├── RecommendationsPage.jsx     ← Lihat rekomendasi semua user (Admin)
        ├── CatalogPage.jsx             ← Katalog menu (User)
        └── MyRecommendationsPage.jsx   ← Rekomendasi personal (User)
```

---

## Cara Menjalankan

```bash
# 1. Masuk ke folder project
cd sakka-base-app

# 2. Install dependencies
npm install

# 3. Jalankan development server
npm run dev

# 4. Buka browser: http://localhost:5173
```

---

## Akun Demo

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| User  | user1    | user123   |
| User  | user2    | user456   |

---

## Use Case yang Diimplementasikan

### Admin
- ✅ Login & Logout
- ✅ Kelola Data Pengguna (CRUD)
- ✅ Kelola Data Menu (CRUD)
- ✅ Kelola Data Pemesanan / Implicit Feedback (CRUD)
- ✅ Lihat Rekomendasi Menu semua user (Top-10 NCF)

### User
- ✅ Register akun baru
- ✅ Login & Logout
- ✅ Lihat Katalog Menu (dengan pencarian & filter kategori)
- ✅ Lihat Rekomendasi Personal (Top-10 NCF)

---

## Menghubungkan ke Backend NCF (Python/PyTorch)

Buka file `src/utils/ncfUtils.js` dan ganti fungsi `getNCFRecommendations` dengan pemanggilan API nyata:

```js
export async function getNCFRecommendations(userId, menus, orders, topN = 10) {
  const res = await fetch(`http://localhost:8000/api/recommend?user_id=${userId}&top_n=${topN}`);
  const data = await res.json();
  // data.recommendations = [{menuId, menuName, score}, ...]
  return data.recommendations.map(r => ({
    ...menus.find(m => m.id === r.menuId),
    score: r.score
  }));
}
```

---

## Teknologi

- **React 18** + **Vite**
- **Pure CSS** (tidak menggunakan UI library eksternal)
- Tema: Hijau (#1a7a3e), Putih, Kuning Emas (#c9a227)
- Responsive untuk semua ukuran layar
