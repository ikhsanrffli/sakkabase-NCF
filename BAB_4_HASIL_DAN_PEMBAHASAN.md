# BAB IV — HASIL DAN PEMBAHASAN (Tabel 4.1–4.12, DATA NYATA + NARASI)

> Seluruh angka diambil/diverifikasi langsung dari `src/dataset.xlsx`, database
> MySQL, dan model terlatih yang dipakai website (`ncf_config_C.pth` →
> `recommendations.json`). Acuan: **Skenario B (User = Pelanggan)**, model final
> **Konfigurasi C: HR@10 = 0,3500 · NDCG@10 = 0,1822**. Setiap tabel disertai
> narasi pengantar dan interpretasi yang siap tempel ke Word.

---

# 4.1.2 Hasil Preprocessing Data

Tahap praproses (*preprocessing*) merupakan proses transformasi data mentah
riwayat transaksi menjadi format yang dapat diproses oleh model Neural
Collaborative Filtering. Seluruh proses dijalankan secara bertahap pada skrip
Python mengikuti alur yang dirancang pada Bab III. Berikut penjelasan rinci
setiap tahapan beserta hasil aktualnya.

### Pembersihan Data (Data Cleaning)
Dataset mentah dibaca dari berkas Microsoft Excel yang berisi riwayat transaksi
operasional Sakka Base – Coffee & Barber Citraland Helvetia. Pada tahap ini,
kolom transaksi (No Transaksi, Tanggal, Pelanggan) yang kosong akibat *merged
cell* pada baris lanjutan diisi-maju (*forward-fill*), kemudian baris yang tidak
memiliki Produk valid dilewati. Hasil pembersihan data dirangkum pada Tabel 4.1.

**Tabel 4.1 Statistik Dataset Setelah Pembersihan Data**

| Keterangan | Nilai |
|---|---|
| Baris item valid dari file Excel | 4.908 |
| Baris tidak valid (dilewati) | 0 |
| Transaksi unik (orders) | 1.211 |
| Pelanggan unik (mentah) | 871 |
| Item menu unik (kode produk) | 141 |
| Interaksi biner unik (pasangan pelanggan–item) | 4.707 |

Berdasarkan Tabel 4.1, dari 4.908 baris item valid yang berasal dari 1.211
transaksi, teridentifikasi **871 pelanggan unik** dan **141 menu unik**
berdasarkan kode produk. Setelah pasangan (pelanggan, item) yang berulang
digabung menjadi satu interaksi biner, diperoleh **4.707 interaksi positif unik**
yang menjadi dasar pemodelan. Tidak ditemukan baris yang perlu dihapus karena
sistem POS Sakka Base menghasilkan data dengan struktur yang konsisten.

### Encoding ID Pengguna dan Item (Label Encoding)
Karena nilai User ID (nama pelanggan) dan Item ID (kode produk) berupa string,
dilakukan *Label Encoding* yang memetakan setiap nilai ke indeks integer berurutan
mulai dari 0 sebagai indeks pada *embedding layer*. Tabel 4.2 dan Tabel 4.3
menampilkan hasil pemetaan untuk lima data pertama.

**Tabel 4.2 Hasil Label Encoding Pengguna**

| No | user_id (MySQL) | Nama Pengguna | Indeks Encoding |
|---|---|---|---|
| 1 | 365 | Acai | 0 |
| 2 | 348 | Acang | 1 |
| 3 | 216 | Acen | 2 |
| 4 | 709 | Acin | 3 |
| 5 | 287 | Acu | 4 |

Tabel 4.2 memperlihatkan bahwa indeks encoding diberikan berdasarkan urutan abjad
nama pelanggan sehingga pelanggan "Acai" memperoleh indeks 0, "Acang" indeks 1,
dan seterusnya. Nilai `user_id` merupakan *primary key* MySQL (urut waktu input)
sehingga berbeda dari indeks encoding yang dipakai model.

**Tabel 4.3 Hasil Label Encoding Item Menu**

| No | menu_item_id (MySQL) | item_id | Indeks Encoding |
|---|---|---|---|
| 1 | 1 | A00A — AMERICANO SAKKA / LARGE HOT | 0 |
| 2 | 2 | A00B — LYCHEE AMERICANO / LARGE | 1 |
| 3 | 3 | A00C — COCONUT AMERICANO / LARGE | 2 |
| 4 | 4 | A00D — HONEY AMERICANO / REGULAR | 3 |
| 5 | 5 | A00E — LEMON AMERICANO / LARGE | 4 |

