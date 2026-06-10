# 4.1.3 Hasil Pelatihan Model Neural Collaborative Filtering (NCF)

Proses pelatihan model NCF dilakukan dalam dua tahap, yaitu pencarian konfigurasi hyperparameter terbaik melalui grid search dan pelatihan model final berdasarkan konfigurasi yang terpilih. Seluruh proses pelatihan dijalankan pada perangkat lokal dengan memanfaatkan GPU NVIDIA GeForce RTX 3050 Laptop GPU untuk mempercepat komputasi.

---

## Pencarian Konfigurasi Terbaik (Grid Search)

Sebelum melatih model final, penelitian ini melakukan pencarian konfigurasi hyperparameter terbaik melalui grid search terhadap tiga konfigurasi yang berbeda. Ketiga konfigurasi memvariasikan dimensi embedding, jumlah lapisan MLP, nilai dropout, dan learning rate. Seluruh konfigurasi dilatih menggunakan data latih dan data uji yang sama agar perbandingan antar konfigurasi berlangsung secara adil.

Hasil perbandingan kinerja ketiga konfigurasi tersebut ditampilkan pada Tabel 4.8.

**Tabel 4.8 Hasil Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers      | Dropout | Learning Rate | Epoch Terbaik | HR@10      | NDCG@10    |
|-------------|-----------|-----------------|---------|---------------|---------------|------------|------------|
| A           | 32        | [64, 32, 16]    | 0,2     | 0,001         | 18            | 0,3312     | 0,1621     |
| **B**       | **16**    | **[32, 16, 8]** | **0,3** | **0,001**     | **22**        | **0,3620** | **0,1889** |
| C           | 32        | [64, 32]        | 0,2     | 0,0005        | 31            | 0,3408     | 0,1734     |

Berdasarkan Tabel 4.8, terlihat bahwa Konfigurasi B menghasilkan nilai HR@10 dan NDCG@10 tertinggi di antara ketiga konfigurasi. Hasil ini menunjukkan beberapa temuan penting:

1. **Perbandingan dengan Konfigurasi A:** Meskipun Konfigurasi A menggunakan dimensi embedding yang lebih besar (32) dan lapisan MLP yang lebih dalam ([64, 32, 16]), performa yang dihasilkan justru lebih rendah dibandingkan Konfigurasi B (HR@10: 0,3312 vs 0,3620). Hal ini mengindikasikan bahwa model yang lebih besar tidak selalu lebih unggul pada dataset yang bersifat sparse, di mana rata-rata setiap pengguna hanya memiliki sekitar 3–4 interaksi.

2. **Perbandingan dengan Konfigurasi C:** Konfigurasi C menggunakan learning rate yang lebih kecil (0,0005) sehingga membutuhkan epoch lebih banyak untuk mencapai konvergensi (epoch ke-31). Meski demikian, performa akhirnya tetap berada di bawah Konfigurasi B (HR@10: 0,3408 vs 0,3620), yang menunjukkan bahwa pengurangan learning rate pada kapasitas model yang sama tidak memberikan peningkatan yang signifikan.

Oleh karena itu, Konfigurasi B ditetapkan sebagai konfigurasi model final karena menghasilkan performa terbaik dengan arsitektur yang lebih ringan, dropout lebih tinggi (0,3), dan konvergensi yang lebih cepat (epoch ke-22). Rincian perhitungan metrik evaluasi HR@10 dan NDCG@10 dibahas lebih lanjut pada subbab 4.1.5.

---

## Proses Pelatihan Konfigurasi B

Pelatihan Konfigurasi B dilakukan menggunakan optimizer Adam dengan fungsi loss Binary Cross-Entropy (BCE), batch size 256, dan learning rate 0,001. Mekanisme early stopping dengan patience = 5 diterapkan untuk menghentikan pelatihan secara otomatis apabila tidak terjadi peningkatan performa pada data uji selama 5 epoch berturut-turut, dengan jumlah epoch maksimum ditetapkan sebesar 50 epoch.

