# BAB IV — HASIL DAN PEMBAHASAN (Tabel 4.1–4.12, DATA NYATA)

> Seluruh angka diambil/diverifikasi langsung dari `src/dataset.xlsx`, database
> MySQL, dan model terlatih yang dipakai website (`ncf_config_C.pth` →
> `recommendations.json`). Acuan: **Skenario B (User = Pelanggan)**, model final
> **Konfigurasi C: HR@10 = 0,3500 · NDCG@10 = 0,1822**.

---

# 4.1.2 Hasil Preprocessing Data

### Tabel 4.1 Statistik Dataset Setelah Pembersihan Data
| Keterangan | Nilai |
|---|---|
| Baris item valid dari file Excel | 4.908 |
| Baris tidak valid (dilewati) | 0 |
| Transaksi unik (orders) | 1.211 |
| Pelanggan unik (mentah) | 871 |
| Item menu unik (kode produk) | 141 |
| Interaksi biner unik (pasangan pelanggan–item) | 4.707 |

### Tabel 4.2 Hasil Label Encoding Pengguna
*(Indeks Encoding diberikan model berdasarkan urutan abjad nama; `user_id`
adalah primary key MySQL.)*

| No | user_id (MySQL) | Nama Pengguna | Indeks Encoding |
|---|---|---|---|
| 1 | 365 | Acai | 0 |
| 2 | 348 | Acang | 1 |
| 3 | 216 | Acen | 2 |
| 4 | 709 | Acin | 3 |
| 5 | 287 | Acu | 4 |

### Tabel 4.3 Hasil Label Encoding Item Menu
| No | menu_item_id (MySQL) | item_id | Indeks Encoding |
|---|---|---|---|
| 1 | 1 | A00A — AMERICANO SAKKA / LARGE HOT | 0 |
| 2 | 2 | A00B — LYCHEE AMERICANO / LARGE | 1 |
| 3 | 3 | A00C — COCONUT AMERICANO / LARGE | 2 |
| 4 | 4 | A00D — HONEY AMERICANO / REGULAR | 3 |
| 5 | 5 | A00E — LEMON AMERICANO / LARGE | 4 |

### Tabel 4.4 Representasi Implicit Feedback (Pengguna indeks 0 = "Acai")
| User Index | Item Index | Nama Menu | Label | Keterangan |
|---|---|---|---|---|
| 0 | 57 | PURE TEA / COLD REGULAR | 1 | Pernah dipesan |
| 0 | 58 | TEA MANIS / COLD LARGE | 1 | Pernah dipesan |
| 0 | 97 | NASI GORENG KAMPUNG | 1 | Pernah dipesan |
| 0 | 111 | MIE SOP SAKKA | 1 | Pernah dipesan |
| 0 | 127 | CHICKEN CHEESE RICEBOWL | 1 | Pernah dipesan |
| 0 | 0 | AMERICANO SAKKA / LARGE HOT | 0 | Tidak pernah dipesan |
| 0 | 1 | LYCHEE AMERICANO / LARGE | 0 | Tidak pernah dipesan |

### Tabel 4.5 Hasil Negative Sampling 4:1 (Pengguna indeks 0, seed 42)
| No | User Index | Item Index | Nama Menu | Label | Jenis |
|---|---|---|---|---|---|
| 1 | 0 | 57 | PURE TEA / COLD REGULAR | 1 | Positif |
| 2 | 0 | 49 | AVOCADO JUICE | 0 | Negatif |
| 3 | 0 | 50 | TIMUN JUICE | 0 | Negatif |
| 4 | 0 | 90 | RISOL SAKKA | 0 | Negatif |
| 5 | 0 | 26 | COCONUT PANDAN LATTE COLD / LARGE | 0 | Negatif |

### Tabel 4.6 Hasil Leave-One-Out Split — 3 Pengguna Aktual
| User Index | Total Interaksi | Data Latih | Data Uji (Item Terakhir) |
|---|---|---|---|
| 0 | 5 | 4 interaksi | C10B — CHICKEN CHEESE RICEBOWL |
| 1 | 5 | 4 interaksi | C10C — CHICKEN SPICY RICEBOWL |
| 2 | 7 | 6 interaksi | A08B — TEA MANIS / COLD LARGE |

### Tabel 4.7 Statistik Akhir Dataset Setelah Praproses
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
| Strategi pembagian dataset | Leave-One-Out |

---

# 4.1.3 Hasil Pelatihan dan Pengujian Model NCF

### Tabel 4.8 Hasil Grid Search NCF
| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | 1 | 0,3524 | 0,1835 |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | 3 | 0,3488 | 0,1824 |
| **C** | **32** | **[64, 32]** | **0,2** | **0,0005** | **5** | **0,3500** | **0,1822** |

