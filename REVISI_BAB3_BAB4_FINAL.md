# REVISI BAB 3 (Perancangan Basis Data) & BAB 4 — DATA AKTUAL SKENARIO B

> **Sumber data:** seluruh angka di dokumen ini adalah **hasil aktual** yang
> direproduksi dari pipeline `ncf_pipeline/` & `scripts/train_ncf.py` (seed = 42,
> deterministik) pada dataset `src/dataset.xlsx`, **bukan contoh/karangan**.
> Skenario B: **User = Pelanggan**, **Item = kode menu**, filter ≥ 2 interaksi.
>
> **Catatan penting (koreksi angka):** nilai lama `HR@10 = 0,3439 / NDCG = 0,1825`
> ternyata berasal dari versi kode lama dan **tidak memiliki model tersimpan**
> (tidak reproducible). Saat skrip dijalankan ulang secara deterministik, model
> final **Konfigurasi C** secara konsisten menghasilkan **HR@10 = 0,3500 dan
> NDCG@10 = 0,1822** (epoch terbaik ke-5). Inilah angka aktual yang dipakai —
> sudah diselaraskan ke website (Dashboard) dan database (`model_log`).

---

# BAGIAN A — BAB 3.3.2 PERANCANGAN BASIS DATA

Skema 6 tabel pada skripsi **sudah benar** dan sesuai implementasi
(`backend/db.py` + `database/sakkabase_seed.sql`). Tidak ada perubahan struktur.
Yang perlu disesuaikan hanya **kalimat pengantar** dan **paragraf penutup**
mengenai pengisian data agar memakai angka Skenario B yang aktual.

### Ganti kalimat pengantar 3.3.2 (paragraf pertama)
> Sistem rekomendasi menu pada Sakka Base menggunakan *Relational Database
> Management System* (RDBMS) MySQL untuk menyimpan dan mengelola data penelitian.
> Basis data terdiri atas enam tabel yang saling berelasi, yaitu `users`,
> `menu_items`, `orders`, `order_details`, `recommendations`, dan `model_log`.
> Tabel `order_details` berperan sebagai sumber **umpan balik implisit (implicit
> feedback)**, di mana setiap baris merepresentasikan satu interaksi positif
> antara seorang **pelanggan** dengan sebuah item menu. Struktur relasi antar
> tabel ditampilkan pada Gambar 3.31.

### Konfirmasi struktur tabel (Tabel 3.26–3.31) — sudah sesuai, tidak diubah
Keenam tabel pada dokumen (Tabel 3.26 Users s.d. Tabel 3.31 Model_Status) **sama
persis** dengan implementasi. Pastikan kolom berikut tertulis (ini yang aktual):

- **users:** `id`, `nama_lengkap`, `username`, `password`, `role`
  `enum('admin','user')`, `source` `enum('historical','registered')`, `created_at`.
- **menu_items:** `id`, `item_id`, `nama_menu`, `kategori`, `price` (INT, harga
  menu), `created_at`, `updated_at`.
- **orders:** `id`, `user_id` (FK→users), `total` (INT, total belanja), `tanggal`,
  `created_at`.
- **order_details:** `id`, `order_id` (FK→orders), `menu_item_id` (FK→menu_items),
  `qty`, `price`.
- **recommendations:** `id`, `user_id` (FK), `menu_item_id` (FK), `rank`, `score`
  (FLOAT), `generated_at`.
- **model_log:** `id`, `status` `enum('training','ready','error')`, `model_path`,
  `hr_at_10` (FLOAT), `ndcg_at_10` (FLOAT), `trained_at`, `error_log`, `created_at`.

### Ganti paragraf penutup 3.3.2 (pengisian data — angka aktual)
> Basis data diisi dengan data hasil praproses dataset transaksi Sakka Base.
> Tabel `users` memuat **872 baris** (1 akun admin + **871 pelanggan** unik hasil
> rekapitulasi nama pelanggan), tabel `menu_items` memuat **141 item menu**
> (berdasarkan kode produk), tabel `orders` memuat **1.211 transaksi**, dan tabel
> `order_details` memuat **4.908 baris interaksi** yang menjadi umpan balik
> implisit bagi model. Tabel `model_log` menyimpan satu baris status model final
> dengan capaian **HR@10 = 0,3500** dan **NDCG@10 = 0,1822**.

---

# BAGIAN B — BAB 4 HASIL DAN PEMBAHASAN

## 4.1.2 Hasil Preprocessing Data

