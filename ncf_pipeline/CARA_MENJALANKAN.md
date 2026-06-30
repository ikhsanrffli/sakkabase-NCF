# Cara Menjalankan Pipeline NCF — Langkah per Langkah

Panduan menjalankan praproses → training → evaluasi → inferensi di laptop Anda.
Ikuti urut dari atas. Setiap langkah ada **tujuan** dan **hasil yang diharapkan**.

---

## Langkah 0 — Persiapan (sekali saja)

**Tujuan:** menyiapkan kode terbaru & library Python.

1. Buka proyek di VS Code → buka Terminal (menu **Terminal → New Terminal**).
2. Tarik kode terbaru:
   ```bash
   git pull origin claude/awesome-dirac-pu8v2o
   ```
3. Pastikan Python terpasang:
   ```bash
   python --version
   ```
   (Harus muncul Python 3.x. Jika "command not found", coba `py --version`.)
4. Pasang library yang dibutuhkan:
   ```bash
   pip install torch pandas scikit-learn numpy openpyxl matplotlib
   ```
   **Hasil:** semua library terpasang. (Proses `torch` agak besar, tunggu sampai selesai.)

5. Masuk ke folder pipeline:
   ```bash
   cd ncf_pipeline
   ```
   > ⚠️ Semua langkah berikut dijalankan dari dalam folder `ncf_pipeline`.

---

## Langkah 1 — Grid Search (memilih konfigurasi terbaik)

**Tujuan:** melatih 3 konfigurasi (A, B, C) dan membandingkannya → bahan **Tabel 4.8**.

```bash
python grid_search.py
```

**Hasil yang diharapkan (akhir output):**
```
PERBANDINGAN KONFIGURASI (Tabel 4.8)
 Konf | embed | mlp_layers     | drop | lr     | epoch | HR@10  | NDCG@10 | param
   A  |  32   | [64, 32, 16]   | 0.2  | 0.001  |   1   | 0.3524 | 0.1835  | 33345
   B  |  16   | [32, 16, 8]    | 0.3  | 0.001  |   3   | 0.3488 | 0.1824  | 16033
   C  |  32   | [64, 32]       | 0.2  | 0.0005 |   2   | 0.3439 | 0.1825  | 32833
```
> Angka HR/NDCG bisa **sedikit berbeda** antar mesin/versi PyTorch (mis. CPU vs
> GPU). Selama statistik dataset (820/140/4707) sama dan HR ≈ 0,34, berarti benar.
> **Pakai angka dari mesin Anda** untuk skripsi.

---

## Langkah 2 — Latih Model Final (Konfigurasi C)

**Tujuan:** melatih model final, menyimpan file model + riwayat per-epoch →
bahan **Tabel 4.10 & 4.11**.

```bash
python train.py
```

**Hasil yang diharapkan:**
```
MODEL FINAL — Konfigurasi C
Epoch terbaik   : 5
Training loss   : 0.4363
Total epoch     : 10
Total parameter : 32833
HR@10           : 0.3439
NDCG@10         : 0.1825
```
File yang terbentuk:
- `ncf_pipeline/models/ncf_config_C.pth` (file model)
- `ncf_pipeline/outputs/history_C.csv` (data Tabel 4.10)

---

## Langkah 3 — Inferensi Top-10 (contoh rekomendasi)

**Tujuan:** membuktikan model menghasilkan rekomendasi → bahan **Tabel 4.12**.

```bash
python predict.py "Jenny Sanjaya"
```

**Hasil yang diharapkan:**
```
TOP-10 REKOMENDASI — 'Jenny Sanjaya' (indeks 382)
 1 | A00A | 0.5413
 2 | C04B | 0.5090
 3 | A01D | 0.5043
 ...
```
> Bisa diganti nama pelanggan lain, mis. `python predict.py "Rendi Ramadhan"`.

---

## Langkah 4 — (Opsional) Perbarui rekomendasi aplikasi

**Tujuan:** menyimpan ulang Top-10 semua pengguna untuk aplikasi React
(`src/data/recommendations.json`).

```bash
python export_recommendations.py
```
**Hasil:** `820 pengguna skor model, 51 fallback`. (Hanya perlu jika Anda
melatih ulang dan ingin aplikasi ikut diperbarui.)

---

## Langkah 5 — (Opsional) Buat Gambar 4.1 (kurva)

**Tujuan:** menghasilkan grafik training loss & HR@10.

```bash
cd ..                       # kembali ke folder utama proyek
python scripts/plot_figures.py
```
**Hasil:** `figures/gambar_4_1_kurva_training.png`.

---

## Ringkasan urutan
```bash
git pull origin claude/awesome-dirac-pu8v2o
pip install torch pandas scikit-learn numpy openpyxl matplotlib
cd ncf_pipeline
python grid_search.py        # Tabel 4.8
python train.py              # Tabel 4.10 & 4.11 + file model
python predict.py "Jenny Sanjaya"   # Tabel 4.12
python export_recommendations.py    # (opsional) update aplikasi
```

## Kalau ada error
- **`ModuleNotFoundError: No module named 'torch'`** → ulangi `pip install torch ...`
- **`FileNotFoundError ... dataset.xlsx`** → pastikan menjalankan dari folder
  `ncf_pipeline` dan file `src/dataset.xlsx` ada (jalankan `git pull` dulu).
- **`predict.py` error "model belum ada"** → jalankan `python train.py` dulu.
- Angka sedikit berbeda? Pastikan tidak mengubah `config.py`; `seed=42` membuat
  hasil identik.
