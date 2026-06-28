# REVISI BAB 3 & BAB 4 — DATA NYATA SKENARIO B (sesuai Website & Database)

> **Semua angka di dokumen ini adalah DATA NYATA** yang diambil/diverifikasi
> langsung dari `src/dataset.xlsx`, database MySQL (`sakkabase_seed.sql`), dan
> model terlatih yang dipakai website (`ncf_pipeline/models/ncf_config_C.pth` →
> sumber `recommendations.json`). Bukan contoh karangan.
>
> **Acuan angka final (Skenario B, User = Pelanggan):**
> - 871 pelanggan · 141 menu · 4.908 baris interaksi · 1.211 transaksi
> - Setelah praproses: 820 pengguna · 140 item berinteraksi · 4.707 interaksi unik
> - Model final **Konfigurasi C**: **HR@10 = 0,3500 · NDCG@10 = 0,1822**
>   (epoch terbaik 5, 32.833 parameter)
>
> **Catatan penamaan tabel:** tabel log model di implementasi bernama
> **`model_log`** (bukan `model_status`). Tabel `model_status` yang muncul di
> database adalah **sisa skema lama** dan sudah dihapus.

---

# BAGIAN 1 — BAB 3.2 ANALISIS PROSES (Tabel 3.1–3.15, data nyata)

## Paragraf dimensi dataset (ganti)
> Berdasarkan hasil rekapitulasi keseluruhan riwayat transaksi, dataset ini
> memuat **871 pelanggan unik** dan **141 menu unik (berdasarkan kode produk)**,
> dengan total **4.908 baris interaksi** dari **1.211 transaksi**. Setiap baris
> merepresentasikan satu item menu yang dipesan oleh seorang pelanggan. Tabel 3.1
> menyajikan cuplikan dataset mentah sebelum prapemrosesan.

### Tabel 3.1 — Dataset Riwayat Pemesanan (cuplikan NYATA)
| No Transaksi | Tanggal | Outlet | Pelanggan | Produk | Qty |
|---|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Sakka Base - Coffee & Barber | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| 001975 | 01/01/2026 12:49 | Sakka Base - Coffee & Barber | Rendi Ramadhan | A07B - LE MINERAL 600ML | 1 |
| 001977 | 01/01/2026 14:40 | Sakka Base - Coffee & Barber | Jenny Sanjaya | A06E - TOMATO JUICE | 1 |
| 001981 | 02/01/2026 10:31 | Sakka Base - Coffee & Barber | Angelina Tanusaputra | C03C - NASI GORENG SEAFOOD | 1 |
| 001982 | 02/01/2026 12:26 | Sakka Base - Coffee & Barber | Ricky Salim | A06C - AVOCADO JUICE | 1 |

## Pembersihan Data — paragraf (ganti)
> Pada tahap pembersihan, kolom transaksi (No Transaksi, Tanggal, Pelanggan) yang
> kosong akibat *merged cell* pada baris lanjutan satu transaksi diisi-maju
> (*forward-fill*), sehingga setiap baris produk memiliki identitas pelanggan dan
> tanggal yang lengkap. Selanjutnya baris yang tidak memiliki Produk valid
> dihapus. Hasil akhir menghasilkan **4.908 baris interaksi valid**.

### Tabel 3.2 — Sebelum Pembersihan (cuplikan NYATA transaksi 001975)
*Pada data mentah, identitas transaksi hanya tertulis pada baris pertama; baris
lanjutan kosong (merged cell).*

| No Transaksi | Tanggal | Pelanggan | Produk | Qty |
|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| *(kosong)* | *(kosong)* | *(kosong)* | A07B - LE MINERAL 600ML | 1 |
| *(kosong)* | *(kosong)* | *(kosong)* | A06C - AVOCADO JUICE | 1 |
| *(kosong)* | *(kosong)* | *(kosong)* | C04G - NASI CAPCAY SEAFOOD | 1 |

