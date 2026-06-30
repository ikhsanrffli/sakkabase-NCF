# 3.3.2 Perancangan Basis Data — (Tabel 3.26–3.31)

> Diambil **persis** dari skema database program (`database/sakkabase_seed.sql`)
> dan kode backend (`backend/db.py`). Nama tabel, tipe data, dan relasi sama
> dengan implementasi nyata pada web & program.

## Paragraf pengantar (siap tempel)
Sistem rekomendasi menu pada Sakka Base menggunakan *Relational Database
Management System* (RDBMS) MySQL untuk menyimpan dan mengelola data penelitian.
Basis data terdiri atas **enam tabel** yang saling berelasi, yaitu `users`,
`menu_items`, `orders`, `order_details`, `recommendations`, dan `model_log`.
Tabel `order_details` berperan sebagai sumber **umpan balik implisit (implicit
feedback)**, di mana setiap baris merepresentasikan satu interaksi positif antara
seorang pelanggan dengan sebuah item menu. Struktur relasi antar tabel
ditampilkan pada Gambar 3.31. Rincian struktur masing-masing tabel adalah sebagai
berikut.

---

## 1. Tabel Users
Menyimpan data identitas dan kredensial pengguna aplikasi (Admin dan Pelanggan).

**Tabel 3.26 Users**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key, AUTO_INCREMENT — identitas unik pengguna |
| nama_lengkap | varchar(100) | Nama lengkap pengguna |
| username | varchar(50) | Nama pengguna untuk login (unik) |
| password | varchar(255) | Kata sandi pengguna |
| role | enum('admin','user') | Hak akses pengguna (default: 'user') |
| source | enum('historical','registered') | Sumber data: historis atau hasil registrasi (default: 'historical') |
| created_at | datetime | Waktu data dibuat |

---

## 2. Tabel Menu_Items
Menyimpan katalog menu yang tersedia di kafe.

**Tabel 3.27 Menu_Items**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key, AUTO_INCREMENT — identitas unik di database |
| item_id | varchar(100) | Kode referensi item menu (mis. 'A00A') |
| nama_menu | varchar(150) | Nama item menu |
| kategori | varchar(100) | Kategori menu |
| price | int | Harga menu (Rupiah), default 0 |
| created_at | datetime | Waktu data dibuat |
| updated_at | datetime | Waktu data diperbarui |

---

## 3. Tabel Orders
Merekam riwayat transaksi pemesanan yang menjadi sumber umpan balik implisit.

**Tabel 3.28 Orders**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key, AUTO_INCREMENT — identitas transaksi |
| user_id | int(11) | Foreign Key, merujuk ke tabel `users` (id) |
| total | int | Total harga seluruh item dalam transaksi (default 0) |
| tanggal | date | Tanggal transaksi dilakukan |
| created_at | datetime | Waktu data dicatat |

---

## 4. Tabel Order_Details
Berfungsi sebagai *implicit feedback* bagi model NCF; setiap baris
merepresentasikan satu interaksi positif antara pengguna dan item menu.

**Tabel 3.29 Order_Details**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int | Primary Key, AUTO_INCREMENT |
| order_id | int | Foreign Key, merujuk ke tabel `orders` (id) |
| menu_item_id | int | Foreign Key, merujuk ke tabel `menu_items` (id) |
| qty | tinyint | Kuantitas item yang dipesan (default 1) |
| price | int | Harga per item saat transaksi (default 0) |

---

## 5. Tabel Recommendations
Menyimpan daftar rekomendasi menu (Top-N) yang diprediksi model untuk pengguna.

**Tabel 3.30 Recommendations**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key, AUTO_INCREMENT |
| user_id | int(11) | Foreign Key, merujuk ke tabel `users` (id) |
| menu_item_id | int(11) | Foreign Key, merujuk ke tabel `menu_items` (id) |
| rank | tinyint(4) | Urutan peringkat rekomendasi (1–10) |
| score | float | Skor probabilitas (sigmoid) dari model |
| generated_at | datetime | Waktu rekomendasi dihitung |

---

## 6. Tabel Model_Log
Mencatat log status pelatihan dan hasil evaluasi performa model NCF.

**Tabel 3.31 Model_Log**

| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key, AUTO_INCREMENT |
| status | enum('training','ready','error') | Status proses model (default: 'ready') |
| model_path | varchar(255) | Lokasi penyimpanan file model |
| hr_at_10 | float | Nilai evaluasi metrik Hit Ratio@10 |
| ndcg_at_10 | float | Nilai evaluasi metrik NDCG@10 |
| trained_at | datetime | Waktu pelatihan selesai |
| error_log | text | Catatan pesan error (jika ada) |
| created_at | datetime | Waktu log dibuat |

> **Catatan penamaan:** tabel log model bernama **`model_log`** (sebelumnya tertulis
> "Model_Status" di draf — sudah diperbarui agar sesuai nama di database).

---

## Relasi antar tabel (untuk deskripsi Gambar 3.31 / ERD)
| Tabel Anak | Kolom (FK) | Merujuk ke Tabel Induk |
|---|---|---|
| `orders` | user_id | `users` (id) |
| `order_details` | order_id | `orders` (id) |
| `order_details` | menu_item_id | `menu_items` (id) |
| `recommendations` | user_id | `users` (id) |
| `recommendations` | menu_item_id | `menu_items` (id) |

Tabel `model_log` bersifat mandiri (tabel log) sehingga tidak memiliki relasi ke
tabel lain.

---

## Paragraf penutup (pengisian data — angka NYATA)
Basis data diisi dari hasil praproses dataset transaksi Sakka Base. Tabel `users`
memuat **872 baris** (1 akun Admin + **871 pelanggan** unik), tabel `menu_items`
memuat **141 item menu**, tabel `orders` memuat **1.211 transaksi**, dan tabel
`order_details` memuat **4.908 baris interaksi** sebagai umpan balik implisit bagi
model. Tabel `recommendations` diisi secara dinamis dengan hasil Top-10
rekomendasi tiap pengguna, sedangkan tabel `model_log` menyimpan satu baris status
model final dengan capaian **HR@10 = 0,3500** dan **NDCG@10 = 0,1822**.