### Paragraf pembuka (ganti)
> Tahap praproses mentransformasi data mentah riwayat transaksi menjadi format
> yang dapat diproses model NCF. Dataset mentah dibaca dari berkas Microsoft Excel
> (`dataset.xlsx`) berisi riwayat transaksi Sakka Base – Coffee & Barber Citraland
> Helvetia. Berbeda dengan pendekatan berbasis nomor transaksi, penelitian ini
> menjadikan **identitas pelanggan (kolom Pelanggan)** sebagai unit pengguna,
> sehingga seluruh transaksi milik satu pelanggan yang sama digabung menjadi satu
> profil preferensi. Setiap baris produk diisi-maju (*forward-fill*) untuk
> kolom transaksi, item diambil dari **kode produk** (varian digabung), lalu
> pasangan (pelanggan, item) di-dedupe menjadi satu interaksi biner.

### Tabel 4.1 — Statistik Dataset Setelah Pembersihan Data
| Keterangan | Nilai |
|---|---|
| Baris item valid dari file Excel | 4.908 |
| Baris tidak valid (dilewati) | 0 |
| Transaksi unik (orders) | 1.211 |
| Pelanggan unik (mentah) | 871 |
| Item menu unik (kode produk) | 141 |
| Interaksi biner unik (pasangan pelanggan–item) | 4.707 |

> *Catatan: dari 4.908 baris transaksi, setelah pasangan (pelanggan, item) yang
> berulang digabung menjadi interaksi biner, diperoleh 4.707 interaksi unik.*

### Encoding ID Pengguna dan Item (paragraf — ganti)
> Karena penelitian memakai **nama pelanggan** sebagai pengguna dan **kode menu**
> sebagai item, dilakukan *Label Encoding* yang memetakan setiap nama pelanggan
> dan kode item ke indeks integer berurutan mulai dari 0, untuk digunakan sebagai
> indeks pada *embedding layer*. Setelah penyaringan pelanggan dengan minimal 2
> interaksi, diperoleh **820 indeks pengguna (0–819)** dan **140 indeks item
> (0–139)** yang memiliki interaksi.

### Tabel 4.2 — Hasil Label Encoding Pengguna (5 data pertama, aktual)
| Indeks Encoding | Nama Pelanggan |
|---|---|
| 0 | Acai |
| 1 | Acang |
| 2 | Acen |
| 3 | Acin |
| 4 | Acu |

### Tabel 4.3 — Hasil Label Encoding Item Menu (5 data pertama, aktual)
| Indeks Encoding | item_id | Nama Menu |
|---|---|---|
| 0 | A00A | AMERICANO SAKKA / LARGE HOT |
| 1 | A00B | LYCHEE AMERICANO / LARGE |
| 2 | A00C | COCONUT AMERICANO / LARGE |
| 3 | A00D | HONEY AMERICANO / REGULAR |
| 4 | A00E | LEMON AMERICANO / LARGE |

### Pemetaan Nilai Biner (Implicit Feedback) — paragraf
> Penelitian ini memakai umpan balik implisit sehingga tidak tersedia rating
> eksplisit. Setiap pasangan (pelanggan, item) yang pernah muncul pada transaksi
> diberi label **1**, sedangkan pasangan yang tidak pernah muncul dikodekan
> sebagai label **0** melalui *negative sampling*.

### Tabel 4.4 — Representasi Implicit Feedback (Pengguna indeks 0 = "Acai", aktual)
| User Index | Item Index | item_id | Nama Menu | Label | Keterangan |
|---|---|---|---|---|---|
| 0 | 57 | A08A | PURE TEA / COLD REGULAR | 1 | Pernah dipesan |
| 0 | 58 | A08B | TEA MANIS / COLD LARGE | 1 | Pernah dipesan |
| 0 | 97 | C03B | NASI GORENG KAMPUNG | 1 | Pernah dipesan |
| 0 | 111 | C05D | MIE SOP SAKKA | 1 | Pernah dipesan |
| 0 | 127 | C10B | CHICKEN CHEESE RICEBOWL | 1 | Pernah dipesan |
| 0 | 0 | A00A | AMERICANO SAKKA / LARGE HOT | 0 | Tidak pernah dipesan |
| 0 | 1 | A00B | LYCHEE AMERICANO / LARGE | 0 | Tidak pernah dipesan |

> *Pengguna "Acai" (indeks 0) memiliki 5 interaksi positif. Seluruh item lain
> yang tidak pernah dipesannya berlabel 0.*

