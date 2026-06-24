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

### A.3 Tabel 3.1–3.6 (contoh data)
Perbarui cuplikan agar memakai nama pelanggan asli (mis. Rendi Ramadhan, Ahong)
dan kode menu. Strukturnya sama, hanya isi contoh yang berubah.

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
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | **1** | **0,3524** | **0,1835** |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | **3** | **0,3488** | **0,1824** |
| **C** | 32 | [64, 32] | 0,2 | 0,0005 | **5** | **0,3500** | **0,1822** |

Narasi pemilihan model final (ganti):
> Ketiga konfigurasi menghasilkan HR@10 yang berdekatan (selisih ±0,004). Konfigurasi
> A dengan learning rate lebih besar cepat konvergen pada epoch awal lalu plateau,
> sedangkan **Konfigurasi C konvergen lebih stabil pada epoch 5**. Karena performa
> setara namun **Konfigurasi C memiliki jumlah parameter paling sedikit (32.833)**
> dan konvergensi paling stabil, C ditetapkan sebagai **model final**.

### B.3 Tabel 4.9 — Hyperparameter Konfigurasi C
Hyperparameter **TIDAK berubah** (emb 32, MLP [64,32], dropout 0,2, lr 0,0005,
weight decay 1e-5, batch 256, max 50 epoch, neg 4, patience 5, Adam, BCE).
- Hanya **Total parameter model: 47.521 → 32.833**.

### B.4 Tabel 4.10 — Training Loss per Epoch (Konfigurasi C)
Ganti seluruh isi tabel dengan data dari `scripts/history_configC.csv`:

| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan |
|---|---|---|---|---|
| 1 | 0,6688 | 0,3476 | 0,1797 | - |
| 2 | 0,5525 | 0,3451 | 0,1828 | - |
| 3 | 0,4599 | 0,3451 | 0,1800 | - |
| 4 | 0,4432 | 0,3415 | 0,1780 | - |
| 5 | 0,4363 | 0,3500 | 0,1822 | **Model terbaik tersimpan** |
| 6 | 0,4348 | 0,3402 | 0,1800 | Tidak ada peningkatan (1/5) |
| 7 | 0,4353 | 0,3500 | 0,1828 | Tidak ada peningkatan (2/5) |
| 8 | 0,4340 | 0,3415 | 0,1805 | Tidak ada peningkatan (3/5) |
| 9 | 0,4330 | 0,3415 | 0,1799 | Tidak ada peningkatan (4/5) |
| 10 | 0,4330 | 0,3439 | 0,1798 | Early stop terpenuhi (5/5) |

### B.5 Gambar 4.1 — Kurva Training Loss & HR@10
Ganti gambar dengan file: **`figures/gambar_4_1_kurva_training.png`**

### B.6 Tabel 4.11 — Informasi Model Final

| Informasi | LAMA | **BARU** |
|---|---|---|
| Path file model | models/ncf_config_C.pth | models/ncf_config_C.pth |
| Epoch terbaik | 8 | **5** |
| Training loss epoch terbaik | 0,4163 | **0,4363** |
| Total epoch dijalankan | 13 | **10** |
| Total parameter model | 47.521 | **32.833** |
| HR@10 (data uji) | 0,3670 | **0,3500** |
| NDCG@10 (data uji) | 0,1965 | **0,1822** |

### B.7 Tabel 4.12 & Gambar 4.2 — Contoh Inferensi
- **LAMA:** "Pengguna ID 2424".
- **BARU:** ganti ke salah satu pelanggan nyata (mis. *Jenny Sanjaya*) beserta
  Top-10 menu hasil model. *(Bisa di-generate ulang — minta saja.)*

### B.8 Paragraf hasil akhir (kesimpulan evaluasi)
- **LAMA:** "HR@10 sebesar 0,3670 dan NDCG@10 sebesar 0,1965"
- **BARU:** "**HR@10 sebesar 0,3500 dan NDCG@10 sebesar 0,1822**", tetap dengan
  strategi Leave-One-Out (1 positif : 99 negatif).

---

## C. BAB 3 — Perancangan Basis Data (3.3.2)
Skema 6 tabel tetap valid. Data MySQL kini diisi ulang dari dataset baru melalui
`database/sakkabase_seed.sql` (871 pelanggan + admin, 141 menu, 1.211 orders,
4.908 order_details, 1 baris model_log berisi HR/NDCG final).

---

## D. Checklist ringkas
- [ ] Bab 3: dimensi dataset (871 / 141 / 4.707) & contoh encoding (Pelanggan)
- [ ] Bab 3: ganti "No Transaksi" → "Pelanggan" sebagai User ID
- [ ] Tabel 4.7 (statistik) — angka baru
- [ ] Tabel 4.8 (A/B/C) — angka baru
- [ ] Tabel 4.9 — hanya total parameter 32.833
- [ ] Tabel 4.10 — 10 baris epoch baru
- [ ] Gambar 4.1 — ganti PNG baru
- [ ] Tabel 4.11 — model final baru
- [ ] Tabel 4.12 / Gambar 4.2 — pelanggan nyata
- [ ] Paragraf hasil — HR 0,3500 / NDCG 0,1822
