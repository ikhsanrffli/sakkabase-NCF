# BAB V — KESIMPULAN DAN SARAN

> Disusun berdasarkan isi skripsi (Tujuan, Rumusan Masalah, dan hasil Bab IV).
> Angka mengikuti hasil aktual Skenario B: 871 pelanggan, 141 menu, 4.908
> interaksi (820 pengguna & 140 item setelah praproses), model final
> Konfigurasi C dengan HR@10 = 0,3500 dan NDCG@10 = 0,1822. Siap tempel ke Word.

---

## BAB V
## KESIMPULAN DAN SARAN

### 5.1 Kesimpulan

Berdasarkan hasil penelitian dan pembahasan mengenai implementasi metode *Neural
Collaborative Filtering* (NCF) pada sistem rekomendasi menu di Sakka Base – Coffee
& Barber Citraland Helvetia, dapat ditarik kesimpulan sebagai berikut:

1. Penelitian ini berhasil membangun sebuah sistem rekomendasi menu berbasis
   *Neural Collaborative Filtering* dalam bentuk aplikasi web. Sistem memanfaatkan
   **umpan balik implisit (implicit feedback)** yang bersumber dari data riwayat
   transaksi pelanggan, yaitu **4.908 baris interaksi** dari **1.211 transaksi**
   yang melibatkan **871 pelanggan** dan **141 menu**. Setelah melalui tahapan
   praproses (pembersihan data, *label encoding*, pemetaan nilai biner, *negative
   sampling* 4:1, dan pembagian *Leave-One-Out*), diperoleh **820 pengguna** dan
   **140 item** dengan **4.707 interaksi positif unik** yang digunakan untuk
   melatih model. Dengan demikian, tujuan penelitian untuk membangun sistem
   rekomendasi menu menggunakan metode NCF berdasarkan data riwayat pemesanan
   telah tercapai.

2. Melalui proses *grid search* terhadap tiga konfigurasi, **Konfigurasi C**
   (dimensi *embedding* 32, lapisan MLP [64, 32], *dropout* 0,2, dan *learning
   rate* 0,0005) terpilih sebagai model final karena memiliki konvergensi paling
   stabil dengan jumlah parameter paling efisien, yaitu **32.833 parameter**.
   Model final dilatih menggunakan *optimizer* Adam, fungsi *loss* *Binary
   Cross-Entropy*, dan mekanisme *early stopping*, dengan performa terbaik dicapai
   pada **epoch ke-5**.

3. Pengujian performa model menggunakan strategi **Leave-One-Out** (1 item
   *ground truth* berbanding 99 item negatif) menghasilkan nilai **HR@10 sebesar
   0,3500** dan **NDCG@10 sebesar 0,1822**. Nilai HR@10 sebesar 0,3500 berarti
   model mampu menempatkan menu yang benar-benar dipesan ke dalam daftar Top-10
   rekomendasi pada sekitar **35 dari 100 pengguna** yang diuji. Capaian ini
   secara signifikan berada **jauh di atas probabilitas tebakan acak (±10%)**,
   sehingga membuktikan bahwa model NCF berhasil mempelajari pola preferensi
   pelanggan dari data interaksi historis. Dengan demikian, tujuan penelitian
   untuk menguji performa model menggunakan metrik HR dan NDCG telah tercapai.

4. Hasil inferensi menunjukkan bahwa model NCF tidak hanya merekomendasikan menu
   yang sejenis dengan riwayat pelanggan, tetapi juga mampu menangkap **korelasi
   silang antar kategori menu**. Pengujian terhadap pelanggan teraktif (Jenny
   Sanjaya) memperlihatkan model menggabungkan rekomendasi menu kopi, makanan
   berat, dan minuman dengan rentang skor probabilitas 0,32–0,54, sehingga
   menghasilkan keragaman rekomendasi yang tetap relevan dengan selera pelanggan.

5. Sistem yang dibangun telah berfungsi secara menyeluruh sebagai sarana
   eksperimen, mencakup antarmuka otentikasi terpusat, manajemen data (pengguna,
   menu, dan pemesanan) yang terhubung ke basis data MySQL, serta halaman
   rekomendasi yang menampilkan Top-10 menu beserta metrik evaluasi HR@10 dan
   NDCG@10 secara transparan kepada pengguna.

### 5.2 Saran

Berdasarkan keterbatasan yang ditemukan selama penelitian, beberapa saran yang
dapat dipertimbangkan untuk pengembangan selanjutnya adalah sebagai berikut:

1. **Menambah volume dan rentang waktu data.** Capaian HR@10 dan NDCG@10 masih
   dapat ditingkatkan dengan menambah jumlah serta periode data transaksi.
   Karakteristik data yang *sparse* (rata-rata hanya 5,74 interaksi per pengguna)
   menjadi salah satu faktor pembatas performa, sehingga data yang lebih banyak
   diharapkan membantu model mengenali pola preferensi secara lebih akurat.

2. **Membandingkan dengan metode lain (baseline).** Penelitian selanjutnya
   disarankan membandingkan performa NCF dengan metode pembanding seperti
   rekomendasi berbasis popularitas (*popularity-based*) atau *Matrix
   Factorization*, agar keunggulan NCF dapat dibuktikan secara empiris.

3. **Menerapkan pendekatan hybrid dan penambahan fitur.** Performa rekomendasi
   berpotensi ditingkatkan dengan memadukan NCF dan *Content-Based Filtering*
   (*hybrid*), atau dengan menambahkan fitur tambahan seperti kategori, harga, dan
   waktu pemesanan, sehingga model memiliki informasi yang lebih kaya dalam
   memprediksi preferensi pelanggan.

4. **Penanganan menu baru (cold-start) dan pelatihan berkala.** Karena model hanya
   mengenali item yang ada pada saat pelatihan, disarankan menambahkan mekanisme
   pelatihan ulang (*retraining*) secara berkala agar menu-menu baru dapat ikut
   direkomendasikan, serta mengembangkan penanganan *cold-start* yang lebih lanjut
   bagi pengguna maupun item yang belum memiliki riwayat interaksi.

5. **Integrasi dengan sistem operasional kafe.** Untuk pemanfaatan nyata, sistem
   dapat dikembangkan agar terintegrasi langsung dengan sistem kasir/POS Sakka
   Base, sehingga data transaksi terbaru dapat langsung dimanfaatkan dan
   rekomendasi dapat diperbarui secara berkelanjutan.
