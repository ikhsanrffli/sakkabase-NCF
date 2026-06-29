# PERSIAPAN BIMBINGAN — Daftar Tanya Jawab (Preset)

> Kumpulan kemungkinan pertanyaan dosen + jawaban siap pakai. Angka kunci:
> **871 pelanggan · 141 menu · 4.908 interaksi** → praproses → **820 pengguna ·
> 140 item · 4.707 interaksi**. Model final **Konfigurasi C: HR@10 = 0,3500 ·
> NDCG@10 = 0,1822 · 32.833 parameter**.

---

## A. KONSEP & METODE (NCF)

**1. Apa itu Neural Collaborative Filtering (NCF)?**
NCF adalah metode sistem rekomendasi berbasis *deep learning* yang memodelkan
interaksi antara pengguna dan item. Setiap pengguna dan item direpresentasikan
sebagai vektor (*embedding*), lalu digabung dan diproses lewat jaringan saraf
(MLP) untuk memprediksi probabilitas seorang pengguna menyukai/memesan suatu item.

**2. Kenapa pakai NCF, bukan Collaborative Filtering biasa?**
CF konvensional (mis. *matrix factorization*) hanya menangkap hubungan **linear**
antara pengguna dan item. NCF memakai MLP sehingga mampu menangkap **pola
interaksi non-linear** yang lebih kompleks, sehingga lebih cocok untuk data
preferensi yang rumit seperti riwayat pesanan kafe.

**3. Apa beda NCF dengan Content-Based Filtering?**
Content-Based merekomendasikan berdasarkan **kemiripan konten/atribut menu**
(mis. sama-sama kopi). NCF (Collaborative) merekomendasikan berdasarkan **pola
perilaku antar-pelanggan** — "pelanggan yang mirip pola pesanannya cenderung suka
menu X". Maka NCF bisa menyarankan menu lintas kategori yang tidak mirip secara
konten.

**4. Jelaskan arsitektur model Anda.**
Embedding pengguna (32 dimensi) dan embedding item (32 dimensi) → digabung
(*concatenation*) jadi 64 → MLP [64 → 32] dengan aktivasi ReLU dan Dropout 0,2 →
lapisan output 1 neuron dengan aktivasi **sigmoid** yang menghasilkan probabilitas
0–1.

**5. Kenapa output-nya sigmoid dan loss-nya BCE?**
Karena datanya **implicit feedback biner** (1 = pernah dipesan, 0 = tidak).
Sigmoid memetakan ke probabilitas 0–1, dan *Binary Cross-Entropy* adalah fungsi
loss yang tepat untuk klasifikasi biner.

---

## B. DATASET & PRAPROSES

**6. Data berasal dari mana?**
Data primer berupa **struk riwayat transaksi** Sakka Base – Coffee & Barber
Citraland Helvetia, yang didigitalkan ke format Excel. Memuat No Transaksi,
Tanggal, Pelanggan, Produk, dan Qty.

**7. Berapa jumlah datanya?**
**4.908 baris interaksi** dari **1.211 transaksi**, melibatkan **871 pelanggan**
dan **141 menu**. Setelah praproses: **820 pengguna**, **140 item**, dan **4.707
interaksi positif unik**.

**8. Kenapa pengguna = Pelanggan, bukan Nomor Transaksi?**
Karena satu **pelanggan** merepresentasikan satu **profil preferensi** yang
konsisten. Kalau memakai nomor transaksi, satu orang yang datang 5 kali akan
dianggap 5 pengguna berbeda, sehingga pola preferensinya pecah dan tidak bisa
dipelajari. Dengan basis pelanggan, riwayat seseorang tergabung menjadi satu.

**9. Apa itu implicit feedback?**
Umpan balik yang **tidak eksplisit** (tidak ada rating bintang). Sinyal preferensi
diambil dari **tindakan** pelanggan — yaitu *memesan* suatu menu (diberi label 1).
Pasangan pelanggan–menu yang tak pernah terjadi diberi label 0.

