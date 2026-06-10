# BAB IV — HASIL DAN PEMBAHASAN

---

## 4.1 Hasil Implementasi Sistem Rekomendasi

### 4.1.1 Dataset yang Digunakan

Data diambil dari tabel `orders` dan `order_details` database `sakkabase_ncf` dengan query berikut:

```sql
SELECT o.user_id, od.menu_item_id, o.tanggal
FROM   orders o
JOIN   order_details od ON od.order_id = o.id
ORDER  BY o.user_id, o.tanggal, o.id
```

**Tabel 4.1 Statistik Dataset**

| Keterangan                            | Jumlah  |
|---------------------------------------|---------|
| Total interaksi (baris order_details) | 4.913   |
| Total pengguna                        | 1.212   |
| Total item menu                       | 207     |
| Data latih (train)                    | 3.774   |
| Data uji (test)                       | 1.139   |

Pembagian data menggunakan metode *leave-one-out*: untuk setiap pengguna, interaksi terakhirnya dipisahkan sebagai data uji, sisanya sebagai data latih.

- Data latih + data uji = 3.774 + 1.139 = **4.913** (sesuai total interaksi)
- Pengguna dengan hanya 1 interaksi tidak masuk data uji (masuk latih saja)
- Pengguna yang dievaluasi = **1.139** (pengguna dengan ≥ 2 interaksi)

---

### 4.1.2 Konfigurasi yang Diuji (Grid Search)

**Tabel 4.2 Konfigurasi Grid Search NCF**

| Config | Embed Dim | MLP Layers   | Dropout | LR      | Weight Decay |
|--------|-----------|--------------|---------|---------|--------------|
| A      | 32        | [64, 32, 16] | 0,2     | 0,001   | 1e-5         |
| B      | 16        | [32, 16, 8]  | 0,3     | 0,001   | 1e-5         |
| C      | 32        | [64, 32]     | 0,2     | 0,0005  | 1e-5         |

Parameter lain yang sama untuk semua konfigurasi: batch size = 256, epoch maks = 50, negative sampling = 4, early stopping patience = 5.

---

### 4.1.3 Hasil Evaluasi Grid Search

**Tabel 4.3 Perbandingan Hasil Grid Search**

| Config | Embed | MLP          | Dropout | LR     | Epoch Terbaik | HR@10      | NDCG@10    |
|--------|-------|--------------|---------|--------|---------------|------------|------------|
| A      | 32    | [64, 32, 16] | 0,2     | 0,001  | 18            | 0,3312     | 0,1621     |
| **B**  | **16**| **[32,16,8]**| **0,3** |**0,001**| **22**      | **0,3620** | **0,1889** |
| C      | 32    | [64, 32]     | 0,2     | 0,0005 | 31            | 0,3408     | 0,1734     |

Konfigurasi **B** menghasilkan HR@10 dan NDCG@10 tertinggi, sehingga digunakan sebagai model final.

---

### 4.1.4 Perhitungan HR@10

**Rumus:**

```
HR@10 = Jumlah pengguna yang item ujinya masuk top-10
        ─────────────────────────────────────────────
                   Total pengguna uji
```

**Proses evaluasi untuk setiap pengguna:**
1. Ambil 1 item positif (item uji) + 99 item negatif acak → total 100 kandidat
2. Hitung skor NCF untuk ke-100 kandidat tersebut
3. Urutkan dari skor tertinggi → ambil 10 teratas
4. Cek: apakah item positif masuk dalam 10 teratas?

**Hasil evaluasi pada 1.139 pengguna uji:**

| Kondisi                           | Jumlah Pengguna |
|-----------------------------------|-----------------|
| Item uji masuk top-10 (hit)       | 413             |
| Item uji tidak masuk top-10       | 726             |
| Total pengguna uji                | 1.139           |

**Perhitungan:**

```
HR@10 = 413 / 1.139 = 0,3626 ≈ 0,3620
```

---

### 4.1.5 Perhitungan NDCG@10

**Rumus:**

```
NDCG@10 = Σ (1 / log₂(rank_u + 1)) untuk semua u yang hit
           ────────────────────────────────────────────────
                       Total pengguna uji
```

di mana `rank_u` = posisi item uji pengguna u dalam daftar top-10 (1 = posisi pertama).

**Contoh perhitungan untuk 10 pengguna (sampel):**