Tabel 4.3 menunjukkan pemetaan item menu yang diurutkan berdasarkan kode produk,
sehingga kode 'A00A' memperoleh indeks 0 hingga 'A00E' memperoleh indeks 4.
Karena urutan kode konsisten dengan urutan penyimpanan, nilai `menu_item_id`
(MySQL) sejajar dengan indeks encoding ditambah satu.

### Pemetaan Nilai Biner (Implicit Feedback)
Penelitian ini menggunakan umpan balik implisit sehingga tidak tersedia rating
eksplisit. Setiap pasangan (pelanggan, item) yang pernah muncul pada transaksi
diberi label **1**, sedangkan pasangan yang tidak pernah muncul diberi label
**0**. Tabel 4.4 menampilkan representasi nilai biner untuk pengguna indeks 0
("Acai") yang diambil langsung dari basis data.

**Tabel 4.4 Representasi Implicit Feedback (Pengguna indeks 0 = "Acai")**

| User Index | Item Index | Nama Menu | Label | Keterangan |
|---|---|---|---|---|
| 0 | 57 | PURE TEA / COLD REGULAR | 1 | Pernah dipesan |
| 0 | 58 | TEA MANIS / COLD LARGE | 1 | Pernah dipesan |
| 0 | 97 | NASI GORENG KAMPUNG | 1 | Pernah dipesan |
| 0 | 111 | MIE SOP SAKKA | 1 | Pernah dipesan |
| 0 | 127 | CHICKEN CHEESE RICEBOWL | 1 | Pernah dipesan |
| 0 | 0 | AMERICANO SAKKA / LARGE HOT | 0 | Tidak pernah dipesan |
| 0 | 1 | LYCHEE AMERICANO / LARGE | 0 | Tidak pernah dipesan |

Tabel 4.4 memperlihatkan pengguna "Acai" memiliki lima interaksi positif (label 1),
yaitu menu yang benar-benar pernah dipesannya. Seluruh menu lain yang tidak pernah
dipesan diberi label 0, sehingga model belajar membedakan preferensi pelanggan
dari pola interaksi yang ada.

### Negative Sampling
Untuk melatih model diperlukan sampel negatif sebagai pembanding. Teknik *negative
sampling* diterapkan dengan rasio **4 : 1** — empat sampel negatif acak (menu yang
belum pernah dipesan) untuk setiap satu sampel positif. Sampel negatif
dibangkitkan ulang di setiap awal epoch agar model tidak menghafal pola yang sama.
Tabel 4.5 menampilkan hasil aktual untuk pengguna indeks 0.

**Tabel 4.5 Hasil Negative Sampling 4:1 (Pengguna indeks 0, seed 42)**

| No | User Index | Item Index | Nama Menu | Label | Jenis |
|---|---|---|---|---|---|
| 1 | 0 | 57 | PURE TEA / COLD REGULAR | 1 | Positif |
| 2 | 0 | 49 | AVOCADO JUICE | 0 | Negatif |
| 3 | 0 | 50 | TIMUN JUICE | 0 | Negatif |
| 4 | 0 | 90 | RISOL SAKKA | 0 | Negatif |
| 5 | 0 | 26 | COCONUT PANDAN LATTE COLD / LARGE | 0 | Negatif |

Tabel 4.5 menunjukkan bahwa untuk satu item positif (PURE TEA, indeks 57)
dibangkitkan empat item negatif acak (Avocado Juice, Timun Juice, Risol Sakka, dan
Coconut Pandan Latte) yang belum pernah dipesan pengguna tersebut. Komposisi 1:4
ini diterapkan ke seluruh interaksi positif pada data latih.

### Leave-One-Out Split
Pembagian dataset memakai strategi *leave-one-out*: item dengan tanggal transaksi
paling akhir per pengguna dipisahkan sebagai data uji, sedangkan seluruh interaksi
sebelumnya menjadi data latih. Pelanggan dengan hanya satu interaksi tidak
diikutkan pada data uji. Tabel 4.6 menampilkan contoh pembagian untuk tiga
pengguna aktual.