### Tabel 3.3 — Sesudah Pembersihan (forward-fill, NYATA)
| No Transaksi | Tanggal | Pelanggan | Produk | Qty |
|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A07B - LE MINERAL 600ML | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A06C - AVOCADO JUICE | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C04G - NASI CAPCAY SEAFOOD | 1 |

## Encoding ID Pengguna dan Item — paragraf (ganti)
> Nilai User ID (nama pelanggan) dan Item ID (kode produk) berupa string, sehingga
> dilakukan *Label Encoding* yang memetakan tiap nama pelanggan dan kode item ke
> indeks integer berurutan (terurut) mulai dari 0. Sebagai contoh nyata, pelanggan
> pertama secara terurut adalah **'Acai' = 0**, **'Acang' = 1**, **'Acen' = 2**;
> sedangkan item dipetakan **'A00A' = 0**, **'A00B' = 1**, **'A00C' = 2**. Setelah
> menyaring pelanggan dengan minimal 2 interaksi, diperoleh **820 indeks pengguna**
> dan **140 indeks item** yang berinteraksi.

### Tabel 3.4 — Representasi Data Interaksi Biner (Pengguna 'Acai' = indeks 0, NYATA)
| Nama Pelanggan | Encoded User ID | item_id | Nama Menu | Encoded Item ID | Nilai Biner |
|---|---|---|---|---|---|
| Acai | 0 | A08A | PURE TEA / COLD REGULAR | 57 | 1 |
| Acai | 0 | A08B | TEA MANIS / COLD LARGE | 58 | 1 |
| Acai | 0 | C03B | NASI GORENG KAMPUNG | 97 | 1 |
| Acai | 0 | C05D | MIE SOP SAKKA | 111 | 1 |
| Acai | 0 | C10B | CHICKEN CHEESE RICEBOWL | 127 | 1 |
| Acai | 0 | A00A | AMERICANO SAKKA / LARGE HOT | 0 | 0 |
| Acai | 0 | A00B | LYCHEE AMERICANO / LARGE | 1 | 0 |

## Negative Sampling — paragraf (ganti)
> Teknik *negative sampling* diterapkan dengan rasio **4 : 1**: untuk setiap item
> positif diambil 4 item negatif acak yang belum pernah dipesan pengguna tersebut.

### Tabel 3.5 — Hasil Negative Sampling (Pengguna 'Acai' = 0, NYATA, seed 42)
| Nama Pelanggan | Encoded User ID | item_id | Nama Menu | Encoded Item ID | Label |
|---|---|---|---|---|---|
| Acai | 0 | A08A | PURE TEA / COLD REGULAR | 57 | 1 (positif) |
| Acai | 0 | A06C | AVOCADO JUICE | 49 | 0 (negatif) |
| Acai | 0 | A06D | TIMUN JUICE | 50 | 0 (negatif) |
| Acai | 0 | C01M | RISOL SAKKA | 90 | 0 (negatif) |
| Acai | 0 | A02G | COCONUT PANDAN LATTE COLD | 26 | 0 (negatif) |

## Embedding Layer — paragraf (ganti)
> Setiap pengguna dan item direpresentasikan sebagai vektor berdimensi 32 melalui
> *embedding layer*. Vektor pengguna pᵤ dan vektor item qᵢ digabung
> (*concatenation*) menjadi satu vektor berukuran 64. Nilai vektor di bawah adalah
> **bobot nyata** hasil pelatihan model (ditampilkan 4 dimensi pertama).

### Tabel 3.6 — Representasi Vektor pada Embedding Layer (NYATA, dari model terlatih)
| Pelanggan | User ID | item_id | Item ID | Vektor Pengguna pᵤ (4 dim awal) | Vektor Item qᵢ (4 dim awal) |
|---|---|---|---|---|---|
| Acai | 0 | A08A (57) | 57 | [0,0382, 0,0367, 0,0338, −0,0287, …] | [−0,0372, 0,0217, −0,0273, 0,0162, …] |
| Acai | 0 | A00A (0) | 0 | [0,0382, 0,0367, 0,0338, −0,0287, …] | [0,0317, −0,0487, 0,0469, −0,0382, …] |