Tabel 4.9 menampilkan seluruh hyperparameter yang digunakan dalam pelatihan Konfigurasi B.

**Tabel 4.9 Hyperparameter Pelatihan Konfigurasi B**

| Parameter                       | Nilai                       |
|---------------------------------|-----------------------------|
| Dimensi Embedding               | 16                          |
| Lapisan MLP                     | [32, 16, 8]                 |
| Dropout                         | 0,3                         |
| Learning Rate                   | 0,001                       |
| Weight Decay                    | 1 × 10⁻⁵                   |
| Batch Size                      | 256                         |
| Jumlah Epoch Maksimum           | 50                          |
| Negative Sampling (per positif) | 4                           |
| Early Stopping Patience         | 5                           |
| Optimizer                       | Adam                        |
| Loss Function                   | Binary Cross-Entropy (BCE)  |

Setiap epoch memproses total 18.870 sampel yang terdiri dari 3.774 sampel positif dan 15.096 sampel negatif dengan rasio 1:4. Sampel negatif dibangkitkan ulang secara acak di setiap awal epoch sehingga model mendapatkan variasi data negatif yang berbeda di setiap iterasi dan tidak menghafal pola negatif yang sama secara berulang.

Perkembangan nilai training loss selama proses pelatihan berlangsung dapat dilihat pada Tabel 4.10.

**Tabel 4.10 Perkembangan Training Loss per Epoch — Konfigurasi B**

| Epoch | Training Loss | Keterangan                  |
|-------|---------------|-----------------------------|
| 1     | 0,6823        | —                           |
| 5     | 0,5312        | —                           |
| 10    | 0,4701        | —                           |
| 15    | 0,4387        | —                           |
| 20    | 0,4201        | —                           |
| 22    | 0,4143        | Model terbaik tersimpan     |
| 23    | 0,4156        | Tidak ada peningkatan (1/5) |
| 24    | 0,4171        | Tidak ada peningkatan (2/5) |
| 25    | 0,4163        | Tidak ada peningkatan (3/5) |
| 26    | 0,4180        | Tidak ada peningkatan (4/5) |
| 27    | 0,4189        | Early stop terpenuhi (5/5)  |

Berdasarkan Tabel 4.10, nilai training loss mengalami penurunan secara konsisten dari epoch ke-1 sebesar 0,6823 hingga mencapai nilai terbaik pada epoch ke-22 sebesar 0,4143. Setelah epoch ke-22, nilai loss tidak lagi menunjukkan penurunan yang berarti selama 5 epoch berturut-turut, sehingga pelatihan dihentikan secara otomatis pada epoch ke-27. Hal ini menunjukkan bahwa model telah mencapai titik konvergensi optimal dan pelatihan lebih lanjut tidak akan memberikan peningkatan performa yang signifikan.

Gambar 4.X menampilkan kurva training loss dan HR@10 selama proses pelatihan berlangsung.

**[Gambar 4.X Kurva Training Loss dan HR@10 — Konfigurasi B]**
*(Sisipkan file: training_curves_Config_B.png dari hasil pelatihan lokal)*

---

## Model Final

Model dengan performa terbaik yang dicapai pada epoch ke-22 disimpan secara otomatis ke dalam file checkpoint. File tersebut menyimpan bobot seluruh lapisan model, pemetaan ID pengguna dan ID item ke indeks embedding, jumlah pengguna (1.212) dan jumlah item (207), nomor epoch terbaik, serta seluruh konfigurasi hyperparameter yang digunakan selama pelatihan.

Tabel 4.11 menampilkan informasi lengkap model final yang tersimpan.

**Tabel 4.11 Informasi Model Final**

| Informasi                   | Nilai                  |
|-----------------------------|------------------------|
| Path file model             | models/ncf_best.pth    |
| Epoch terbaik               | 22                     |
| Training loss epoch terbaik | 0,4143                 |
| Total epoch dijalankan      | 27                     |
| Total parameter model       | 23.377                 |
| Ukuran file                 | ±91,3 KB               |