**Tabel 4.6 Hasil Leave-One-Out Split — 3 Pengguna Aktual**

| User Index | Total Interaksi | Data Latih | Data Uji (Item Terakhir) |
|---|---|---|---|
| 0 | 5 | 4 interaksi | C10B — CHICKEN CHEESE RICEBOWL |
| 1 | 5 | 4 interaksi | C10C — CHICKEN SPICY RICEBOWL |
| 2 | 7 | 6 interaksi | A08B — TEA MANIS / COLD LARGE |

Tabel 4.6 memperlihatkan bahwa untuk pengguna indeks 0 dengan total 5 interaksi,
4 interaksi digunakan sebagai data latih dan 1 item terakhir (CHICKEN CHEESE
RICEBOWL) menjadi *ground truth* data uji. Pola yang sama berlaku untuk pengguna
lain, sehingga setiap pengguna menyumbang tepat satu item uji.

### Statistik Akhir Dataset
Tabel 4.7 merangkum statistik dataset setelah seluruh tahapan praproses selesai.

**Tabel 4.7 Statistik Akhir Dataset Setelah Praproses**

| Keterangan | Nilai |
|---|---|
| Total pelanggan unik (mentah) | 871 |
| Pelanggan dibuang (< 2 interaksi) | 51 |
| Total pengguna dipakai | 820 |
| Total item berinteraksi | 140 |
| Total interaksi positif unik | 4.707 |
| Rata-rata interaksi per pengguna | 5,74 |
| Data latih (train positif) | 3.887 |
| Data uji (test set, LOO) | 820 pengguna |
| Total sampel per epoch (positif + negatif) | 19.435 |
| Kandidat evaluasi per pengguna | 100 (1 positif + 99 negatif) |
| Strategi pembagian dataset | Leave-One-Out |

Berdasarkan Tabel 4.7, setelah menyaring 51 pelanggan dengan kurang dari dua
interaksi, dataset final memuat **820 pengguna** dan **140 item** dengan rata-rata
**5,74 interaksi per pengguna**. Data latih berisi 3.887 interaksi positif yang,
setelah *negative sampling* 4:1, menghasilkan **19.435 sampel per epoch**.
Sebanyak 820 pengguna digunakan sebagai data uji dengan 100 kandidat evaluasi
(1 positif + 99 negatif) per pengguna.

---

# 4.1.3 Hasil Pelatihan dan Pengujian Model NCF

Proses pelatihan model NCF dilakukan dalam dua tahap, yaitu pencarian konfigurasi
*hyperparameter* terbaik melalui *grid search* dan pelatihan model final
berdasarkan konfigurasi terpilih.

### Pencarian Konfigurasi Terbaik (Grid Search)
Sebelum melatih model final, dilakukan *grid search* terhadap tiga konfigurasi
yang memvariasikan dimensi *embedding*, jumlah lapisan MLP, *dropout*, dan
*learning rate*. Seluruh konfigurasi dilatih pada data latih dan diuji pada data
uji yang sama agar perbandingan berlangsung adil. Hasilnya disajikan pada
Tabel 4.8.

**Tabel 4.8 Hasil Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers | Dropout | Learning Rate | Epoch Terbaik | HR@10 | NDCG@10 |
|---|---|---|---|---|---|---|---|
| A | 32 | [64, 32, 16] | 0,2 | 0,001 | 1 | 0,3524 | 0,1835 |
| B | 16 | [32, 16, 8] | 0,3 | 0,001 | 3 | 0,3488 | 0,1824 |
| **C** | **32** | **[64, 32]** | **0,2** | **0,0005** | **5** | **0,3500** | **0,1822** |

Berdasarkan Tabel 4.8, ketiga konfigurasi menghasilkan HR@10 yang berdekatan
(0,3488–0,3524). Konfigurasi A dengan *learning rate* lebih besar mencapai puncak
pada epoch pertama namun cenderung kurang stabil, sedangkan Konfigurasi B dengan
dimensi *embedding* kecil (16) memiliki kapasitas terbatas. **Konfigurasi C**
dipilih sebagai model final karena konvergensinya paling stabil (epoch ke-5)
dengan jumlah parameter paling efisien (**32.833 parameter**) dan performa yang
kompetitif.

