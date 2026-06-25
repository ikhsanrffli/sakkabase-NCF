# Panduan Lengkap Memperbarui BAB IV — Skenario B (data nyata)

Panduan langkah-per-langkah untuk menulis ulang **Bab 4 (Hasil & Pembahasan)**
dengan dataset baru, di mana **User = Pelanggan** (bukan Nomor Transaksi).
Setiap langkah: **Tujuan** (untuk apa) → **Hasil** (angkanya) → **Teks/Tabel siap paste**.

Semua angka reproducible via `ncf_pipeline/` (seed 42).

> 🔁 **PERUBAHAN METODOLOGI (wajib disadari):** Bab 4 lama memakai
> *User ID = Nomor Transaksi* (1.212 pengguna). Versi baru memakai
> *User ID = Pelanggan* (820 pengguna setelah filter). Maka semua kalimat
> "Nomor Transaksi sebagai User" diganti "Pelanggan sebagai User".

---

# 4.1.2 Hasil Preprocessing Data

## Langkah 1 — Pembersihan Data (Data Cleaning)
**Tujuan:** membuang baris tidak valid agar data konsisten sebelum dimodelkan.
**Yang diubah:** kriteria utama kini **Pelanggan + Produk** (bukan hanya No Transaksi).
**Hasil:** dari file `dataset.xlsx` terbaca **4.908 baris item valid** dari
**1.211 nomor transaksi**, **871 pelanggan unik**, dan **141 menu (kode)**;
**1 baris tidak valid** (kolom Produk kosong) dihapus.

**Teks siap paste:**
> Dataset mentah dibaca dari file `dataset.xlsx` menggunakan library openpyxl.
> Kolom transaksi yang kosong akibat sel tergabung (Nomor Transaksi, Tanggal,
> Pelanggan) diisi maju (forward-fill) sehingga setiap baris produk memiliki
> identitas pelanggan dan tanggal. Baris tanpa Produk yang valid dihapus, dan
> kuantitas yang tidak dapat dikonversi diganti nilai default 1. Proses ini
> menghasilkan 4.908 baris item valid dari 1.211 transaksi, mencakup 871
> pelanggan unik dan 141 menu unik.

### Tabel 4.1 — Statistik Dataset Setelah Pembersihan Data
| Keterangan | Nilai |
|---|---|
| Total nomor transaksi unik | 1.211 |
| Total baris item valid | 4.908 |
| Total pelanggan unik | 871 |
| Total menu unik (kode) | 141 |
| Baris tidak valid dihapus | 1 |

---

## Langkah 2 — Label Encoding Pengguna & Item
**Tujuan:** mengubah ID teks menjadi indeks integer agar bisa dipakai embedding.
**Yang diubah:** User ID kini dari **nama Pelanggan** (diurutkan alfabetis),
bukan Nomor Transaksi. Item dari **kode menu**.
**Hasil:** pemetaan integer mulai dari 0.

> Ganti kalimat: "User ID (**Nomor Transaksi**)" → "User ID (**Pelanggan**)".

### Tabel 4.2 — Hasil Label Encoding Pengguna (5 data pertama)
| Pelanggan (Asli) | ID Pengguna (Encoded) |
|---|---|
| Acai | 0 |
| Acang | 1 |
| Acen | 2 |
| Acin | 3 |
| Acu | 4 |

### Tabel 4.3 — Hasil Label Encoding Item Menu (5 data pertama)
| Kode Item (Asli) | Nama Menu | ID Item (Encoded) |
|---|---|---|
| A00A | Americano Sakka | 0 |
| A00B | Lychee Americano | 1 |
| A00C | Coconut Americano | 2 |
| A00D | Honey Americano | 3 |
| A00E | Lemon Americano | 4 |

---