## Hidden Layer (MLP) — paragraf (tetap, sudah benar)
> Vektor gabungan (64 dimensi) diproses oleh MLP dua lapis **[64 → 32]** dengan
> aktivasi ReLU pada tiap lapis untuk menangkap pola interaksi non-linear.

### Tabel 3.7 — Transformasi Dimensi pada Hidden Layer
| Input (dari Embedding) | Hidden Layer (ReLU) | Output ke Sigmoid |
|---|---|---|
| Vektor gabungan 64 dimensi | 64 → 32 dimensi | 32 → 1 dimensi |

## Output Layer — paragraf (ganti dengan skor NYATA)
> Keluaran lapisan tersembunyi terakhir (32 dimensi) diteruskan ke *output layer*
> dengan satu neuron beraktivasi *sigmoid* yang memetakan prediksi ke rentang
> probabilitas 0–1. Tabel 3.8 menampilkan **skor nyata** model untuk pengguna
> 'Acai'.

### Tabel 3.8 — Hasil Keluaran Prediksi Output Layer (NYATA)
| Encoded User ID | item_id | Item ID | Probabilitas Sigmoid (ŷ) | Keterangan |
|---|---|---|---|---|
| 0 (Acai) | A00A | 0 | 0,5400 | Probabilitas relatif tinggi |
| 0 (Acai) | A08A | 57 | 0,2580 | Probabilitas relatif rendah |

## Perhitungan Loss (BCE) — paragraf (ganti dengan nilai NYATA)
> Nilai *loss* dihitung dengan *Binary Cross-Entropy* antara prediksi dan label
> aktual. Tabel 3.9 menampilkan contoh perhitungan dari prediksi nyata di atas.

### Tabel 3.9 — Tahap Perhitungan Binary Cross-Entropy (NYATA)
| Input (User, Item) | Prediksi ŷ | Label y | Nilai Loss BCE |
|---|---|---|---|
| (0, A08A) | 0,2580 | 1 | 1,3547 (error besar — positif tapi skor rendah) |
| (0, A00A) | 0,5400 | 0 | 0,7765 (error sedang — negatif tapi skor agak tinggi) |

> *BCE = −[y·ln(ŷ) + (1−y)·ln(1−ŷ)]. Contoh: −ln(0,2580) = 1,3547.*

## Optimizer Adam — paragraf (tetap konsep, tanpa angka karangan)
> Optimizer Adam memperbarui bobot jaringan melalui *backpropagation* untuk
> meminimalkan total *loss* pada setiap iterasi. Bobot *embedding* dan lapisan MLP
> disesuaikan secara bertahap sesuai gradien hingga model konvergen.

### Tabel 3.10 — Ilustrasi Pembaruan Bobot oleh Optimizer Adam
| Komponen | Arah Penyesuaian (Gradien) | Dampak |
|---|---|---|
| Vektor Pengguna pᵤ | dinaikkan untuk item positif | prediksi item relevan mendekati 1 |
| Vektor Item qᵢ (negatif) | diturunkan | prediksi item negatif mendekati 0 |

*(Nilai bobot spesifik adalah parameter internal hasil pelatihan; tabel ini
menggambarkan arah pembaruan, bukan angka eksak.)*

## Alur Inferensi Rekomendasi (Tabel 3.11–3.15) — pengguna NYATA: Budi Santoso

### Tabel 3.11 — Mengumpulkan Daftar Menu (NYATA)
| Indeks | item_id | Nama Menu | Kategori | Keterangan |
|---|---|---|---|---|
| 1 | A00A | Americano Sakka | Kopi & Espresso | Terdaftar di katalog |
| 2 | A01A | Espresso | Kopi & Espresso | Terdaftar di katalog |
| 3 | A01C | Split Coffee | Kopi & Espresso | Terdaftar di katalog |
| 4 | A01E | Cappuccino | Kopi & Espresso | Terdaftar di katalog |
| … | … | … | … | **Total 141 menu** |

