# Panduan Revisi Skripsi — Skenario B (User = Pelanggan)

Dokumen ini memetakan **angka LAMA → BARU** beserta teks siap-tempel agar skripsi
selaras dengan dataset baru (User = Pelanggan asli, Item = kode menu, filter ≥2
interaksi). Semua angka baru reproducible via `scripts/train_ncf.py` (seed 42).

> Yang **TIDAK berubah**: seluruh teori NCF (Bab 2), rumus, arsitektur
> (embedding 32 → concat 64 → MLP 64→32 ReLU → sigmoid), negative sampling 4:1,
> Leave-One-Out, metrik HR@10 & NDCG@10. Hanya **data & angka hasil** yang berubah.

---

## A. BAB 3 — Dataset & Praproses

### A.1 Dimensi dataset (paragraf "Dataset")
- **LAMA:** "1.211 ID Pengguna unik dan 207 ID Item unik, dengan total 4.909 interaksi"
- **BARU:** ganti menjadi:

> Berdasarkan rekapitulasi riwayat transaksi, dataset memuat **871 pelanggan unik**
> dan **141 menu unik (berdasarkan kode produk)**, dengan total **4.908 baris
> transaksi**. Setelah dedupe pasangan pelanggan–menu menjadi interaksi biner dan
> menyaring pelanggan dengan minimal 2 interaksi, diperoleh **820 pengguna**,
> **140 menu yang memiliki interaksi**, dan **4.707 interaksi positif unik**.

### A.2 Encoding ID Pengguna & Item (ganti contoh)
- **LAMA:** User ID (No Transaksi): `'001975' → 0`, `'001976' → 1`; Item: `'C03E - NASI GORENG SPECIAL' → 0`
- **BARU:**

> Karena penelitian kini memakai **identitas pelanggan** sebagai pengguna, nilai
> User ID berupa nama pelanggan dipetakan dengan Label Encoding ke indeks integer:
> `'Acai' → 0`, `'Acang' → 1`, `'Acen' → 2`. Item dipetakan dari **kode menu**:
> `'A00A' → 0`, `'A00B' → 1`, `'A00C' → 2`.

> **Penting:** ganti semua kalimat "User ID (No Transaksi)" → "User ID (Pelanggan)".
> Inilah inti penguatan: satu **pelanggan nyata** = satu pengguna (bukan satu transaksi).

### A.3 Perubahan kalimat naratif (ganti "No Transaksi"/"transaksi" → "Pelanggan")
1. Paragraf *Pembersihan Data*: "...tidak memiliki User ID (**No Transaksi**)..."
   → "...tidak memiliki User ID (**Pelanggan**)..."
2. Paragraf *Encoding*: "User ID (**No Transaksi**)" → "User ID (**Pelanggan**)"
3. Paragraf *Pemetaan Nilai Biner*: "pasangan **transaksi**-menu" → "pasangan **pelanggan**-menu"

### A.4 Gambar 3.4 — Flowchart Pembersihan Data (perlu digambar ulang)
Ganti label di dalam flowchart: kriteria baris dibuang dari
"User ID (**No Transaksi**) tidak valid" → "**Pelanggan** atau **Produk** kosong".
Diagram lain (3.2, 3.3, 3.5, 3.6, 3.31/ERD) tidak berubah.

### A.5 Tabel 3.1–3.6 (data nyata, siap paste)
Contoh memakai pelanggan **Rendi Ramadhan** (transaksi pertama `001975`,
ter-encode ke **indeks 574**). Outlet selalu "Sakka Base - Coffee & Barber"
sehingga kolomnya diringkas. Semua nilai diambil langsung dari `src/dataset.xlsx`.

#### Tabel 3.1 — Dataset Riwayat Pemesanan (cuplikan data mentah)

| No Transaksi | Tanggal | Pelanggan | Produk | Qty |
|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| | | | A07B - LE MINERAL 600ML | 1 |
| | | | A06C - AVOCADO JUICE | 1 |
| | | | C04G - NASI CAPCAY SEAFOOD | 1 |
| 001976 | 01/01/2026 14:40 | Ahong | C02D - CHICKEN SANDWICH TOAST | 1 |
| | | | A01D - SANGER SAKKA / COLD LARGE | 1 |
| | | | A01D - SANGER SAKKA / COLD REGULAR | 1 |
| | | | A07B - LE MINERAL 600ML | 2 |

*(Sel kosong = lanjutan transaksi yang sama / merged cell pada sumber.)*

#### Tabel 3.2 — Sebelum Dataset Cleaning

| No Transaksi | Tanggal | Pelanggan | Produk | Qty | Keterangan |
|---|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 | valid |
| *(kosong)* | *(kosong)* | *(kosong)* | A07B - LE MINERAL 600ML | 1 | lanjutan transaksi |
| *(kosong)* | *(kosong)* | *(kosong)* | A06C - AVOCADO JUICE | 1 | lanjutan transaksi |
| *(kosong)* | *(kosong)* | *(kosong)* | *(kosong)* | 5349 | ❌ tidak valid — Produk kosong |