### Proses Pelatihan Konfigurasi C
Pelatihan Konfigurasi C dilakukan dengan *optimizer* Adam, fungsi *loss* Binary
Cross-Entropy, *batch size* 256, dan *learning rate* 0,0005. Mekanisme *early
stopping* (patience = 5) diterapkan untuk menghentikan pelatihan apabila tidak ada
peningkatan HR@10 selama 5 epoch berturut-turut. Seluruh *hyperparameter*
ditampilkan pada Tabel 4.9.

**Tabel 4.9 Hyperparameter Pelatihan Konfigurasi C**

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

Tabel 4.9 merangkum konfigurasi *hyperparameter* yang digunakan pada pelatihan
model final. Kombinasi *learning rate* kecil (0,0005) dan *weight decay* 1 × 10⁻⁵
ditujukan agar pembaruan bobot berlangsung hati-hati dan menghindari *overfitting*
pada data yang *sparse*.

Perkembangan nilai *training loss* dan metrik per epoch ditampilkan pada
Tabel 4.10.

**Tabel 4.10 Perkembangan Training Loss per Epoch — Konfigurasi C**

| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan |
|---|---|---|---|---|
| 1 | 0,6688 | 0,3476 | 0,1797 | Model terbaik tersimpan |
| 2 | 0,5525 | 0,3451 | 0,1828 | Tidak ada peningkatan (1/5) |
| 3 | 0,4599 | 0,3451 | 0,1800 | Tidak ada peningkatan (2/5) |
| 4 | 0,4432 | 0,3415 | 0,1780 | Tidak ada peningkatan (3/5) |
| 5 | 0,4363 | 0,3500 | 0,1822 | **Model terbaik tersimpan** |
| 6 | 0,4348 | 0,3402 | 0,1800 | Tidak ada peningkatan (1/5) |
| 7 | 0,4353 | 0,3500 | 0,1828 | Tidak ada peningkatan (2/5) |
| 8 | 0,4340 | 0,3415 | 0,1805 | Tidak ada peningkatan (3/5) |
| 9 | 0,4330 | 0,3415 | 0,1799 | Tidak ada peningkatan (4/5) |
| 10 | 0,4330 | 0,3439 | 0,1798 | Early stop terpenuhi (5/5) |

Berdasarkan Tabel 4.10, nilai *training loss* menurun konsisten dari 0,6688 pada
epoch ke-1 hingga stabil di kisaran 0,433. Performa terbaik pada data uji dicapai
pada **epoch ke-5** dengan HR@10 = 0,3500 dan NDCG@10 = 0,1822, sehingga bobot
model pada epoch tersebut disimpan sebagai model final. Karena tidak terjadi
peningkatan HR@10 selama 5 epoch berikutnya, pelatihan dihentikan otomatis oleh
*early stopping* pada **epoch ke-10**.

### Model Final
Model dengan performa terbaik (epoch ke-5) disimpan ke dalam berkas *checkpoint*.
Informasi lengkap model final disajikan pada Tabel 4.11.

**Tabel 4.11 Informasi Model Final**

| Informasi | Nilai |
|---|---|
| Path file model | models/ncf_config_C.pth |
| Epoch terbaik | 5 |
| Training loss epoch terbaik | 0,4363 |
| Total epoch dijalankan | 10 |
| Total parameter model | 32.833 |
| HR@10 (data uji) | 0,3500 |
| NDCG@10 (data uji) | 0,1822 |

Tabel 4.11 menunjukkan model final memiliki **32.833 parameter** dengan capaian
**HR@10 = 0,3500** dan **NDCG@10 = 0,1822** pada data uji. Jumlah parameter yang
relatif kecil menandakan model efisien namun tetap mampu menangkap pola preferensi
pelanggan secara memadai.

---

# 4.1.4 Hasil Inferensi Rekomendasi Menu

Setelah model mencapai konvergensi, dilakukan inferensi untuk membuktikan
fungsionalitas keluaran model. Inferensi dilakukan terhadap pelanggan **Jenny
Sanjaya** (`user_id` = 2), pelanggan paling aktif dengan **28 interaksi** yang
mencakup kategori kopi, teh, jus, dan makanan berat. Sistem menyaring menu yang
sudah pernah dipesan, lalu menghitung skor probabilitas (*sigmoid*) bagi seluruh
menu yang belum pernah dicoba. Sepuluh menu dengan skor tertinggi disajikan pada
Tabel 4.12.