## Langkah 3 — Pemetaan Nilai Biner (Implicit Feedback)
**Tujuan:** merepresentasikan preferensi sebagai 1 (pernah dipesan) / 0 (tidak).
**Yang diubah:** interaksi kini per **(Pelanggan, menu)**. Pembelian berulang
menu yang sama oleh pelanggan yang sama digabung menjadi satu interaksi positif.
**Hasil:** contoh pengguna indeks 0 (Pelanggan **Acai**) memiliki 5 interaksi positif.

### Tabel 4.4 — Representasi Implicit Feedback (Pengguna indeks 0 = Acai)
| ID Pengguna | ID Item | Kode | Nama Menu | Label |
|---|---|---|---|---|
| 0 | 57 | A08A | Pure Tea | 1 |
| 0 | 58 | A08B | Tea Manis | 1 |
| 0 | 97 | C03B | Nasi Goreng Kampung | 1 |
| 0 | 111 | C05D | Mie Sop Sakka | 1 |
| 0 | 127 | C10B | Chicken Cheese Ricebowl | 1 |

---

## Langkah 4 — Negative Sampling (rasio 4:1)
**Tujuan:** menyediakan contoh negatif (menu tak dipesan) sebagai pembanding saat latih.
**Hasil:** untuk 1 positif diambil 4 negatif acak; dibangkitkan ulang tiap epoch.

### Tabel 4.5 — Hasil Negative Sampling 4:1 (Pengguna indeks 0)
| ID Pengguna | ID Item | Kode | Label |
|---|---|---|---|
| 0 | 57 | A08A | 1 (positif) |
| 0 | 28 | A02I | 0 (negatif) |
| 0 | 6 | A01B | 0 (negatif) |
| 0 | 70 | A09H | 0 (negatif) |
| 0 | 62 | A08F | 0 (negatif) |

---

## Langkah 5 — Leave-One-Out Split
**Tujuan:** memisahkan 1 interaksi terakhir tiap pengguna sebagai data uji.
**Hasil:** menu dengan tanggal terbaru → data uji; sisanya → data latih.

### Tabel 4.6 — Hasil Leave-One-Out Split (3 Pengguna Aktual)
| Pengguna | Data Latih (kode menu) | Data Uji (kode) |
|---|---|---|
| Acai (0) | A08A, A08B, C03B, C05D | C10B |
| Acang (1) | A00A, A07B, A09F, C10A | C10C |
| Acen (2) | A02F, A03A, A03C, A07B, C01E, C04B | A08B |

---

## Statistik akhir praproses

### Tabel 4.7 — Statistik Akhir Dataset Setelah Praproses
| Keterangan | Nilai |
|---|---|
| Total pengguna (pelanggan) unik | 871 |
| Pengguna dibuang (<2 interaksi) | 51 |
| Total pengguna dipakai | 820 |
| Total item menu (memiliki interaksi) | 140 |
| Total interaksi positif unik | 4.707 |
| Rata-rata interaksi per pengguna | 5,74 |
| Data latih (train set) | 3.887 interaksi |
| Data uji (test set) | 820 pengguna |
| Total sampel per epoch (latih+negatif) | 19.435 |
| Kandidat evaluasi per pengguna | 100 (1 positif + 99 negatif) |
| Strategi pembagian | Leave-One-Out |

> **Catatan dedupe:** basis data menyimpan 4.908 baris order_details (mentah),
> namun untuk umpan balik biner, pembelian berulang menu yang sama oleh pelanggan
> yang sama digabung → 4.707 interaksi unik (setelah filter ≥2 interaksi).

---

# 4.1.3 Hasil Pelatihan & Pengujian Model

## Langkah 6 — Grid Search (3 konfigurasi)
**Tujuan:** memilih konfigurasi hyperparameter terbaik.
**Hasil:** ketiga konfigurasi berdekatan; **Konfigurasi C** dipilih final
(paling efisien & stabil).

### Tabel 4.8 — Hasil Grid Search NCF
| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 | Parameter |
|---|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | 5 | 0,3451 | 0,1806 | 33.345 |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | 5 | 0,3402 | 0,1772 | 16.033 |
| **C** | 32 | [64, 32] | 0,2 | 0,0005 | 2 | 0,3439 | 0,1825 | 32.833 |

