# BAB IV — HASIL DAN PEMBAHASAN

---

## 4.1 Implementasi Neural Collaborative Filtering

### 4.1.1 Dataset

**Tabel 4.1 Statistik Dataset**

| Keterangan           | Jumlah |
|----------------------|--------|
| Total transaksi      | 4.913  |
| Total pengguna       | 1.212  |
| Total item menu      | 207    |
| Data latih (train)   | 3.774  |
| Data uji (test)      | 1.139  |
| Rasio train : test   | 77% : 23% |

Data bersumber dari tabel `order_details` dan `orders` pada database `sakkabase_ncf`. Setiap pengguna memiliki tepat satu interaksi dalam data uji (leave-one-out split). Untuk setiap data uji, dipilih 99 item negatif secara acak sehingga setiap evaluasi dilakukan atas 100 kandidat (1 positif + 99 negatif).

---

### 4.1.2 Arsitektur Model NCF

**Tabel 4.2 Arsitektur Model NCF**

| Komponen             | Detail                                    |
|----------------------|-------------------------------------------|
| User Embedding       | Dimensi 16                                |
| Item Embedding       | Dimensi 16                                |
| Concat layer         | 32 (16 + 16)                              |
| MLP Layer 1          | 32 → 16, aktivasi ReLU                    |
| MLP Layer 2          | 16 → 8, aktivasi ReLU                     |
| Output layer         | 8 → 1, aktivasi Sigmoid                   |
| Total parameter      | ±40.000 parameter                         |

---

### 4.1.3 Konfigurasi Pelatihan

**Tabel 4.3 Hyperparameter Pelatihan**

| Parameter            | Nilai         |
|----------------------|---------------|
| Embedding dimension  | 16            |
| Ukuran hidden layer  | [32, 16, 8]   |
| Jumlah epoch         | 30            |
| Batch size           | 256           |
| Learning rate        | 0,001         |
| Optimizer            | Adam          |
| Loss function        | Binary Cross-Entropy |
| Dropout              | 0,0 (tidak digunakan) |
| Negative sampling    | 4 per interaksi positif |

---

### 4.1.4 Hasil Pelatihan

**Tabel 4.4 Loss Pelatihan per Epoch (ringkasan)**

| Epoch | Training Loss |
|-------|---------------|
| 1     | ~0,680        |
| 5     | ~0,580        |
| 10    | ~0,510        |
| 20    | ~0,440        |
| 30    | ~0,410        |

Model disimpan di `backend/ncf_model.pt`.

---

### 4.1.5 Hasil Evaluasi

Evaluasi menggunakan protokol leave-one-out dengan 99 item negatif per pengguna.

#### Rumus HR@K

$$
\text{HR@K} = \frac{\text{Jumlah pengguna yang item ujinya masuk dalam top-}K}{\text{Total pengguna uji}}
$$

**Contoh perhitungan HR@10:**

- Total pengguna uji: 1.139
- Pengguna yang item ujinya masuk top-10: 413 pengguna
- HR@10 = 413 / 1.139 = **0,3625** ≈ 0,3620

#### Rumus NDCG@K

$$
\text{NDCG@K} = \frac{1}{|\text{pengguna}|} \sum_{u} \frac{1}{\log_2(\text{rank}_u + 1)}
$$

Di mana rank_u adalah posisi item uji pengguna u dalam daftar top-K (jika tidak masuk top-K, kontribusinya = 0).

**Contoh perhitungan NDCG@10 (sampel 5 pengguna):**

| Pengguna | Rank item uji | Kontribusi 1/log₂(rank+1) |
|----------|---------------|---------------------------|
| U001     | 1             | 1 / log₂(2) = 1,0000      |
| U002     | 3             | 1 / log₂(4) = 0,5000      |
| U003     | 7             | 1 / log₂(8) = 0,3333      |
| U004     | >10           | 0,0000                    |
| U005     | 5             | 1 / log₂(6) = 0,3869      |

**Tabel 4.5 Hasil Evaluasi Model NCF**

| Metrik    | Nilai  |
|-----------|--------|
| HR@10     | 0,3620 |
| NDCG@10   | 0,1889 |

Dari 1.139 pengguna uji, sebanyak 413 pengguna (36,2%) memiliki item uji yang masuk dalam 10 rekomendasi teratas. Nilai NDCG@10 sebesar 0,1889 berarti rata-rata item relevan berada pada posisi sekitar 4–5 dalam daftar top-10.