#### Tabel 3.3 — Sesudah Dataset Cleaning
Kolom transaksi diisi maju (forward-fill) sehingga tiap baris produk memiliki
Pelanggan & Tanggal; baris tanpa Produk valid dihapus.

| No Transaksi | Tanggal | Pelanggan | Produk | Qty |
|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A07B - LE MINERAL 600ML | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A06C - AVOCADO JUICE | 1 |

*(Baris dengan Produk kosong telah dihapus pada tahap ini.)*

#### Tabel 3.4 — Contoh Representasi Data Interaksi Biner
Pengguna **Rendi Ramadhan (indeks 574)** — menu yang pernah dipesan diberi label 1.

| ID Pengguna | ID Item | Kode Menu | Nama Menu | Interaksi |
|---|---|---|---|---|
| 574 | 21 | A02B | Spanish Latte Cold | 1 |
| 574 | 24 | A02E | Butterscotch Latte Cold | 1 |
| 574 | 49 | A06C | Avocado Juice | 1 |
| 574 | 56 | A07B | Le Mineral 600ml | 1 |
| 574 | 100 | C03E | Nasi Goreng Special | 1 |
| 574 | 107 | C04G | Nasi Capcay Seafood | 1 |
| 574 | 6 | A01B | *(belum pernah dipesan)* | 0 |
| 574 | 70 | A09H | *(belum pernah dipesan)* | 0 |

*(Rendi memiliki 13 interaksi positif; di atas cuplikannya. Pasangan
pengguna–menu yang tak pernah muncul diberi label 0.)*

#### Tabel 3.5 — Contoh Hasil Negative Sampling (rasio 1 : 4)
Untuk 1 item positif, diambil 4 item negatif acak yang belum pernah dipesan
pengguna 574.

| ID Pengguna | ID Item | Kode Menu | Label |
|---|---|---|---|
| 574 | 21 | A02B | 1 (positif) |
| 574 | 28 | A02I | 0 (negatif) |
| 574 | 6 | A01B | 0 (negatif) |
| 574 | 70 | A09H | 0 (negatif) |
| 574 | 62 | A08F | 0 (negatif) |

#### Tabel 3.6 — Contoh Perubahan Data pada Embedding Layer
Pengguna 574 (Rendi Ramadhan) dengan item 21 (A02B). Nilai vektor di bawah
bersifat **ilustrasi** — nilai sebenarnya dipelajari model saat pelatihan.

| Pengguna (Asli) | ID Pengguna (Encoded) | Item (Asli) | ID Item (Encoded) | Vektor Embedding Pengguna pᵤ (32) | Vektor Embedding Item qᵢ (32) | Vektor Gabungan (64) |
|---|---|---|---|---|---|---|
| Rendi Ramadhan | 574 | A02B - Spanish Latte Cold | 21 | [0.12, 0.45, …, 0.88] | [0.76, 0.23, …, 0.91] | [0.12, 0.45, …, 0.88, 0.76, 0.23, …, 0.91] |
| Rendi Ramadhan | 574 | A06C - Avocado Juice | 49 | [0.12, 0.45, …, 0.88] | [0.34, 0.67, …, 0.11] | [0.12, 0.45, …, 0.88, 0.34, 0.67, …, 0.11] |

---

## B. BAB 4 — Hasil

### B.1 Tabel 4.7 — Statistik Akhir Dataset Setelah Praproses

| Keterangan | LAMA | **BARU** |
|---|---|---|
| Total pengguna unik | 1.212 | **871** |
| Total item menu unik | 207 | **141 (140 memiliki interaksi)** |
| Total interaksi | 4.913 | **4.707** |
| Rata-rata interaksi per pengguna | 4,05 | **5,74** |
| Data latih (train set) | 3.774 | **3.887** |
| Data uji (test set) | 1.139 pengguna | **820 pengguna** |
| Pengguna hanya 1 interaksi (dibuang) | 73 | **51** |
| Total sampel per epoch (latih + negatif) | 18.880 | **19.435** |
| Kandidat evaluasi per pengguna | 100 (1+99) | 100 (1+99) — sama |
| Strategi pembagian | Leave-One-Out | Leave-One-Out — sama |

### B.2 Tabel 4.8 — Perbandingan Konfigurasi

| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | **5** | **0,3451** | **0,1806** |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | **5** | **0,3402** | **0,1772** |
| **C** | 32 | [64, 32] | 0,2 | 0,0005 | **2** | **0,3439** | **0,1825** |

Narasi pemilihan model final (ganti):
> Ketiga konfigurasi menghasilkan HR@10 yang berdekatan (selisih ±0,005). Konfigurasi
> A dengan learning rate lebih besar cepat konvergen lalu plateau,
> sedangkan **Konfigurasi C konvergen stabil pada epoch 2**. Karena performa
> setara namun **Konfigurasi C memiliki jumlah parameter relatif sedikit (32.833)**
> dan konvergensi paling stabil, C ditetapkan sebagai **model final**.