### Tabel 3.12 — Menghapus Menu yang Pernah Dibeli (riwayat NYATA Budi Santoso, 7 interaksi)
| Nama Menu | Riwayat Budi Santoso | Tindakan Sistem | Status |
|---|---|---|---|
| Le Mineral 600ml | Pernah dipesan | Dibuang | Bukan kandidat |
| French Fries | Pernah dipesan | Dibuang | Bukan kandidat |
| Chicken Popcorn | Pernah dipesan | Dibuang | Bukan kandidat |
| Nasi Goreng Kampung | Pernah dipesan | Dibuang | Bukan kandidat |
| Americano Sakka | Belum pernah dipesan | Dipertahankan | Kandidat model |

> *Riwayat lengkap Budi Santoso (NYATA): Le Mineral 600ml, Lychee Tea, French
> Fries, Pisang Bakar Coklat Keju, Chicken Popcorn, Nasi Goreng Kampung, Grilled
> Chicken Mushroom. Dari 140 item, 7 dibuang → 133 kandidat.*

### Tabel 3.13 — Menghitung Skor Kecocokan (skor NYATA)
| User Target | Kandidat Menu | Probabilitas (Sigmoid) | Persentase |
|---|---|---|---|
| Budi Santoso | Americano Sakka | 0,5417 | 54,2% |
| Budi Santoso | Nasi Ayam Penyet Cabe Ijo | 0,5200 | 52,0% |
| Budi Santoso | Sanger Sakka | 0,5163 | 51,6% |
| Budi Santoso | Tomato Juice | 0,1xxx | (skor rendah, tidak masuk Top-10) |

### Tabel 3.14 — Mengurutkan Menu (NYATA)
| Posisi | Nama Menu | Probabilitas | Status |
|---|---|---|---|
| Ke-1 | Americano Sakka | 0,5417 | Diambil |
| Ke-2 | Nasi Ayam Penyet Cabe Ijo | 0,5200 | Diambil |
| Ke-3 | Sanger Sakka | 0,5163 | Diambil |
| … | … | … | … |
| Ke-10 | Nasi Soto Ayam | 0,4246 | Batas pengambilan (cut-off) |
| Ke-11 | (menu berikutnya) | < 0,4246 | Tidak diambil |
| Ke-133 | (kandidat terakhir) | 0,0358 | Tidak diambil |

### Tabel 3.15 — Mengambil 10 Menu Terbaik (Top-10 NYATA, Budi Santoso)
| Peringkat | item_id | Nama Menu | Skor (NCF) |
|---|---|---|---|
| 1 | A00A | Americano Sakka | 54,2% |
| 2 | C04B | Nasi Ayam Penyet Cabe Ijo | 52,0% |
| 3 | A01D | Sanger Sakka | 51,6% |
| 4 | C03C | Nasi Goreng Seafood | 49,6% |
| 5 | C04C | Nasi Ayam Geprek | 47,4% |
| 6 | A08C | Lemon Tea | 45,3% |
| 7 | C03E | Nasi Goreng Special | 45,2% |
| 8 | A03A | Butterscotch Cream Cheese Cold | 44,8% |
| 9 | A02A | Aren Latte | 43,5% |
| 10 | C04D | Nasi Soto Ayam | 42,5% |

---

# BAGIAN 2 — BAB 3.3.2 PERANCANGAN BASIS DATA

Skema **6 tabel** sudah benar dan sesuai implementasi (`backend/db.py`).
**Perubahan wajib:** ganti nama **Tabel 3.31 "Model_Status" → "Model_Log"**
(nama tabel asli di sistem = `model_log`; `model_status` adalah tabel sisa skema
lama yang sudah dihapus).