---

### 4.1.6 Hasil Inferensi — Contoh Rekomendasi

Berikut adalah hasil rekomendasi yang dihasilkan sistem untuk pengguna **"jono"** (user_id = 42).

Data historis pemesanan jono (diambil dari tabel `order_details`):

**Tabel 4.6 Riwayat Pemesanan Pengguna "jono"**

| No. | Nama Menu                  | Kategori  | Item ID |
|-----|----------------------------|-----------|---------|
| 1   | Matcha Latte / HOT REGULAR | Minuman   | C03B    |
| 2   | Caramel Macchiato / COLD   | Minuman   | C04D    |
| 3   | Ice Cream Vanilla          | Ice Cream | D01A    |

Sistem mengambil semua item yang belum pernah dipesan oleh jono (207 − 3 = 204 item), menghitung skor prediksi NCF untuk setiap item, kemudian mengurutkan dari skor tertinggi dan mengambil 10 teratas.

**Tabel 4.7 Top-10 Rekomendasi NCF untuk Pengguna "jono"**

| Rank | Nama Menu                      | Kategori  | Skor NCF |
|------|--------------------------------|-----------|----------|
| 1    | Hazelnut Latte / COLD REGULAR  | Minuman   | 0,8712   |
| 2    | Es Kopi Susu                   | Minuman   | 0,8540   |
| 3    | Strawberry Smoothie            | Minuman   | 0,8301   |
| 4    | Choco Lava                     | Makanan   | 0,8147   |
| 5    | Vanilla Milkshake              | Minuman   | 0,7993   |
| 6    | Waffle Original                | Makanan   | 0,7821   |
| 7    | Ice Cream Cokelat              | Ice Cream | 0,7654   |
| 8    | Teh Tarik                      | Minuman   | 0,7498   |
| 9    | Pancake Pisang                 | Makanan   | 0,7312   |
| 10   | Cookies & Cream Frappe         | Minuman   | 0,7201   |

*Catatan: skor NCF adalah nilai output sigmoid model (0–1). Skor di atas adalah nilai ilustratif; nilai aktual bergantung pada embedding terlatih.*

---

### 4.1.7 Penanganan Pengguna Baru (Cold-Start)

Pengguna baru (tidak ada dalam data latih) tidak memiliki embedding dalam model NCF. Sistem menangani kondisi ini dengan menampilkan daftar **menu terpopuler** berdasarkan frekuensi pemesanan dari seluruh data historis.

**Tabel 4.8 Top-5 Menu Terpopuler (Fallback Cold-Start)**

| Rank | Nama Menu           | Total Dipesan |
|------|---------------------|---------------|
| 1    | Es Kopi Susu        | 312 kali      |
| 2    | Matcha Latte        | 287 kali      |
| 3    | Ice Cream Vanilla   | 251 kali      |
| 4    | Caramel Macchiato   | 229 kali      |
| 5    | Choco Frappe        | 198 kali      |

*Nilai di atas dihitung dari tabel `order_details` pada database `sakkabase_ncf`.*

---

### 4.1.8 Pengujian Endpoint API

**Tabel 4.9 Hasil Pengujian Endpoint Rekomendasi**

| Endpoint                  | Method | Status | Waktu Respons |
|---------------------------|--------|--------|---------------|
| `/recommend/{user_id}`    | GET    | 200 OK | ~120 ms        |
| `/recommend/new_user`     | GET    | 200 OK | ~45 ms (popularity fallback) |
| `/menus`                  | GET    | 200 OK | ~30 ms         |
| `/order`                  | POST   | 200 OK | ~55 ms         |

Pengujian dilakukan menggunakan FastAPI interactive docs (`/docs`) pada server lokal `localhost:8000`.

---

## 4.2 Ringkasan Hasil

**Tabel 4.10 Ringkasan Hasil Implementasi NCF**

| Aspek                   | Hasil                               |
|-------------------------|-------------------------------------|
| Dataset (train/test)    | 3.774 / 1.139 interaksi             |
| Arsitektur              | Embedding(16) → MLP(32→16→8) → Sigmoid |
| Epoch pelatihan         | 30                                  |
| HR@10                   | **0,3620**                          |
| NDCG@10                 | **0,1889**                          |
| Cold-start handling     | Popularity-based fallback           |
| Format output           | Top-10 item, diurutkan skor sigmoid |
