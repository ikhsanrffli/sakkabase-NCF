# Panduan Demo Pengujian NCF saat Sidang (live di website)

Skenario: penguji membuat akun baru, memesan menu, lalu sistem menampilkan
Top-10 rekomendasi NCF **beserta nilai HR@10 & NDCG@10** — semuanya live di browser.

---

## Persiapan (sebelum sidang) — 3 terminal

**Terminal 1 — latih model (sekali saja):**
```bash
cd ncf_pipeline
pip install torch pandas scikit-learn numpy openpyxl
python train.py            # membuat models/ncf_config_C.pth
```

**Terminal 2 — jalankan backend:**
```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --port 8000
```

**Terminal 3 — jalankan website:**
```bash
npm install
npm run dev                # buka http://localhost:5173
```

> Biarkan Terminal 2 & 3 tetap berjalan selama demo.

---

## Langkah demo (di depan penguji)

1. **Registrasi** — buka website → "Daftar di sini" → buat akun, mis.
   nama "Penguji A", username `pengujiA`, password bebas.
2. **Login** sebagai Penguji A (tab **User**).
3. **Pesan menu** — buka **Pesan Menu** → pesan beberapa menu **berurutan**.
   Pesanan **TERAKHIR** akan jadi "menu uji" yang disembunyikan. Contoh urutan:
   Espresso → Cappuccino → Cafe Latte → **(terakhir) Sanger Sakka**.
   > Tips: agar lebih mungkin HIT, pesan menu yang sekategori/berhubungan.
4. **Buka "Rekomendasiku"** — sistem otomatis:
   - menyembunyikan pesanan terakhir (ground truth),
   - melatih embedding Penguji A (fold-in) dari pesanan lainnya,
   - menampilkan **Top-10 + skor**, dan panel **Hasil Pengujian**:
     - menu uji + posisinya,
     - **HR@10** (1 = HIT bila menu uji masuk Top-10, 0 = MISS),
     - **NDCG@10**.

---

## Yang harus Anda jelaskan ke penguji

- **HR@10 / NDCG@10 satu user = hit/miss (1 atau 0).** Angka **0,3439 / 0,1825**
  di skripsi adalah **rata-rata 820 user** pada evaluasi keseluruhan (Bab 4).
- **User baru & cold-start:** model NCF tidak otomatis mengenal user baru. Sistem
  memakai *fold-in* — melatih embedding user baru dari riwayatnya tanpa melatih
  ulang seluruh model. Ini menjawab kelemahan klasik cold-start pada NCF.
- **Arsitektur:** website (React) ↔ backend (FastAPI) ↔ model NCF (PyTorch).
  Konsisten dengan stack di skripsi (FastAPI, PyTorch).

## Jika "Rekomendasiku" menampilkan peringatan backend offline
Artinya Terminal 2 (uvicorn) belum jalan / model belum dilatih. Jalankan
`python train.py` lalu `uvicorn main:app --port 8000`, lalu muat ulang halaman.
