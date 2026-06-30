# Narasi Lengkap BAB IV — Skenario B (siap copy-paste ke Word)

Teks paragraf utuh gaya skripsi. Tabel & gambar mengacu ke
`PANDUAN_BAB4_SkenarioB.md`. Tinggal tempel paragraf ini ke dokumen Anda.

---

## 4.1.2 Hasil Preprocessing Data

Tahap praproses (preprocessing) merupakan proses transformasi data mentah riwayat
transaksi menjadi format yang dapat diproses oleh model Neural Collaborative
Filtering. Seluruh proses dilakukan secara bertahap di dalam skrip Python pada
modul `dataset.py`, mengikuti alur pembersihan data, pengkodean, pemetaan umpan
balik biner, negative sampling, hingga pembagian dataset.

**Pembersihan Data (Data Cleaning).**
Dataset mentah diperoleh dari file Microsoft Excel (`dataset.xlsx`) yang berisi
riwayat transaksi operasional Sakka Base – Coffee & Barber Citraland Helvetia, dan
dibaca menggunakan library openpyxl. Pada sumber data, satu transaksi dapat memuat
beberapa baris menu di mana kolom Nomor Transaksi, Tanggal, dan Pelanggan hanya
terisi pada baris pertama (sel tergabung). Oleh karena itu sistem melakukan
pengisian maju (forward-fill) sehingga setiap baris produk memiliki identitas
pelanggan dan tanggal yang lengkap. Baris yang tidak memiliki kolom Produk yang
valid dihapus, dan nilai kuantitas yang tidak dapat dikonversi ke bilangan bulat
positif diganti dengan nilai default 1. Proses ini menghasilkan 4.908 baris item
valid yang berasal dari 1.211 nomor transaksi unik, mencakup 871 pelanggan unik
dan 141 menu unik. Statistik dataset setelah pembersihan ditampilkan pada Tabel 4.1.

**Encoding ID Pengguna dan Item (Label Encoding).**
Karena nilai User ID berupa nama pelanggan (string) dan Item ID berupa kode menu
dari aplikasi POS, dilakukan Label Encoding untuk memetakan setiap ID ke indeks
integer berurutan mulai dari 0. Identitas pelanggan diurutkan secara alfabetis,
sehingga misalnya pelanggan "Acai" dipetakan ke indeks 0, "Acang" ke indeks 1, dan
seterusnya. Item menu dipetakan berdasarkan kode, misalnya "A00A" ke indeks 0.
Proses encoding ini memungkinkan model embedding pada NCF merepresentasikan setiap
pengguna dan item sebagai vektor numerik. Hasil pengkodean ditampilkan pada Tabel
4.2 dan Tabel 4.3.

**Pemetaan Nilai Biner (Implicit Feedback).**
Penelitian ini menggunakan data umpan balik implisit (implicit feedback) sehingga
tidak tersedia data rating eksplisit dari pelanggan. Setiap pasangan pelanggan–menu
yang pernah berinteraksi (menu pernah dipesan) dikodekan sebagai nilai 1, sedangkan
pasangan yang tidak pernah berinteraksi dikodekan sebagai nilai 0. Pembelian
berulang menu yang sama oleh pelanggan yang sama digabung menjadi satu interaksi
positif agar sesuai dengan formulasi NCF untuk data implisit. Tabel 4.4 menampilkan
contoh representasi nilai biner pada pengguna indeks 0 (pelanggan Acai), yang
memiliki lima interaksi positif.

**Negative Sampling.**
Untuk melatih model diperlukan data negatif sebagai pembanding, yaitu menu yang
tidak pernah dipesan oleh pengguna. Teknik negative sampling diterapkan dengan
rasio 4:1 — empat sampel negatif untuk setiap satu sampel positif. Sampel negatif
dibangkitkan ulang secara acak pada setiap awal epoch sehingga model memperoleh
variasi data negatif yang berbeda di setiap iterasi dan tidak menghafal pola
negatif yang sama. Tabel 4.5 menampilkan contoh hasil negative sampling untuk
pengguna indeks 0.

**Leave-One-Out Split.**
Pembagian dataset dilakukan menggunakan strategi leave-one-out. Untuk setiap
pengguna, satu interaksi dengan tanggal transaksi paling akhir dipisahkan sebagai
data uji, sedangkan seluruh interaksi sebelumnya digunakan sebagai data latih.
Strategi ini dipilih karena mampu mensimulasikan kondisi nyata, yaitu memprediksi
menu berikutnya berdasarkan riwayat sebelumnya. Tabel 4.6 menampilkan hasil
pembagian leave-one-out untuk tiga pengguna aktual.

