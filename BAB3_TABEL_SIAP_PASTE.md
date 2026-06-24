# Bab 3 — Tabel 3.1–3.6 Siap Paste (Skenario B, data nyata)

Contoh memakai pelanggan **Rendi Ramadhan** (transaksi pertama `001975`,
ter-encode ke **indeks 574**). Outlet selalu "Sakka Base - Coffee & Barber"
sehingga kolomnya diringkas. Semua nilai diambil langsung dari `src/dataset.xlsx`.

---

## Contoh Encoding (paragraf A.2)
- **Pengguna:** `'Acai' → 0`, `'Acang' → 1`, `'Acen' → 2` (Label Encoding alfabetis)
- **Item (kode):** `'A00A' → 0`, `'A00B' → 1`, `'A00C' → 2`

---

## Tabel 3.1 — Dataset Riwayat Pemesanan (cuplikan data mentah)

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

---

## Tabel 3.2 — Sebelum Dataset Cleaning

| No Transaksi | Tanggal | Pelanggan | Produk | Qty | Keterangan |
|---|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 | valid |
| *(kosong)* | *(kosong)* | *(kosong)* | A07B - LE MINERAL 600ML | 1 | lanjutan transaksi |
| *(kosong)* | *(kosong)* | *(kosong)* | A06C - AVOCADO JUICE | 1 | lanjutan transaksi |
| *(kosong)* | *(kosong)* | *(kosong)* | *(kosong)* | 5349 | ❌ tidak valid — Produk kosong |

---

## Tabel 3.3 — Sesudah Dataset Cleaning

Kolom transaksi diisi maju (forward-fill) sehingga tiap baris produk memiliki
Pelanggan & Tanggal; baris tanpa Produk valid dihapus.

| No Transaksi | Tanggal | Pelanggan | Produk | Qty |
|---|---|---|---|---|
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | C03E - NASI GORENG SPECIAL | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A07B - LE MINERAL 600ML | 1 |
| 001975 | 01/01/2026 12:49 | Rendi Ramadhan | A06C - AVOCADO JUICE | 1 |

*(Baris dengan Produk kosong telah dihapus pada tahap ini.)*

---

## Tabel 3.4 — Contoh Representasi Data Interaksi Biner
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

---

## Tabel 3.5 — Contoh Hasil Negative Sampling (rasio 1 : 4)
Untuk 1 item positif, diambil 4 item negatif acak yang belum pernah dipesan
pengguna 574.

| ID Pengguna | ID Item | Kode Menu | Label |
|---|---|---|---|
| 574 | 21 | A02B | 1 (positif) |
| 574 | 28 | A02I | 0 (negatif) |
| 574 | 6 | A01B | 0 (negatif) |
| 574 | 70 | A09H | 0 (negatif) |
| 574 | 62 | A08F | 0 (negatif) |

---

## Tabel 3.6 — Contoh Perubahan Data pada Embedding Layer
Pengguna 574 (Rendi Ramadhan) dengan item 21 (A02B). Nilai vektor di bawah
bersifat **ilustrasi** — nilai sebenarnya dipelajari model saat pelatihan.

| Pengguna (Asli) | ID Pengguna (Encoded) | Item (Asli) | ID Item (Encoded) | Vektor Embedding Pengguna pᵤ (32) | Vektor Embedding Item qᵢ (32) | Vektor Gabungan (64) |
|---|---|---|---|---|---|---|
| Rendi Ramadhan | 574 | A02B - Spanish Latte Cold | 21 | [0.12, 0.45, …, 0.88] | [0.76, 0.23, …, 0.91] | [0.12, 0.45, …, 0.88, 0.76, 0.23, …, 0.91] |
| Rendi Ramadhan | 574 | A06C - Avocado Juice | 49 | [0.12, 0.45, …, 0.88] | [0.34, 0.67, …, 0.11] | [0.12, 0.45, …, 0.88, 0.34, 0.67, …, 0.11] |