### Ganti paragraf penutup 3.3.2 (pengisian data — NYATA)
> Basis data diisi dari hasil praproses dataset. Tabel `users` memuat **872 baris**
> (1 admin + **871 pelanggan**), `menu_items` memuat **141 item menu**, `orders`
> memuat **1.211 transaksi**, dan `order_details` memuat **4.908 baris interaksi**
> sebagai umpan balik implisit. Tabel `model_log` menyimpan satu baris status model
> final dengan **HR@10 = 0,3500** dan **NDCG@10 = 0,1822**.

### Tabel 3.31 — Model_Log (ganti judul dari "Model_Status")
| Nama Field | Tipe Data | Keterangan |
|---|---|---|
| id | int(11) | Primary Key |
| status | enum('training','ready','error') | Status proses model |
| model_path | varchar(255) | Lokasi file model |
| hr_at_10 | float | Nilai Hit Ratio@10 |
| ndcg_at_10 | float | Nilai NDCG@10 |
| trained_at | datetime | Waktu pelatihan selesai |
| error_log | text | Catatan error (jika ada) |
| created_at | datetime | Waktu log dibuat |

*(Tabel 3.26–3.30 tidak berubah — sudah sesuai.)*

---

# BAGIAN 3 — BAB 4 HASIL DAN PEMBAHASAN

## 4.1.2 Hasil Preprocessing Data

### Tabel 4.1 — Statistik Dataset Setelah Pembersihan
| Keterangan | Nilai |
|---|---|
| Baris item valid dari file Excel | 4.908 |
| Transaksi unik (orders) | 1.211 |
| Pelanggan unik (mentah) | 871 |
| Item menu unik (kode produk) | 141 |
| Interaksi biner unik (pasangan pelanggan–item) | 4.707 |

### Tabel 4.2 — Label Encoding Pengguna (5 pertama, NYATA)
| Indeks | Nama Pelanggan |
|---|---|
| 0 | Acai |
| 1 | Acang |
| 2 | Acen |
| 3 | Acin |
| 4 | Acu |

### Tabel 4.3 — Label Encoding Item (5 pertama, NYATA)
| Indeks | item_id | Nama Menu |
|---|---|---|
| 0 | A00A | AMERICANO SAKKA / LARGE HOT |
| 1 | A00B | LYCHEE AMERICANO / LARGE |
| 2 | A00C | COCONUT AMERICANO / LARGE |
| 3 | A00D | HONEY AMERICANO / REGULAR |
| 4 | A00E | LEMON AMERICANO / LARGE |

### Tabel 4.4 — Representasi Implicit Feedback (Pengguna 0 = Acai, NYATA)
| User Index | Item Index | item_id | Nama Menu | Label |
|---|---|---|---|---|
| 0 | 57 | A08A | PURE TEA / COLD REGULAR | 1 |
| 0 | 58 | A08B | TEA MANIS / COLD LARGE | 1 |
| 0 | 97 | C03B | NASI GORENG KAMPUNG | 1 |
| 0 | 111 | C05D | MIE SOP SAKKA | 1 |
| 0 | 127 | C10B | CHICKEN CHEESE RICEBOWL | 1 |
| 0 | 0 | A00A | AMERICANO SAKKA / LARGE HOT | 0 |

### Tabel 4.5 — Negative Sampling 4:1 (Pengguna 0, NYATA, seed 42)
| No | User Index | Item Index | item_id | Nama Menu | Label | Jenis |
|---|---|---|---|---|---|---|
| 1 | 0 | 57 | A08A | PURE TEA / COLD REGULAR | 1 | Positif |
| 2 | 0 | 49 | A06C | AVOCADO JUICE | 0 | Negatif |
| 3 | 0 | 50 | A06D | TIMUN JUICE | 0 | Negatif |
| 4 | 0 | 90 | C01M | RISOL SAKKA | 0 | Negatif |
| 5 | 0 | 26 | A02G | COCONUT PANDAN LATTE COLD | 0 | Negatif |

### Tabel 4.6 — Leave-One-Out Split (3 pengguna NYATA)
| User Index | Total Interaksi | Data Latih | Data Uji (Item Terakhir) |
|---|---|---|---|
| 0 | 5 | 4 interaksi | C10B — CHICKEN CHEESE RICEBOWL |
| 1 | 5 | 4 interaksi | C10C — CHICKEN SPICY RICEBOWL |
| 2 | 7 | 6 interaksi | A08B — TEA MANIS / COLD LARGE |