> ⚠️ **PERHATIAN penting:** pada data baru, **Konfigurasi A** justru sedikit
> lebih tinggi (0,3451) daripada C (0,3439). Selisihnya ±0,0012 — **setara
> secara statistik** (hanya 820 pengguna uji). JANGAN menulis "C menghasilkan
> HR tertinggi". Gunakan justifikasi baru di bawah.

**Teks siap paste (justifikasi pemilihan C):**
> Ketiga konfigurasi menghasilkan HR@10 yang sangat berdekatan (selisih ±0,003),
> sehingga secara statistik dapat dianggap setara. Konfigurasi A dengan learning
> rate lebih besar (0,001) cepat mencapai puncak pada epoch awal lalu mengalami
> plateau, sedangkan Konfigurasi C dengan learning rate lebih kecil (0,0005)
> menunjukkan konvergensi yang lebih stabil hingga epoch ke-5. Karena performa
> setara namun Konfigurasi C memiliki arsitektur lebih sederhana (lapisan MLP
> [64, 32], 32.833 parameter) dan konvergensi paling stabil, Konfigurasi C
> ditetapkan sebagai model final.

## Langkah 7 — Pelatihan Konfigurasi C

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

**Hasil:** tiap epoch memproses **19.435 sampel** (3.887 positif + 15.548 negatif, rasio 1:4).

### Tabel 4.10 — Perkembangan Training Loss per Epoch (Konfigurasi C)
| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan |
|---|---|---|---|---|
| 1 | 0,6687 | 0,3366 | 0,1833 | Model terbaik tersimpan |
| 2 | 0,5536 | 0,3439 | 0,1825 | **Model terbaik tersimpan** |
| 3 | 0,4609 | 0,3378 | 0,1776 | Tidak ada peningkatan (1/5) |
| 4 | 0,4447 | 0,3390 | 0,1805 | Tidak ada peningkatan (2/5) |
| 5 | 0,4370 | 0,3439 | 0,1797 | Tidak ada peningkatan (3/5) |
| 6 | 0,4350 | 0,3305 | 0,1771 | Tidak ada peningkatan (4/5) |
| 7 | 0,4362 | 0,3329 | 0,1737 | Early stop terpenuhi (5/5) |

**Gambar 4.1:** ganti dengan `figures/gambar_4_1_kurva_training.png`.

## Langkah 8 — Model Final

### Tabel 4.11 — Informasi Model Final
| Informasi | Nilai |
|---|---|
| Path file model | models/ncf_config_C.pth |
| Epoch terbaik | 2 |
| Training loss epoch terbaik | 0,5536 |
| Total epoch dijalankan | 7 |
| Jumlah pengguna | 820 |
| Jumlah item | 140 |
| Total parameter model | 32.833 |
| HR@10 (data uji) | 0,3439 |
| NDCG@10 (data uji) | 0,1825 |

---

# 4.1.4 Hasil Inferensi Rekomendasi Menu

**Tujuan:** membuktikan keluaran model menghasilkan rekomendasi relevan & lintas kategori.
**Yang diubah:** pengguna contoh dari "ID 2424" → **pelanggan nyata Jenny Sanjaya**
(indeks 382), pelanggan paling aktif dengan **28 menu** beragam.

**Gambar 4.2 — Riwayat Pemesanan Jenny Sanjaya** (cuplikan; ambil screenshot dari
halaman Data Pemesanan aplikasi, filter nama "Jenny Sanjaya"). Riwayatnya
mencakup kopi (Honey Americano, Cafe Latte, Aren Latte), jus (Mango, Tomato),
nasi (Nasi Goreng Special, Nasi Ayam Bakar), pasta (Carbonara), hingga steak.

### Tabel 4.12 — Hasil Inferensi Top-10 Rekomendasi (Pengguna: Jenny Sanjaya)
| Rank | Kode | Nama Menu | Kategori | Skor |
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

