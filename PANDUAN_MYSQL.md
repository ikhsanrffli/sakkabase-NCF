# Panduan Integrasi MySQL (Tahap 2 — Integrasi Penuh)

Website kini **membaca DAN menulis** seluruh data (users, menus, orders) **dari/ke
MySQL** lewat backend FastAPI. Data historis sudah ada dari
`database/sakkabase_seed.sql`.

> **Tahap 2 (integrasi penuh):** aplikasi memuat daftar pengguna, menu, dan
> pesanan langsung dari MySQL. Registrasi & pemesanan baru ditulis ke MySQL dan
> **bertahan setelah refresh** (bisa login lagi). Bila backend/MySQL mati,
> aplikasi otomatis **fallback** ke data bawaan (`initialData.js`) agar tetap jalan.

**Yang dibaca dari MySQL saat aplikasi dibuka:**
- Tabel `users` → halaman Login & Data Pengguna
- Tabel `menu_items` → Data Menu, Lihat Menu, Pesan Menu
- Tabel `orders` + `order_details` → Data Pemesanan, Riwayat, Rekomendasi

---

## 1. Prasyarat — pastikan database sudah ada
Import sekali (kalau belum) lewat phpMyAdmin atau terminal:
```bash
mysql -u root -p nama_database_anda < database/sakkabase_seed.sql
```
Ini membuat 6 tabel + mengisi data historis. Catat **nama database**-nya.

## 2. Set koneksi database (DATABASE_URL)
Backend membaca koneksi dari environment variable `DATABASE_URL`. Formatnya:
```
mysql+pymysql://USER:PASSWORD@HOST:PORT/NAMA_DATABASE
```

**Windows (PowerShell)** — jalankan di terminal backend sebelum uvicorn:
```powershell
$env:DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/sakkabase_ncf"
```
(XAMPP/Laragon biasanya user `root` tanpa password. Ganti `sakkabase_ncf`
dengan nama database Anda. Kalau ada password: `root:passwordku@...`.)

**Mac/Linux:**
```bash
export DATABASE_URL="mysql+pymysql://root:password@127.0.0.1:3306/sakkabase_ncf"
```

> Jika `DATABASE_URL` tidak diset, default ke `root@127.0.0.1/sakkabase_ncf` tanpa password.

## 3. Install dependency & jalankan backend
```bash
pip install -r backend/requirements.txt
cd backend
# set DATABASE_URL dulu (langkah 2), lalu:
python -m uvicorn main:app --port 8000
```
Cek koneksi DB: buka `http://localhost:8000/db/health` → harus muncul
`{"status":"ok","users_in_db": ...}`. Kalau `"status":"error"`, periksa
DATABASE_URL / MySQL menyala.

## 4. Uji & buktikan tersimpan
1. Jalankan website (`npm run dev`) di terminal lain.
2. **Registrasi** akun baru (mis. "Penguji A").
3. **Pesan** beberapa menu.
4. Buka **phpMyAdmin** → database Anda:
   - Tabel **`users`** → ada baris baru dengan `source = registered`.
   - Tabel **`orders`** & **`order_details`** → ada pesanan baru.

Atau cek via API: `http://localhost:8000/db/users`.

5. **Bukti Tahap 2:** setelah registrasi, **refresh** browser (F5) lalu login lagi
   dengan akun itu — **masih bisa** (karena dibaca dari MySQL). Halaman Data
   Pengguna (admin) juga menampilkan user dari database.

---

## Endpoint yang tersedia
| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/db/health` | Status koneksi DB |
| GET | `/db/users` | Baca semua user (login & Data Pengguna) |
| GET | `/db/menus` | Baca semua menu (Data Menu, katalog) |
| GET | `/db/orders` | Baca semua pesanan (Data Pemesanan, riwayat) |
| POST | `/db/register` | Simpan user baru (otomatis dari halaman Register) |
| POST | `/db/order` | Simpan pesanan (otomatis saat checkout) |

## Catatan
- Penyimpanan bersifat **best-effort**: bila backend/MySQL mati, website tetap
  jalan (data di memori) — tidak error. Begitu backend hidup, data tersimpan lagi.
- `order_details.menu_item_id` dipetakan dari **kode menu** (`item_id`) ke id tabel
  `menu_items`. Pastikan `menu_items` sudah terisi dari seed SQL.
- Password disimpan apa adanya (sesuai aplikasi). Untuk produksi sebaiknya di-hash.