### Tabel 4.7 — Statistik Akhir Dataset Setelah Praproses
| Keterangan | Nilai |
|---|---|
| Total pelanggan unik (mentah) | 871 |
| Pelanggan dibuang (< 2 interaksi) | 51 |
| Total pengguna dipakai | 820 |
| Total item berinteraksi | 140 |
| Total interaksi positif unik | 4.707 |
| Rata-rata interaksi per pengguna | 5,74 |
| Data latih (train positif) | 3.887 |
| Data uji (test set, LOO) | 820 pengguna |
| Total sampel per epoch (positif + negatif) | 19.435 |
| Kandidat evaluasi per pengguna | 100 (1 positif + 99 negatif) |
| Strategi pembagian | Leave-One-Out |

## 4.1.3 Hasil Pelatihan dan Pengujian Model

### Tabel 4.8 — Hasil Grid Search NCF (NYATA)
| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | 1 | 0,3524 | 0,1835 |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | 3 | 0,3488 | 0,1824 |
| **C** | **32** | **[64, 32]** | **0,2** | **0,0005** | **5** | **0,3500** | **0,1822** |

### Tabel 4.9 — Hyperparameter Konfigurasi C
| Parameter | Nilai |
|---|---|
| Dimensi Embedding | 32 |
| Lapisan MLP | [64, 32] |
| Dropout | 0,2 |
| Learning Rate | 0,0005 |
| Weight Decay | 1 × 10⁻⁵ |
| Batch Size | 256 |
| Jumlah Epoch Maksimum | 50 |
| Negative Sampling (per positif) | 4 |
| Early Stopping Patience | 5 |
| Optimizer | Adam |
| Loss Function | Binary Cross-Entropy (BCE) |

### Tabel 4.10 — Perkembangan Pelatihan per Epoch — Konfigurasi C (NYATA)
| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan |
|---|---|---|---|---|
| 1 | 0,6688 | 0,3476 | 0,1797 | Model terbaik tersimpan |
| 2 | 0,5525 | 0,3451 | 0,1828 | Tidak ada peningkatan (1/5) |
| 3 | 0,4599 | 0,3451 | 0,1800 | Tidak ada peningkatan (2/5) |
| 4 | 0,4432 | 0,3415 | 0,1780 | Tidak ada peningkatan (3/5) |
| 5 | 0,4363 | 0,3500 | 0,1822 | **Model terbaik tersimpan** |
| 6 | 0,4348 | 0,3402 | 0,1800 | Tidak ada peningkatan (1/5) |
| 7 | 0,4353 | 0,3500 | 0,1828 | Tidak ada peningkatan (2/5) |
| 8 | 0,4340 | 0,3415 | 0,1805 | Tidak ada peningkatan (3/5) |
| 9 | 0,4330 | 0,3415 | 0,1799 | Tidak ada peningkatan (4/5) |
| 10 | 0,4330 | 0,3439 | 0,1798 | Early stop terpenuhi (5/5) |

### Tabel 4.11 — Informasi Model Final (NYATA)
| Informasi | Nilai |
|---|---|
| Path file model | models/ncf_config_C.pth |
| Epoch terbaik | 5 |
| Training loss epoch terbaik | 0,4363 |
| Total epoch dijalankan | 10 |
| Total parameter model | 32.833 |
| HR@10 (data uji) | 0,3500 |
| NDCG@10 (data uji) | 0,1822 |

## 4.1.4 Hasil Inferensi Rekomendasi Menu

### Paragraf pembuka (ganti — pengguna NYATA)
> Sebagai pembuktian fungsionalitas, dilakukan inferensi terhadap pelanggan
> **Jenny Sanjaya** (indeks 382), pelanggan paling aktif dengan **28 interaksi**
> yang mencakup kategori kopi, teh, jus, dan makanan berat. Sistem menyaring menu
> yang sudah pernah dipesan, lalu menghitung skor sigmoid bagi menu yang belum
> dicoba. Hasil Top-10 disajikan pada Tabel 4.12.