### B.3 Tabel 4.9 — Hyperparameter Konfigurasi C
Hyperparameter **TIDAK berubah** (emb 32, MLP [64,32], dropout 0,2, lr 0,0005,
weight decay 1e-5, batch 256, max 50 epoch, neg 4, patience 5, Adam, BCE).
- Hanya **Total parameter model: 47.521 → 32.833**.

### B.4 Tabel 4.10 — Training Loss per Epoch (Konfigurasi C)
Ganti seluruh isi tabel dengan data dari `scripts/history_configC.csv`:

| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan |
|---|---|---|---|---|
| 1 | 0,6687 | 0,3366 | 0,1833 | Model terbaik tersimpan |
| 2 | 0,5536 | 0,3439 | 0,1825 | **Model terbaik tersimpan** |
| 3 | 0,4609 | 0,3378 | 0,1776 | Tidak ada peningkatan (1/5) |
| 4 | 0,4447 | 0,3390 | 0,1805 | Tidak ada peningkatan (2/5) |
| 5 | 0,4370 | 0,3439 | 0,1797 | Tidak ada peningkatan (3/5) |
| 6 | 0,4350 | 0,3305 | 0,1771 | Tidak ada peningkatan (4/5) |
| 7 | 0,4362 | 0,3329 | 0,1737 | Early stop terpenuhi (5/5) |

### B.5 Gambar 4.1 — Kurva Training Loss & HR@10
Ganti gambar dengan file: **`figures/gambar_4_1_kurva_training.png`**

### B.6 Tabel 4.11 — Informasi Model Final

| Informasi | LAMA | **BARU** |
|---|---|---|
| Path file model | models/ncf_config_C.pth | models/ncf_config_C.pth |
| Epoch terbaik | 8 | **2** |
| Training loss epoch terbaik | 0,4163 | **0,5536** |
| Total epoch dijalankan | 13 | **7** |
| Total parameter model | 47.521 | **32.833** |
| HR@10 (data uji) | 0,3670 | **0,3439** |
| NDCG@10 (data uji) | 0,1965 | **0,1825** |

### B.7 Tabel 4.12 & Gambar 4.2 — Contoh Inferensi
- **LAMA:** "Pengguna ID 2424".
- **BARU:** ganti ke salah satu pelanggan nyata (mis. *Jenny Sanjaya*) beserta
  Top-10 menu hasil model. *(Bisa di-generate ulang — minta saja.)*

### B.8 Paragraf hasil akhir (kesimpulan evaluasi)
- **LAMA:** "HR@10 sebesar 0,3670 dan NDCG@10 sebesar 0,1965"
- **BARU:** "**HR@10 sebesar 0,3439 dan NDCG@10 sebesar 0,1825**", tetap dengan
  strategi Leave-One-Out (1 positif : 99 negatif).

---

## C. BAB 3 — Perancangan Basis Data (3.3.2)
Skema 6 tabel tetap valid. Data MySQL kini diisi ulang dari dataset baru melalui
`database/sakkabase_seed.sql` (871 pelanggan + admin, 141 menu, 1.211 orders,
4.908 order_details, 1 baris model_log berisi HR/NDCG final).

---

## D. Checklist ringkas
**Bab 1 (Pendahuluan):** ✅ tidak ada perubahan wajib (tidak memuat angka dataset;
narasi sudah selaras dengan pendekatan per-pelanggan). Opsional: pertegas di Latar
Belakang bahwa unit analisis = interaksi tiap **pelanggan** dengan menu.

**Bab 2 (Teori):** ✅ tidak berubah (rumus & arsitektur NCF tetap).

**Bab 3:**
- [ ] Dimensi dataset (871 / 141 / 4.707) & contoh encoding (Pelanggan)
- [ ] Ganti kalimat "No Transaksi"/"transaksi" → "Pelanggan" (3 paragraf, lihat A.3)
- [ ] Gambar 3.4 (flowchart cleaning) — relabel ke "Pelanggan/Produk kosong"
- [ ] Tabel 3.1–3.6 — pakai data nyata di A.5
- [ ] Perancangan Basis Data — sudah diisi via `database/sakkabase_seed.sql`

**Bab 4:**
- [ ] Tabel 4.7 (statistik) — angka baru
- [ ] Tabel 4.8 (A/B/C) — angka baru
- [ ] Tabel 4.9 — hanya total parameter 32.833
- [ ] Tabel 4.10 — 10 baris epoch baru
- [ ] Gambar 4.1 — ganti PNG baru
- [ ] Tabel 4.11 — model final baru
- [ ] Tabel 4.12 / Gambar 4.2 — pelanggan nyata
- [ ] Gambar 4.4–4.13 (screenshot implementasi) — ambil ulang dgn data baru
- [ ] Paragraf hasil — HR 0,3439 / NDCG 0,1825