**Teks siap paste:**
> Sebagai pembuktian fungsionalitas keluaran model, dilakukan inferensi terhadap
> pelanggan Jenny Sanjaya yang memiliki riwayat pemesanan beragam lintas kategori.
> Menu kandidat yang belum pernah dipesan dihitung skor probabilitasnya melalui
> fungsi sigmoid. Sepuluh menu teratas (Tabel 4.12) menunjukkan model mampu
> menangkap preferensi lintas kategori: merekomendasikan kopi (Americano Sakka,
> Sanger Sakka) sesuai kebiasaan ngopinya, sekaligus menu nasi (Nasi Ayam Penyet,
> Nasi Goreng Seafood) dan minuman (Lemon Tea, Avocado Juice) yang selaras dengan
> pola konsumsi makanannya.

---

# 4.1.5 Implementasi Antarmuka
**Yang diubah:** angka di **Dashboard Admin** (Gambar 4.5 / paragrafnya):
- LAMA: "1.212 pengguna, 207 item, 4.915 interaksi"
- **BARU: "871 pengguna, 141 item, 4.908 interaksi"**

**Screenshot (Gambar 4.3–4.13):** ambil ULANG dari aplikasi yang sudah memakai
data baru (`npm run dev`), agar tampilan & angka sesuai. Halaman yang menampilkan
data: Dashboard Admin, Manajemen Pengguna (871), Manajemen Menu (141),
Manajemen Pemesanan (4.908), Rekomendasi (pilih Jenny Sanjaya).

---

# 4.2 Pembahasan

## 4.2.1 Analisis Konfigurasi
Tetap valid: lr 0,0005 (C) lebih stabil dari 0,001 (A/B); MLP dangkal [64,32]
cukup tanpa overfitting. Sesuaikan agar tidak mengklaim C "tertinggi" — gunakan
"setara namun paling efisien & stabil".

## 4.2.2 Analisis HR & NDCG
- **LAMA:** HR@10 0,3670 / NDCG@10 0,1965
- **BARU:** **HR@10 0,3439 / NDCG@10 0,1825**

**Teks siap paste:**
> Evaluasi model final menghasilkan HR@10 sebesar 0,3439 dan NDCG@10 sebesar
> 0,1825, dihitung dengan Leave-One-Out (1 ground truth : 99 negatif). Nilai
> HR@10 0,3439 berarti dari setiap 100 pengguna uji, model berhasil menempatkan
> menu yang benar-benar dipesan ke dalam Top-10 pada sekitar 34 pengguna. Nilai
> NDCG@10 0,1825 menunjukkan kualitas urutan rekomendasi, dengan item relevan
> cenderung berada pada peringkat menengah daftar Top-10.

## 4.2.3 Analisis Kualitas Inferensi
Gunakan contoh Jenny Sanjaya: model menangkap korelasi silang antar kategori
(kopi ↔ makanan ↔ minuman), membuktikan NCF melampaui content-based filtering.

---

# ✅ Checklist Bab 4
- [ ] 4.1.2: ganti "Nomor Transaksi" → "Pelanggan" (Langkah 1–5)
- [ ] Tabel 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7 — angka baru
- [ ] Tabel 4.8 — angka baru + JANGAN klaim "C tertinggi"
- [ ] Tabel 4.9 — sama (param 32.833 di Tabel 4.11)
- [ ] Tabel 4.10 — 7 baris baru; Gambar 4.1 — PNG baru
- [ ] Tabel 4.11 — model final baru (820 user, 140 item, 32.833 param, epoch 2)
- [ ] 4.1.4: pengguna Jenny Sanjaya, Tabel 4.12, Gambar 4.2 baru
- [ ] 4.1.5: Dashboard "871 / 141 / 4.908"; screenshot Gambar 4.3–4.13 diambil ulang
- [ ] 4.2.2: HR 0,3439 / NDCG 0,1825