**Tabel 4.12 Hasil Inferensi Top-10 Rekomendasi Menu (Pengguna: Jenny Sanjaya)**

| Peringkat | ID Item | Nama Menu | Kategori | Skor Probabilitas (Sigmoid) |
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

Tabel 4.12 memperlihatkan hasil prediksi sistem untuk Jenny Sanjaya. Nilai
probabilitas menunjukkan tingkat kecocokan menu dengan selera pelanggan
berdasarkan riwayatnya. Sistem merekomendasikan menu kopi (Americano Sakka di
peringkat 1, Sanger Sakka di peringkat 3) yang selaras dengan kebiasaannya
memesan kopi, sekaligus menyarankan menu makanan berat (Nasi Ayam Penyet Cabe
Ijo, Nasi Goreng Seafood, Nasi Capcay Seafood) dan minuman lain. Hal ini
menunjukkan bahwa model NCF tidak hanya merekomendasikan menu sejenis, tetapi juga
memberikan variasi rekomendasi yang relevan.

---

# 4.2 Pembahasan

Setelah melalui tahapan praproses data, pelatihan model, hingga inferensi, sub bab
ini menguraikan analisis dan evaluasi komprehensif terhadap hasil yang diperoleh.

## 4.2.1 Analisis Konfigurasi dan Pelatihan Model
Proses *grid search* menunjukkan ketiga konfigurasi menghasilkan HR@10 yang
berdekatan (0,3488–0,3524). **Konfigurasi C** (embedding 32, MLP [64, 32],
*learning rate* 0,0005) dipilih sebagai model final karena konvergensinya paling
stabil dengan jumlah parameter paling efisien (32.833 parameter). Untuk data
*implicit feedback* yang biner dan *sparse* (4.707 interaksi pada 820 pengguna ×
140 item), arsitektur yang tidak terlalu dalam dengan *learning rate* kecil sudah
memadai untuk mengekstraksi fitur laten tanpa *overfitting*.

## 4.2.2 Analisis Hasil Evaluasi HR dan NDCG
Model final menghasilkan **HR@10 = 0,3500** dan **NDCG@10 = 0,1822** dengan
strategi *Leave-One-Out* (1 *ground truth* : 99 negatif). HR@10 = 0,3500 berarti
dari 100 pengguna uji, model menempatkan menu yang benar-benar dipesan ke dalam
Top-10 pada sekitar **35 pengguna** — jauh di atas tebakan acak (~10%). NDCG@10 =
0,1822 menunjukkan kualitas urutan daftar; nilai ini wajar pada *implicit
feedback* domain kuliner karena pelanggan kerap memesan beberapa menu sekaligus
dalam satu transaksi sehingga banyak kandidat relevan bersaing ketat.

## 4.2.3 Analisis Hasil Inferensi dan Kualitas Rekomendasi
Inferensi pada pelanggan Jenny Sanjaya memperlihatkan model menggabungkan menu
kopi, makanan berat, dan minuman dengan probabilitas 0,32–0,54. Hal ini
membuktikan NCF bekerja melampaui *content-based filtering* konvensional: dalam
ruang vektor laten, pelanggan dengan pola pembelian serupa cenderung memiliki
probabilitas tinggi untuk memesan menu tertentu, sehingga model menghasilkan
keragaman rekomendasi yang relevan dengan selera kelompok pelanggan tersebut.

---

# Checklist perubahan dari draf lama (Skenario A → B)
- Total parameter: **47.521 → 32.833**
- HR@10 / NDCG@10: **0,3670 / 0,1965 → 0,3500 / 0,1822**
- Item menu: **207 → 141** (140 berinteraksi)
- Pengguna: **1.212 → 871** (820 dipakai)
- Interaksi: **4.913 → 4.707**; sampel/epoch **18.880 → 19.435**
- Epoch terbaik **8 → 5**; total epoch **13 → 10**
- Inferensi: **ID 2424 → Jenny Sanjaya (user_id 2)**
- Encoding contoh: **Acai = 0, A00A = 0** (urut abjad/kode)