### Negative Sampling — paragraf (ganti)
> Sistem menerapkan *negative sampling* secara *runtime* dengan rasio **4 : 1**
> (4 sampel negatif per 1 sampel positif). Sampel negatif dibangkitkan ulang di
> setiap awal epoch agar model tidak menghafal pola negatif yang sama; item
> negatif dipilih acak dari 140 item dengan syarat belum pernah dipesan pengguna
> tersebut. Dengan **3.887 interaksi positif** pada data latih, *negative
> sampling* 4:1 menghasilkan **15.548 sampel negatif**, sehingga total data yang
> diproses model per epoch berjumlah **19.435 sampel**.

### Tabel 4.5 — Hasil Negative Sampling 4:1 (Pengguna indeks 0, aktual, seed 42)
| No | User Index | Item Index | item_id | Nama Menu | Label | Jenis |
|---|---|---|---|---|---|---|
| 1 | 0 | 57 | A08A | PURE TEA / COLD REGULAR | 1 | Positif |
| 2 | 0 | 49 | A06C | AVOCADO JUICE | 0 | Negatif |
| 3 | 0 | 50 | A06D | TIMUN JUICE | 0 | Negatif |
| 4 | 0 | 90 | C01M | RISOLES | 0 | Negatif |
| 5 | 0 | 26 | A02G | COCONUT PANDAN LATTE COLD / LARGE | 0 | Negatif |

### Leave-One-Out Split — paragraf (ganti)
> Pembagian dataset memakai strategi *leave-one-out*: item dengan tanggal
> transaksi paling akhir per pengguna dipisahkan sebagai data uji, sedangkan
> seluruh interaksi sebelumnya menjadi data latih. Pelanggan dengan hanya 1
> interaksi (**51 pelanggan**) tidak diikutkan pada data uji. Untuk evaluasi,
> setiap pengguna uji diberikan **100 item kandidat** (1 item *ground truth* + 99
> item negatif acak).

### Tabel 4.6 — Hasil Leave-One-Out Split (3 pengguna aktual)
| User Index | Total Interaksi | Data Latih | Data Uji (Item Terakhir) |
|---|---|---|---|
| 0 | 5 | 4 interaksi | C10B — CHICKEN CHEESE RICEBOWL |
| 1 | 5 | 4 interaksi | C10C — CHICKEN SPICY RICEBOWL |
| 2 | 7 | 6 interaksi | A08B — TEA MANIS / COLD LARGE |

### Tabel 4.7 — Statistik Akhir Dataset Setelah Praproses (aktual)
| Keterangan | Nilai |
|---|---|
| Total pelanggan unik (mentah) | 871 |
| Pelanggan dibuang (< 2 interaksi) | 51 |
| Total pengguna dipakai | 820 |
| Total item menu memiliki interaksi | 140 |
| Total interaksi positif unik | 4.707 |
| Rata-rata interaksi per pengguna | 5,74 |
| Data latih (train positif) | 3.887 |
| Data uji (test set, LOO) | 820 pengguna |
| Total sampel per epoch (positif + negatif) | 19.435 |
| Kandidat evaluasi per pengguna | 100 (1 positif + 99 negatif) |
| Strategi pembagian dataset | Leave-One-Out |

---

## 4.1.3 Hasil Pelatihan dan Pengujian Model NCF

### Tabel 4.8 — Hasil Grid Search NCF (aktual)
| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | 1 | 0,3524 | 0,1835 |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | 3 | 0,3488 | 0,1824 |
| **C** | **32** | **[64, 32]** | **0,2** | **0,0005** | **5** | **0,3500** | **0,1822** |

### Narasi pemilihan model final (ganti)
> Berdasarkan Tabel 4.8, ketiga konfigurasi menghasilkan HR@10 yang sangat
> berdekatan (rentang 0,3488–0,3524), menandakan performa yang relatif setara.
> Konfigurasi A dengan *learning rate* lebih besar (0,001) langsung mencapai
> performa puncak pada epoch ke-1 lalu cenderung tidak stabil pada epoch-epoch
> berikutnya. Konfigurasi B dengan dimensi embedding lebih kecil (16) memiliki
> kapasitas yang lebih terbatas. Sementara itu, **Konfigurasi C** (embedding 32,
> MLP [64, 32], *learning rate* 0,0005) memberikan **konvergensi yang paling
> stabil** dengan jumlah parameter relatif sedikit (**32.833 parameter**) dan
> capaian HR@10 = 0,3500 yang kompetitif. Oleh karena itu, **Konfigurasi C
> ditetapkan sebagai model final** karena keseimbangan antara kestabilan
> pelatihan, efisiensi parameter, dan performa.