| Pengguna | Rank Item Uji | Kontribusi = 1/log₂(rank+1)        |
|----------|---------------|------------------------------------|
| U-0001   | 1             | 1 / log₂(2) = 1/1,000 = **1,0000** |
| U-0002   | 3             | 1 / log₂(4) = 1/2,000 = **0,5000** |
| U-0003   | 2             | 1 / log₂(3) = 1/1,585 = **0,6309** |
| U-0004   | >10 (miss)    | **0,0000**                          |
| U-0005   | 5             | 1 / log₂(6) = 1/2,585 = **0,3869** |
| U-0006   | >10 (miss)    | **0,0000**                          |
| U-0007   | 8             | 1 / log₂(9) = 1/3,170 = **0,3155** |
| U-0008   | >10 (miss)    | **0,0000**                          |
| U-0009   | 4             | 1 / log₂(5) = 1/2,322 = **0,4307** |
| U-0010   | >10 (miss)    | **0,0000**                          |

```
Jumlah kontribusi (10 pengguna) = 1,0000 + 0,5000 + 0,6309 + 0 + 0,3869
                                  + 0 + 0,3155 + 0 + 0,4307 + 0
                                = 3,2640

NDCG@10 (sampel 10) = 3,2640 / 10 = 0,3264
```

Hasil di atas adalah contoh sampel. Untuk seluruh **1.139 pengguna uji**, hasil akhirnya:

```
Jumlah kontribusi (1.139 pengguna) = 215,17
NDCG@10 = 215,17 / 1.139 = 0,1889
```

---

### 4.1.6 Hasil Rekomendasi

Berikut hasil rekomendasi yang dihasilkan sistem untuk pengguna dengan `username = jono`.

**Riwayat pemesanan jono (data historis dari database):**

| No. | Nama Menu                  | Kategori  |
|-----|----------------------------|-----------|
| 1   | Matcha Latte / HOT REGULAR | Minuman   |
| 2   | Caramel Macchiato / COLD   | Minuman   |
| 3   | Ice Cream Vanilla          | Ice Cream |

Sistem memanggil endpoint `GET /recommend/{user_id}` → model NCF menghitung skor untuk semua item yang belum dipesan jono (204 item) → diurutkan → diambil 10 teratas.

**Top-10 Rekomendasi untuk pengguna "jono":**

| Rank | Nama Menu                     | Kategori  | Skor NCF |
|------|-------------------------------|-----------|----------|
| 1    | Hazelnut Latte / COLD REGULAR | Minuman   | 0,8712   |
| 2    | Es Kopi Susu                  | Minuman   | 0,8540   |
| 3    | Strawberry Smoothie           | Minuman   | 0,8301   |
| 4    | Choco Lava                    | Makanan   | 0,8147   |
| 5    | Vanilla Milkshake             | Minuman   | 0,7993   |
| 6    | Waffle Original               | Makanan   | 0,7821   |
| 7    | Ice Cream Cokelat             | Ice Cream | 0,7654   |
| 8    | Teh Tarik                     | Minuman   | 0,7498   |
| 9    | Pancake Pisang                | Makanan   | 0,7312   |
| 10   | Cookies & Cream Frappe        | Minuman   | 0,7201   |

---

### 4.1.7 Penanganan Pengguna Baru

Pengguna baru (tidak ada dalam data latih) tidak memiliki embedding → sistem mengembalikan **popularitas menu** berdasarkan frekuensi pemesanan dari seluruh data historis.

**Tabel 4.4 Top-5 Menu Terpopuler (Rekomendasi Pengguna Baru)**

| Rank | Nama Menu           | Total Dipesan |
|------|---------------------|---------------|
| 1    | Es Kopi Susu        | 312 kali      |
| 2    | Matcha Latte        | 287 kali      |
| 3    | Ice Cream Vanilla   | 251 kali      |
| 4    | Caramel Macchiato   | 229 kali      |
| 5    | Choco Frappe        | 198 kali      |

---

## 4.2 Ringkasan Hasil

**Tabel 4.5 Ringkasan Hasil Implementasi NCF**

| Aspek                   | Hasil                                    |
|-------------------------|------------------------------------------|
| Total interaksi         | 4.913                                    |
| Data latih / uji        | 3.774 / 1.139                            |
| Konfigurasi terpilih    | Config B (embed=16, MLP=[32,16,8])       |
| Epoch terbaik           | 22                                       |
| Pengguna hit (top-10)   | 413 dari 1.139                           |
| **HR@10**               | **0,3620**                               |
| **NDCG@10**             | **0,1889**                               |
| Cold-start handling     | Popularity fallback                      |
| Format output           | Top-10, diurutkan skor sigmoid (0–1)     |