Untuk keperluan evaluasi, setiap pengguna pada data uji diberikan 100 item kandidat
yang terdiri dari 1 item positif (ground truth) dan 99 item negatif acak. Pengguna
dengan kurang dari dua interaksi tidak dapat dievaluasi dengan leave-one-out
sehingga disaring; dari 871 pelanggan, sebanyak 51 pelanggan dengan satu interaksi
dibuang, menyisakan 820 pengguna. Statistik akhir dataset setelah seluruh tahapan
praproses dirangkum pada Tabel 4.7.

---

## 4.1.3 Hasil Pelatihan dan Pengujian Model NCF

Proses pelatihan model NCF dilakukan dalam dua tahap, yaitu pencarian konfigurasi
hyperparameter terbaik melalui grid search dan pelatihan model final berdasarkan
konfigurasi yang terpilih.

**Pencarian Konfigurasi Terbaik (Grid Search).**
Sebelum melatih model final, dilakukan pencarian konfigurasi hyperparameter melalui
grid search terhadap tiga konfigurasi yang memvariasikan dimensi embedding, jumlah
lapisan MLP, dropout, dan learning rate. Hasil perbandingan ditampilkan pada Tabel
4.8. Ketiga konfigurasi menghasilkan HR@10 yang sangat berdekatan (selisih ±0,003),
sehingga secara statistik dapat dianggap setara. Konfigurasi A dengan learning rate
lebih besar (0,001) cepat mencapai puncak pada epoch awal kemudian mengalami
plateau, sedangkan Konfigurasi C dengan learning rate lebih kecil (0,0005)
menunjukkan konvergensi yang lebih stabil. Karena performa setara
namun Konfigurasi C memiliki arsitektur paling sederhana (lapisan MLP [64, 32]
dengan 32.833 parameter) dan konvergensi paling stabil, Konfigurasi C ditetapkan
sebagai konfigurasi model final.

**Proses Pelatihan Konfigurasi C.**
Pelatihan Konfigurasi C dilakukan menggunakan optimizer Adam dengan fungsi loss
Binary Cross-Entropy (BCE), batch size 256, dan learning rate 0,0005. Mekanisme
early stopping dengan patience = 5 diterapkan untuk menghentikan pelatihan secara
otomatis ketika tidak ada peningkatan performa. Seluruh hyperparameter ditampilkan
pada Tabel 4.9. Setiap epoch memproses total 19.435 sampel yang terdiri dari 3.887
sampel positif dan 15.548 sampel negatif dengan rasio 1:4. Perkembangan nilai
training loss dan metrik per epoch dapat dilihat pada Tabel 4.10. Nilai training
loss menurun secara konsisten dari 0,6687 pada epoch pertama hingga mencapai
performa terbaik pada epoch ke-2 dengan loss 0,5536, kemudian pelatihan dihentikan
oleh early stopping pada epoch ke-7. Kurva training loss dan HR@10 selama
pelatihan ditampilkan pada Gambar 4.1.

**Model Final.**
Model dengan performa terbaik yang dicapai pada epoch ke-2 disimpan secara otomatis
ke dalam file checkpoint. File tersebut menyimpan bobot seluruh lapisan model,
pemetaan ID pengguna dan item ke indeks embedding, jumlah pengguna (820), serta
jumlah item (140). Informasi lengkap model final ditampilkan pada Tabel 4.11.
Evaluasi pada data uji menghasilkan HR@10 sebesar 0,3439 dan NDCG@10 sebesar 0,1825.

---

## 4.1.4 Hasil Inferensi Rekomendasi Menu

Tahapan inferensi dilakukan setelah model Neural Collaborative Filtering selesai
dilatih dan mencapai konvergensi optimal. Sebagai pembuktian fungsionalitas keluaran
model, dilakukan penarikan data inferensi terhadap pelanggan Jenny Sanjaya, yang
tercatat sebagai salah satu pelanggan paling aktif dengan riwayat 28 menu beragam
lintas kategori — mulai dari kopi (Honey Americano, Cafe Latte, Aren Latte), jus
(Mango Juice, Tomato Juice), nasi (Nasi Goreng Special, Nasi Ayam Bakar), pasta
(Fettucini Carbonara), hingga chicken steak. Riwayat pemesanan pengguna tersebut
ditampilkan pada Gambar 4.2.