**10. Apa tahapan preprocessing-nya?**
(1) Pembersihan data + *forward-fill*; (2) *Label Encoding* pengguna & item ke
indeks integer; (3) Pemetaan biner (implicit feedback); (4) *Negative sampling*
4:1; (5) Pembagian *Leave-One-Out*.

**11. Kenapa pelanggan dengan < 2 interaksi dibuang?**
Strategi *Leave-One-Out* menyembunyikan 1 item terakhir sebagai data uji. Kalau
pelanggan hanya punya 1 interaksi, tidak ada data latih yang tersisa untuknya.
Maka 51 pelanggan dibuang, menyisakan 820 pengguna.

**12. Apa itu negative sampling dan kenapa rasio 4:1?**
Karena data hanya berisi interaksi positif (label 1), model perlu contoh negatif
(label 0) agar bisa belajar membedakan. Untuk tiap 1 item positif diambil 4 item
acak yang belum pernah dipesan. Rasio 4:1 adalah **standar umum di literatur NCF**
— seimbang antara cukup sinyal negatif tanpa membuat data terlalu berat sebelah.

**13. Kenapa negative sampling diulang tiap epoch?**
Agar model tidak menghafal pasangan negatif yang sama; tiap epoch melihat variasi
sampel negatif yang berbeda sehingga lebih general.

---

## C. PELATIHAN & HYPERPARAMETER

**14. Kenapa memilih Konfigurasi C?**
Dari *grid search* 3 konfigurasi, ketiganya menghasilkan HR berdekatan (A=0,3524;
B=0,3488; C=0,3500). Konfigurasi C dipilih karena **konvergensi paling stabil**
dan **jumlah parameter paling efisien (32.833)** dengan performa yang setara.

**15. Apa itu learning rate dan kenapa 0,0005?**
*Learning rate* mengatur seberapa besar langkah pembaruan bobot. Nilai kecil
(0,0005) membuat pembelajaran lebih hati-hati dan stabil, menghindari melompati
titik optimal — terbukti lebih baik dibanding 0,001 pada Konfigurasi A & B.

**16. Apa itu dropout dan weight decay?**
Keduanya teknik **regularisasi** untuk mencegah *overfitting*. *Dropout* (0,2)
mematikan sebagian neuron secara acak saat latih; *weight decay* (1×10⁻⁵)
menahan bobot agar tidak terlalu besar. Cocok untuk data yang *sparse*.

**17. Apa itu early stopping?**
Menghentikan pelatihan otomatis bila tidak ada peningkatan HR@10 selama 5 epoch
berturut-turut (*patience* = 5). Mencegah *overfitting* dan menghemat waktu.
Performa terbaik dicapai epoch ke-5, pelatihan berhenti di epoch ke-10.

**18. Kenapa embedding 32 dimensi?**
Hasil *grid search*. Dimensi 32 sudah cukup menangkap fitur laten untuk ukuran
data ini; dimensi lebih kecil (16, Konfigurasi B) kapasitasnya terbatas.

**19. Optimizer apa yang dipakai?**
**Adam**, karena adaptif dan umum dipakai untuk pelatihan jaringan saraf, cocok
dipadukan dengan BCE.

---

## D. EVALUASI (HR & NDCG)

**20. Apa itu HR@10 dan NDCG@10?**
- **HR@10 (Hit Ratio):** proporsi pengguna yang item *ground truth*-nya muncul di
  Top-10. Mengukur *apakah* item relevan masuk daftar.
- **NDCG@10:** mengukur *kualitas urutan* — memberi nilai lebih tinggi bila item
  relevan ada di peringkat atas.

**21. Bagaimana cara menghitungnya? (Leave-One-Out)**
Untuk tiap pengguna uji: item terakhir disembunyikan sebagai *ground truth*, lalu
dicampur dengan 99 item negatif (total 100 kandidat). Model mengurutkan, diambil
Top-10. HR = 1 bila *ground truth* masuk Top-10. NDCG = 1/log₂(peringkat+1) bila
hit. Nilai akhir = rata-rata seluruh 820 pengguna.