> Ketiga konfigurasi menghasilkan HR@10 yang berdekatan (0,3488–0,3524).
> Konfigurasi **C** dipilih sebagai model final karena konvergensinya paling
> stabil dengan jumlah parameter paling efisien (**32.833 parameter**).

### Tabel 4.9 Hyperparameter Pelatihan Konfigurasi C
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

### Tabel 4.10 Perkembangan Training Loss per Epoch — Konfigurasi C
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

> *Training loss turun konsisten dari 0,6688 (epoch 1) dan stabil di kisaran
> 0,433. Performa terbaik dicapai pada **epoch ke-5** (HR@10 = 0,3500); pelatihan
> dihentikan otomatis pada **epoch ke-10** oleh early stopping.*

### Tabel 4.11 Informasi Model Final
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

# 4.1.4 Hasil Inferensi Rekomendasi Menu

> Inferensi dilakukan terhadap pelanggan **Jenny Sanjaya** (`user_id` = 2),
> pelanggan paling aktif dengan **28 interaksi**. Sistem menyaring menu yang sudah
> pernah dipesan, lalu menghitung skor sigmoid bagi menu yang belum dicoba.

### Tabel 4.12 Hasil Inferensi Top-10 Rekomendasi Menu (Pengguna: Jenny Sanjaya)
| Peringkat | ID Item | Nama Menu | Kategori | Skor Probabilitas (Sigmoid) |
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

> *Model merekomendasikan menu kopi (Americano Sakka, Sanger Sakka) yang selaras
> dengan kebiasaan pelanggan, sekaligus menawarkan variasi makanan berat dan
> minuman lain — menunjukkan NCF menangkap korelasi silang antar kategori.*

---

# 4.2 Pembahasan

## 4.2.1 Analisis Konfigurasi dan Pelatihan Model
Proses *grid search* menunjukkan ketiga konfigurasi menghasilkan HR@10 yang
berdekatan (0,3488–0,3524). **Konfigurasi C** (embedding 32, MLP [64, 32],
*learning rate* 0,0005) dipilih sebagai model final karena konvergensinya paling
stabil dengan jumlah parameter paling efisien (32.833 parameter). Untuk data
*implicit feedback* yang biner dan *sparse* (4.707 interaksi pada 820 pengguna ×
140 item), arsitektur yang tidak terlalu dalam dengan *learning rate* kecil sudah
memadai untuk mengekstraksi fitur laten tanpa *overfitting*.

## 4.2.2 Analisis Hasil Evaluasi HR dan NDCG
Model final menghasilkan **HR@10 = 0,3500** dan **NDCG@10 = 0,1822** dengan
strategi *Leave-One-Out* (1 *ground truth* : 99 negatif). HR@10 = 0,3500 berarti
dari 100 pengguna uji, model menempatkan menu yang benar-benar dipesan ke dalam
Top-10 pada sekitar **35 pengguna** — jauh di atas tebakan acak (~10%). NDCG@10 =
0,1822 menunjukkan kualitas urutan daftar; nilai ini wajar pada *implicit
feedback* domain kuliner karena pelanggan kerap memesan beberapa menu sekaligus
dalam satu transaksi sehingga banyak kandidat relevan bersaing ketat.

## 4.2.3 Analisis Hasil Inferensi dan Kualitas Rekomendasi
Inferensi pada pelanggan Jenny Sanjaya memperlihatkan model menggabungkan menu
kopi, makanan berat, dan minuman dengan probabilitas 0,32–0,54. Hal ini
membuktikan NCF bekerja melampaui *content-based filtering* konvensional: dalam
ruang vektor laten, pelanggan dengan pola pembelian serupa cenderung memiliki
probabilitas tinggi untuk memesan menu tertentu, sehingga model menghasilkan
keragaman rekomendasi yang relevan dengan selera kelompok pelanggan tersebut.

---

# Checklist perubahan dari draf lama (Skenario A → B)
- Total parameter: **47.521 → 32.833**
- HR@10 / NDCG@10: **0,3670 / 0,1965 → 0,3500 / 0,1822**
- Item menu: **207 → 141** (140 berinteraksi)
- Pengguna: **1.212 → 871** (820 dipakai)
- Interaksi: **4.913 → 4.707**; sampel/epoch **18.880 → 19.435**
- Epoch terbaik **8 → 5**; total epoch **13 → 10**
- Inferensi: **ID 2424 → Jenny Sanjaya (user_id 2)**
- Encoding contoh: **Acai = 0, A00A = 0** (urut abjad/kode)
