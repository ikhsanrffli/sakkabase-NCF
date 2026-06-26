# Panduan Integrasi MySQL (Write-through)

Setiap **registrasi user baru** dan **pemesanan** di website kini **disimpan ke
MySQL** lewat backend FastAPI. Data historis (871 pelanggan dll) sudah ada dari
`database/sakkabase_seed.sql`.

> Catatan lingkup: ini **write-through** — data baru DITULIS ke MySQL. Tampilan
> aplikasi masih memakai data bawaan; yang penting **data tersimpan permanen di DB**
> dan bisa Anda tunjukkan di phpMyAdmin.

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

Atau cek via API: `http://localhost:8000/db/users` (20 user terbaru).

---

## Endpoint yang tersedia
| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/db/health` | Status koneksi DB |
| POST | `/db/register` | Simpan user baru (otomatis dari halaman Register) |
| POST | `/db/order` | Simpan pesanan (otomatis saat checkout) |
| GET | `/db/users` | Lihat user terbaru (verifikasi) |

## Catatan
- Penyimpanan bersifat **best-effort**: bila backend/MySQL mati, website tetap
  jalan (data di memori) — tidak error. Begitu backend hidup, data tersimpan lagi.
- `order_details.menu_item_id` dipetakan dari **kode menu** (`item_id`) ke id tabel
  `menu_items`. Pastikan `menu_items` sudah terisi dari seed SQL.
- Password disimpan apa adanya (sesuai aplikasi). Untuk produksi sebaiknya di-hash.