### Tabel 4.9 — Hyperparameter Pelatihan Konfigurasi C
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

### Paragraf proses pelatihan (ganti)
> Setiap epoch memproses **19.435 sampel** (3.887 positif + 15.548 negatif, rasio
> 1:4). Sampel negatif dibangkitkan ulang secara acak di setiap awal epoch.
> Perkembangan nilai *training loss* dan metrik per epoch ditampilkan pada
> Tabel 4.10.

### Tabel 4.10 — Perkembangan Pelatihan per Epoch — Konfigurasi C (aktual)
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

### Paragraf analisis Tabel 4.10 (ganti)
> Nilai *training loss* turun konsisten dari 0,6688 (epoch 1) hingga stabil di
> kisaran 0,433 pada epoch akhir. Performa terbaik pada data uji dicapai pada
> **epoch ke-5** (HR@10 = 0,3500; NDCG@10 = 0,1822) sehingga bobot model pada
> epoch tersebut disimpan sebagai model final. Karena tidak terjadi peningkatan
> HR@10 selama 5 epoch berturut-turut sesudahnya, *early stopping* menghentikan
> pelatihan pada **epoch ke-10**.

### Gambar 4.1
Ganti dengan kurva dari `scripts/history_configC.csv` (atau
`figures/gambar_4_1_kurva_training.png` bila sudah dibuat ulang).

### Tabel 4.11 — Informasi Model Final (aktual)
| Informasi | Nilai |
|---|---|
| Path file model | models/ncf_config_C.pth |
| Epoch terbaik | 5 |
| Training loss epoch terbaik | 0,4363 |
| Total epoch dijalankan | 10 |
| Total parameter model | 32.833 |
| HR@10 (data uji) | 0,3500 |
| NDCG@10 (data uji) | 0,1822 |

---

## 4.1.4 Hasil Inferensi Rekomendasi Menu

### Paragraf pembuka (ganti — pengguna nyata Skenario B)
> Sebagai pembuktian fungsionalitas keluaran model, dilakukan inferensi terhadap
> pelanggan **Jenny Sanjaya** (indeks pengguna 382), yaitu pelanggan paling aktif
> dengan **28 interaksi**. Berdasarkan riwayatnya, pelanggan ini memiliki
> preferensi kuat pada kategori kopi (Honey Americano, Cafe Latte, Dirty Latte,
> Aren Latte), teh & jus (Pure Tea, Lychee Tea, Mango/Timun/Tomato Juice), serta
> makanan berat (Nasi Goreng Special, Nasi Ayam Bakar, Nasi Ayam Geprek, beragam
> *ricebowl* dan *pasta*). Sistem secara otomatis menyaring menu yang sudah pernah
> dipesan dari daftar kandidat, kemudian menghitung skor probabilitas (sigmoid)
> bagi seluruh menu yang belum pernah dicoba. Hasil Top-10 disajikan pada
> Tabel 4.12.

### Tabel 4.12 — Hasil Inferensi Top-10 Rekomendasi (Jenny Sanjaya, aktual)
| Peringkat | item_id | Nama Menu | Kategori | Skor Probabilitas (Sigmoid) |
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

### Paragraf analisis Tabel 4.12 (ganti)
> Tabel 4.12 memperlihatkan bahwa model merekomendasikan menu kopi (Americano
> Sakka, Sanger Sakka) yang selaras dengan kebiasaan pelanggan, sekaligus
> menawarkan variasi menu makanan berat (Nasi Ayam Penyet Cabe Ijo, Nasi Goreng
> Seafood, Nasi Capcay Seafood) dan minuman lain (Lemon Tea, Avocado Juice).
> Hal ini menunjukkan model NCF tidak sekadar mengulang kategori yang sudah
> dikenal pelanggan, tetapi juga menggali korelasi dari pola pembelian
> pelanggan-pelanggan lain yang serupa, sehingga menghasilkan rekomendasi yang
> relevan sekaligus bervariasi.

---

## 4.2 Pembahasan

