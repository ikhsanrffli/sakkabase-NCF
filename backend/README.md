# Backend FastAPI — Rekomendasi & Pengujian NCF

Backend kecil yang melayani rekomendasi NCF real-time untuk website, termasuk
**user baru** (lewat teknik *fold-in*) dan **evaluasi HR@10 / NDCG@10** secara
leave-one-out — sehingga halaman "Rekomendasiku" bisa menampilkan hasil
pengujian langsung di browser.

## Prasyarat
Model harus sudah dilatih (file `ncf_pipeline/models/ncf_config_C.pth`):
```bash
cd ncf_pipeline
python train.py
```

## Menjalankan
```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```
Backend siap di `http://localhost:8000`. Biarkan jendela terminal ini terbuka,
lalu jalankan website (`npm run dev`) di terminal lain.

## Endpoint
- `GET /health` → status + jumlah user/item + HR/NDCG agregat.
- `POST /recommend` → body `{ "orders": ["A01A","A13A","C03A"], "evaluate": true }`
  - `orders`: kode menu urut kronologis. Jika `evaluate=true` & ≥2 menu,
    pesanan **terakhir disembunyikan** sebagai ground truth (leave-one-out).
  - Respons: `top10` (menu + skor), `evaluation` (HR@10, NDCG@10, hit, rank).

## Cara kerja (singkat)
1. Model NCF terlatih dimuat & **dibekukan** (item embedding + MLP).
2. Untuk user (baru), embedding-nya **dilatih singkat** (fold-in) dari menu yang
   pernah dipesan — ini menyelesaikan *cold-start* tanpa melatih ulang seluruh model.
3. Semua menu kandidat diberi skor sigmoid → Top-10.
4. Jika ada ground truth (pesanan terakhir): dicek apakah masuk Top-10
   (HR@10 = 1/0) dan posisinya (NDCG@10).

> Catatan: HR/NDCG untuk satu user bernilai hit (1) atau miss (0). Rata-rata
> seluruh data uji (820 user) = HR@10 0,3500 / NDCG@10 0,1822 (hasil di skripsi).