**22. Kenapa 1 positif : 99 negatif?**
Ini protokol evaluasi standar untuk rekomendasi Top-N (mengikuti paper NCF asli).
Membuat pengujian **ketat** — model harus mengangkat 1 item benar di antara 100.

**23. Nilai HR 0,3500 itu bagus atau jelek?**
Cukup baik untuk konteks ini. Artinya pada ~35 dari 100 pengguna, model menebak
tepat. Karena peluang **tebakan acak hanya ~10%** (10 dari 100), capaian 35%
adalah **±3,5 kali lebih baik dari acak** — bukti model benar-benar belajar pola,
bukan menebak.

**24. (Jebakan) Kenapa HR tidak lebih tinggi, mis. di atas 0,5?**
Tiga faktor: (a) **data sparse** — rata-rata hanya 5,74 interaksi/pengguna,
sinyalnya terbatas; (b) **protokol sangat ketat** (1:99); (c) **banyak menu
relevan bersaing** karena pelanggan kerap memesan beragam menu dalam satu
transaksi. Untuk meningkatkannya dibutuhkan data lebih banyak / pendekatan hybrid
(sudah saya tulis di Saran Bab V).

**25. Kenapa NDCG (0,1822) lebih kecil dari HR (0,3500)?**
Wajar. HR hanya mengecek *apakah masuk* Top-10, sedangkan NDCG memberi penalti
bila item benar berada di peringkat bawah. Karena banyak kandidat relevan
bersaing, item target tidak selalu di peringkat 1–2, sehingga NDCG lebih rendah.

---

## E. HASIL & INTERPRETASI

**26. Apa hasil utama penelitian ini?**
Sistem rekomendasi menu berbasis NCF berhasil dibangun dan diuji dengan **HR@10 =
0,3500** dan **NDCG@10 = 0,1822**, membuktikan model mampu mempelajari preferensi
pelanggan jauh di atas tebakan acak.

**27. Tunjukkan contoh rekomendasinya bekerja.**
Pada pelanggan teraktif (Jenny Sanjaya, 28 interaksi), model merekomendasikan menu
kopi (Americano, Sanger) sesuai kebiasaannya, **sekaligus** menu makanan berat
(Nasi Ayam Penyet, Nasi Goreng Seafood) lintas kategori. Ini bukti NCF menangkap
**korelasi silang antar kategori**, bukan sekadar menu sejenis.

**28. Apa kontribusi/kebaruan penelitian Anda?**
Implementasi NCF pada **domain kafe nyata** (Sakka Base) memakai **data transaksi
implisit asli**, lengkap dengan **sistem web fungsional** yang menampilkan
evaluasi HR/NDCG secara transparan — bukan sekadar eksperimen di notebook.

---

## F. SISTEM / PROGRAM

**29. Teknologi apa yang dipakai membangun sistem?**
*Frontend* React.js; *Backend* FastAPI (Python); model PyTorch; basis data MySQL
(SQLAlchemy + PyMySQL). Praproses dengan Pandas, NumPy, Scikit-learn.

**30. Bagaimana alur sistemnya?**
Admin mengelola data (pengguna, menu, pemesanan) yang tersimpan ke MySQL → data
pemesanan menjadi *implicit feedback* → model NCF dilatih → hasil Top-10
rekomendasi ditampilkan di halaman User (Rekomendasiku) beserta metrik HR/NDCG.

**31. Kenapa login dibuat terpusat (tanpa pilih role)?**
Agar lebih praktis dan aman — sistem otomatis mendeteksi peran (Admin/User) dari
kredensial di basis data, tanpa pengguna perlu memilih manual.