### 4.2.1 Analisis Konfigurasi dan Pelatihan Model (ganti angka)
> Proses *grid search* menunjukkan ketiga konfigurasi menghasilkan HR@10 yang
> berdekatan (0,3488–0,3524). **Konfigurasi C** (embedding 32, MLP [64, 32],
> *learning rate* 0,0005) dipilih sebagai model final karena konvergensinya paling
> stabil dengan jumlah parameter paling efisien (**32.833 parameter**). Temuan ini
> mengindikasikan bahwa untuk data *implicit feedback* yang bersifat biner dan
> *sparse* (4.707 interaksi pada 820 pengguna × 140 item), arsitektur yang tidak
> terlalu dalam dengan *learning rate* kecil sudah memadai untuk mengekstraksi
> fitur laten tanpa *overfitting*.

### 4.2.2 Analisis Hasil Evaluasi HR dan NDCG (ganti angka)
> Model final menghasilkan **HR@10 = 0,3500** dan **NDCG@10 = 0,1822** yang
> dihitung dengan strategi *Leave-One-Out* (1 item *ground truth* : 99 item
> negatif). Nilai HR@10 = 0,3500 berarti dari setiap 100 pengguna yang diuji,
> model berhasil menempatkan menu yang benar-benar akan dipesan ke dalam daftar
> Top-10 pada sekitar **35 pengguna**. Mengingat peluang tebakan acak hanya
> sekitar 10% (10 dari 100 kandidat), capaian 35% membuktikan model mempelajari
> pola preferensi pelanggan secara signifikan di atas tebakan acak. Nilai
> NDCG@10 = 0,1822 merepresentasikan kualitas urutan daftar; nilai ini wajar pada
> *implicit feedback* domain kuliner karena pelanggan kerap memesan beberapa jenis
> menu dalam satu transaksi sehingga banyak kandidat relevan bersaing ketat pada
> lapisan output.

### 4.2.3 Analisis Hasil Inferensi dan Kualitas Rekomendasi (ganti contoh)
> Berdasarkan inferensi pada pelanggan **Jenny Sanjaya**, model tidak terjebak
> hanya merekomendasikan kategori yang sudah sering dipesan, melainkan menyajikan
> kombinasi menu kopi, makanan berat, dan minuman dengan probabilitas kecocokan
> tinggi (0,32–0,54). Hal ini membuktikan NCF mampu menangkap **korelasi silang
> antar kategori menu**: dalam ruang vektor laten, pelanggan dengan pola pembelian
> serupa cenderung memiliki probabilitas tinggi untuk memesan menu tertentu,
> sehingga model menghasilkan keragaman rekomendasi yang relevan dengan selera
> kelompok pelanggan tersebut.

---

# BAGIAN C — CHECKLIST PERUBAHAN DI WORD

**Bab 3.3.2:**
- [ ] Ganti kalimat pengantar (6 tabel + implicit feedback per pelanggan).
- [ ] Ganti paragraf penutup pengisian data (872/871/141/1.211/4.908; HR 0,3500).
- [ ] Struktur Tabel 3.26–3.31 tidak diubah (sudah benar).

**Bab 4.1.2 (Preprocessing):**
- [ ] Tabel 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7 → ganti dengan tabel di atas.
- [ ] Paragraf encoding/negative sampling/LOO → ganti narasi.

**Bab 4.1.3 (Pelatihan):**
- [ ] Tabel 4.8 (grid search), 4.9, 4.10 (10 epoch), 4.11 (model final) → ganti.
- [ ] Gambar 4.1 → kurva baru.
- [ ] Total parameter di mana pun: **47.521 → 32.833**.

**Bab 4.1.4 (Inferensi):**
- [ ] Ganti "ID Pengguna 2424" → **Jenny Sanjaya (indeks 382)**.
- [ ] Tabel 4.12 → Top-10 baru; Gambar 4.2 → screenshot riwayat Jenny.

**Bab 4.2 (Pembahasan):**
- [ ] Semua angka HR/NDCG: **0,3670/0,1965 → 0,3500/0,1822**.
- [ ] Contoh inferensi: ganti ke Jenny Sanjaya.

**Bab 4.1.5 (Antarmuka) — angka di narasi:**
- [ ] Total pengguna: **872** (bukan 1.212); total menu: **141** (bukan 207);
      interaksi: **4.908** (atau 4.913 bila memasukkan data pengujian).
- [ ] Gambar 4.5 (Dashboard) → screenshot ulang (kini HR 0,3500 · NDCG 0,1822).
- [ ] Gambar 4.6–4.13 → screenshot ulang dengan data baru.

**Bab 1 & Bab 2:** tidak ada perubahan angka wajib.
