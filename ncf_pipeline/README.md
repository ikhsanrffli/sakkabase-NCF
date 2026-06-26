# ncf_pipeline — Pipeline Training NCF (Skenario B)

Pipeline Python referensi yang **sudah benar** untuk Skenario B
(**User = Pelanggan**, item = kode menu, filter ≥2 interaksi). Strukturnya
sengaja dibuat sama seperti proyek Anda agar mudah dibandingkan / dipakai.

## Struktur
| File | Fungsi | Untuk skripsi |
|---|---|---|
| `config.py` | Path dataset & hyperparameter (A/B/C) | Tabel 4.9 |
| `dataset.py` | Praproses: cleaning, encoding, biner, neg-sampling, leave-one-out | Bab 3, Tabel 3.1–3.6, 4.7 |
| `model.py` | Arsitektur NCF (embedding → MLP → sigmoid) | Bab 3 |
| `train.py` | Latih 1 konfigurasi + simpan model & riwayat | Tabel 4.10, 4.11, Gambar 4.1 |
| `grid_search.py` | Latih A/B/C + tabel perbandingan | Tabel 4.8 |
| `predict.py` | Top-10 rekomendasi 1 pengguna | Tabel 4.12 |

## Cara pakai
```bash
pip install torch pandas scikit-learn numpy openpyxl
cd ncf_pipeline

python grid_search.py          # bandingkan A/B/C (Tabel 4.8)
python train.py                # latih + simpan model final (C)
python predict.py "Rendi Ramadhan"   # Top-10 utk satu pelanggan
```

## Hasil yang diharapkan (reproducible, seed 42)
- Statistik: 820 pengguna, 140 item, 4.707 interaksi, 3.887 latih, 820 uji
- Konfigurasi final C: **HR@10 ≈ 0,3439**, **NDCG@10 ≈ 0,1825**, 32.833 parameter (angka bisa sedikit beda per mesin/versi PyTorch)

## ⚠️ Perbedaan utama vs versi lama Anda
Yang membuat hasil benar untuk Skenario B ada di `config.py` dan `dataset.py`:
- `USER_COL = "Pelanggan"`  ← **BUKAN** "No Transaksi"
- `ITEM_BY_CODE = True`     ← varian ukuran digabung jadi 1 menu
- `MIN_INTERACT = 2`        ← filter agar leave-one-out valid

Jika proyek lama Anda masih memetakan **No Transaksi sebagai user**, itulah yang
harus diubah. Bandingkan `dataset.py` ini dengan milik Anda.