**32. (Jebakan) Kalau Admin menambah data menu/pesanan baru, apakah HR berubah?**
Tidak otomatis. Model adalah hasil pelatihan yang sudah "beku", dan HR/NDCG global
(0,3500) adalah hasil evaluasi pelatihan tersebut. Data baru baru berpengaruh bila
model **dilatih ulang**. Jadi menambah data demo tidak mengubah hasil di Bab IV.

**33. Bagaimana pengguna BARU (belum punya riwayat) bisa direkomendasi?**
Memakai teknik **fold-in**: saat pengguna baru memesan beberapa menu, sistem
membentuk *embedding* sementara dari riwayat barunya (bobot item & MLP tetap),
lalu menghitung rekomendasi secara *live* tanpa melatih ulang seluruh model.

**34. Apa beda HR/NDCG di halaman Rekomendasiku dengan yang di Bab IV?**
Yang di **Bab IV (0,3500)** adalah evaluasi **global** rata-rata 820 pengguna.
Yang di **halaman Rekomendasiku** adalah evaluasi **per-akun** (1 pengguna, nilai
HR 0 atau 1) — untuk demonstrasi/pengujian individual saat sistem berjalan.

---

## G. PERTANYAAN JEBAKAN / KELEMAHAN

**35. Kenapa tidak ada pembanding (baseline)?**
Fokus penelitian ini adalah **implementasi dan pengujian NCF** pada kasus nyata.
Perbandingan dengan baseline (popularity / matrix factorization) sudah saya
cantumkan sebagai **saran pengembangan (Bab V)** untuk penelitian lanjutan.

**36. Apa keterbatasan penelitian ini?**
(a) Data terbatas & *sparse* (5,74 interaksi/pengguna); (b) hanya memakai sinyal
interaksi tanpa fitur tambahan (harga/waktu); (c) model perlu dilatih ulang untuk
mengenali menu baru; (d) belum dibandingkan dengan metode lain.

**37. Kenapa hanya pakai implicit feedback, bukan rating?**
Karena di Sakka Base tidak tersedia data rating eksplisit. Yang ada hanya riwayat
transaksi (dipesan/tidak), sehingga pendekatan *implicit feedback* paling sesuai.

**38. Apakah harga menu memengaruhi model?**
Tidak. Model murni memakai **interaksi (pelanggan–menu)**, bukan harga. Harga
hanya untuk kelengkapan tampilan/total belanja, tidak masuk ke pemodelan NCF.

**39. Bagaimana memastikan hasil ini bukan kebetulan?**
Pelatihan memakai **seed tetap (42)** sehingga **reproducible** (bisa diulang dan
menghasilkan angka sama), serta dievaluasi pada 820 pengguna dengan protokol ketat
1:99.

---

## H. PERTANYAAN UMUM PENUTUP

**40. Apa kesimpulan penelitian Anda?**
Sistem rekomendasi menu berbasis NCF berhasil dibangun dan mampu mempelajari pola
preferensi pelanggan (HR@10 = 0,3500; NDCG@10 = 0,1822), jauh di atas tebakan
acak, serta menghasilkan rekomendasi yang relevan dan bervariasi.

**41. Apa saran Anda untuk pengembangan?**
Menambah volume data, membandingkan dengan baseline, menerapkan pendekatan hybrid,
menangani *cold-start*/pelatihan berkala, dan mengintegrasikan dengan sistem kasir.

---

## TIPS SAAT BIMBINGAN
1. Kuasai **alur**: data → praproses → training → evaluasi → rekomendasi.
2. Hafal 4 angka inti: **820 pengguna, 140 item, HR 0,3500, NDCG 0,1822**.
3. Kalau ditanya hal yang belum ada (baseline, dll), jawab jujur: *"itu menjadi
   saran pengembangan, sudah saya tulis di Bab V"* — jangan mengarang.
4. Selalu kaitkan jawaban ke **tujuan**: membangun + menguji sistem rekomendasi NCF.
5. Tenang & percaya diri — kamu yang paling paham programmu sendiri. 💪