Sistem kemudian memasukkan sisa kandidat menu yang belum pernah dipesan oleh
pengguna ke dalam model NCF untuk dihitung skor probabilitasnya menggunakan fungsi
aktivasi sigmoid pada lapisan output. Hasil inferensi sepuluh menu teratas
ditampilkan pada Tabel 4.12. Sistem merekomendasikan menu Americano Sakka dengan
skor tertinggi (0,5413), diikuti Nasi Ayam Penyet Cabe Ijo dan Sanger Sakka. Daftar
ini menunjukkan model mampu menangkap preferensi lintas kategori: merekomendasikan
kopi sesuai kebiasaan ngopi pelanggan, sekaligus menu nasi dan minuman yang selaras
dengan pola konsumsi makanannya.

---

## 4.2 Pembahasan

### 4.2.1 Analisis Konfigurasi dan Pelatihan Model

Proses pencarian hyperparameter (grid search) menunjukkan bahwa Konfigurasi C
(dimensi embedding 32, lapisan MLP [64, 32], dropout 0,2, dan learning rate 0,0005)
merupakan arsitektur yang paling sesuai untuk data penelitian ini. Pertama, learning
rate yang lebih kecil (0,0005) pada Konfigurasi C menghasilkan konvergensi yang
lebih stabil dibandingkan learning rate 0,001 pada Konfigurasi A dan B yang cepat
mencapai puncak lalu plateau. Hal ini menunjukkan bahwa optimasi bobot jaringan
untuk data implicit feedback yang relatif jarang (sparse) lebih baik dilakukan
secara bertahap. Kedua, penggunaan lapisan MLP yang tidak terlalu dalam, yaitu dua
lapisan [64, 32], sudah cukup untuk mengekstraksi fitur laten tanpa menambah
kompleksitas parameter. Dengan performa yang setara namun arsitektur paling efisien
(32.833 parameter), Konfigurasi C menjadi pilihan yang paling seimbang antara akurasi
dan kesederhanaan model.

### 4.2.2 Analisis Hasil Evaluasi Hit Ratio (HR) dan NDCG

Evaluasi model final menghasilkan nilai HR@10 sebesar 0,3439 dan NDCG@10 sebesar
0,1825. Metrik ini dihitung menggunakan strategi pengujian yang ketat, yaitu
Leave-One-Out dengan rasio 1 item ground truth berbanding 99 item negatif yang belum
pernah dilihat model. Nilai HR@10 sebesar 0,3439 mengartikan bahwa dari setiap 100
pengguna yang diuji, model berhasil menempatkan menu aktual yang benar-benar akan
dipesan ke dalam daftar Top-10 rekomendasi pada sekitar 34 pengguna. Sementara itu,
nilai NDCG@10 sebesar 0,1825 merepresentasikan kualitas urutan daftar rekomendasi,
yang memberikan penalti apabila item ground truth muncul pada posisi lebih bawah.
Nilai ini menunjukkan bahwa meskipun model mampu menempatkan item relevan dalam
Top-10, posisinya cenderung berada pada peringkat menengah. Capaian ini tergolong
baik mengingat karakteristik dataset kafe yang relatif kecil dan tersebar.

### 4.2.3 Analisis Hasil Inferensi dan Kualitas Rekomendasi

Salah satu keunggulan utama penerapan Neural Collaborative Filtering yang teramati
pada penelitian ini adalah kemampuannya menangkap korelasi silang antar kategori
menu. Berdasarkan pengujian inferensi pada pelanggan Jenny Sanjaya, model tidak
hanya merekomendasikan menu dari satu kategori yang sama dengan riwayatnya, tetapi
memadukan rekomendasi kopi, nasi, dan minuman secara bersamaan sesuai pola konsumsi
pelanggan tersebut. Hasil ini membuktikan bahwa NCF bekerja melampaui logika
Content-Based Filtering konvensional yang hanya berfokus pada kemiripan atribut item.
Model mempelajari bahwa dalam ruang vektor laten, pelanggan-pelanggan dengan pola
pembelian serupa cenderung menyukai menu yang sama, sehingga rekomendasi yang
dihasilkan lebih personal dan beragam.