### Tabel 4.12 — Top-10 Rekomendasi (Jenny Sanjaya, skor NYATA)
| Peringkat | item_id | Nama Menu | Kategori | Skor Sigmoid |
|---|---|---|---|---|
| 1 | A00A | Americano Sakka | Kopi & Espresso | 0,5413 |
| 2 | C04B | Nasi Ayam Penyet Cabe Ijo | Nasi Lauk | 0,5090 |
| 3 | A01D | Sanger Sakka | Kopi & Espresso | 0,5043 |
| 4 | C03C | Nasi Goreng Seafood | Nasi Goreng | 0,4808 |
| 5 | A08C | Lemon Tea | Minuman | 0,4363 |
| 6 | A08B | Tea Manis | Minuman | 0,3997 |
| 7 | A06C | Avocado Juice | Juice | 0,3954 |
| 8 | C04G | Nasi Capcay Seafood | Nasi Lauk | 0,3786 |
| 9 | C08D | Grilled Chicken Mushroom Steak | Chicken Steak | 0,3521 |
| 10 | C01O | Snack Platter | Gorengan & Snack | 0,3247 |

## 4.2 Pembahasan (ganti angka)

### 4.2.2 Analisis HR dan NDCG
> Model final menghasilkan **HR@10 = 0,3500** dan **NDCG@10 = 0,1822** dengan
> strategi *Leave-One-Out* (1 *ground truth* : 99 negatif). HR@10 = 0,3500 berarti
> dari 100 pengguna uji, model menempatkan menu yang benar-benar dipesan ke dalam
> Top-10 pada sekitar **35 pengguna** — jauh di atas tebakan acak (~10%). NDCG@10 =
> 0,1822 menunjukkan kualitas urutan; nilai ini wajar pada *implicit feedback*
> kuliner karena pelanggan kerap memesan beberapa menu sekaligus.

### 4.2.3 Analisis Kualitas Rekomendasi
> Inferensi pada Jenny Sanjaya memperlihatkan model menggabungkan menu kopi,
> makanan berat, dan minuman dengan probabilitas 0,32–0,54, membuktikan NCF
> menangkap korelasi silang antar kategori, bukan sekadar mengulang kategori yang
> sudah dikenal pelanggan.

---

# BAGIAN 4 — CHECKLIST PERUBAHAN DI WORD

**Bab 3.2 (Analisis Proses):**
- [ ] Dimensi: **871 / 141 / 4.908** (hapus 207 & 1.211-pengguna).
- [ ] Tabel 3.1 (nyata), 3.2–3.3 (forward-fill nyata), 3.4–3.6 (encoding nyata Acai),
      3.7–3.10 (skor & BCE nyata), 3.11–3.15 (Budi Santoso, skor nyata 42–54%).
- [ ] **Hapus "207/208 Menu" → 141**; "Ke-204" → **Ke-133**; skor **98,9% → 42–54%**.

**Bab 3.3.2 (Basis Data):**
- [ ] **Judul Tabel 3.31: "Model_Status" → "Model_Log"**.
- [ ] Paragraf pengisian data: 872/871/141/1.211/4.908; HR 0,3500.

**Bab 4:**
- [ ] Tabel 4.1–4.7, 4.8–4.11, 4.12 → ganti dengan tabel di atas.
- [ ] Total parameter **47.521 → 32.833**; HR/NDCG **0,3670/0,1965 → 0,3500/0,1822**.
- [ ] Inferensi: ID 2424 → **Jenny Sanjaya (indeks 382)**.
- [ ] Narasi 4.1.5: total pengguna **872**, menu **141**, interaksi **4.908**.
- [ ] Gambar 4.1 (kurva), 4.2 (riwayat Jenny), 4.5–4.13 (screenshot ulang).
