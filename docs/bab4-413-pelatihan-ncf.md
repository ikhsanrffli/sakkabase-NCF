# 4.1.3 Hasil Pelatihan Model Neural Collaborative Filtering (NCF)

Proses pelatihan model NCF dilakukan dalam dua tahap, yaitu pencarian konfigurasi hyperparameter terbaik melalui grid search dan pelatihan model final berdasarkan konfigurasi yang terpilih. Seluruh proses dijalankan pada perangkat lokal dengan GPU NVIDIA GeForce RTX 3050 Laptop GPU.

---

## Pencarian Konfigurasi Terbaik (Grid Search)

Untuk menentukan kombinasi hyperparameter yang menghasilkan performa terbaik, dilakukan grid search terhadap tiga konfigurasi model yang berbeda. Ketiga konfigurasi dilatih menggunakan data latih dan data uji yang sama agar perbandingan antar konfigurasi berlangsung secara adil.

Tabel 4.8 menampilkan ketiga konfigurasi yang diuji beserta hasil evaluasinya.

**Tabel 4.8 Hasil Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers      | Dropout | Learning Rate | Epoch Terbaik | HR@10      | NDCG@10    |
|-------------|-----------|-----------------|---------|---------------|---------------|------------|------------|
| A           | 32        | [64, 32, 16]    | 0,2     | 0,001         | 18            | 0,3312     | 0,1621     |
| **B**       | **16**    | **[32, 16, 8]** | **0,3** | **0,001**     | **22**        | **0,3620** | **0,1889** |
| C           | 32        | [64, 32]        | 0,2     | 0,0005        | 31            | 0,3408     | 0,1734     |

Konfigurasi B menghasilkan nilai HR@10 dan NDCG@10 tertinggi di antara ketiga konfigurasi, sehingga dipilih sebagai konfigurasi model final yang akan digunakan pada tahap inferensi.

---

## Proses Pelatihan Konfigurasi B

Pelatihan Konfigurasi B dilakukan menggunakan optimizer Adam dengan fungsi loss Binary Cross-Entropy (BCE). Mekanisme early stopping diterapkan dengan patience = 5, yaitu pelatihan dihentikan secara otomatis apabila tidak terjadi peningkatan performa pada data uji selama 5 epoch berturut-turut. Jumlah epoch maksimum ditetapkan sebesar 50 epoch.

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

Setiap epoch memproses total 18.870 sampel yang terdiri dari 3.774 sampel positif dan 15.096 sampel negatif dengan rasio 1:4. Sampel negatif dibangkitkan ulang secara acak di setiap awal epoch sehingga model tidak menghafal pola negatif yang sama secara berulang.

Tabel 4.10 menampilkan perkembangan nilai training loss di setiap epoch selama proses pelatihan berlangsung.

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

Gambar 4.X menampilkan kurva training loss dan HR@10 selama proses pelatihan berlangsung.

**[Gambar 4.X Kurva Training Loss dan HR@10 — Konfigurasi B]**
*(Sisipkan file: `models/training_curves_Config_B.png`)*

Nilai training loss mengalami penurunan secara konsisten dari epoch ke-1 (0,6823) hingga mencapai titik terbaik pada epoch ke-22 (0,4143). Setelah epoch ke-22, nilai loss tidak menunjukkan penurunan yang berarti sehingga kondisi early stopping terpenuhi pada epoch ke-27.

---

## Model Final

Model dengan performa terbaik pada epoch ke-22 disimpan secara otomatis ke dalam file checkpoint. Tabel 4.11 menampilkan informasi lengkap model final yang tersimpan.

**Tabel 4.11 Informasi Model Final**

| Informasi                   | Nilai                  |
|-----------------------------|------------------------|
| Epoch terbaik               | 22                     |
| Training loss epoch terbaik | 0,4143                 |
| Total epoch dijalankan      | 27                     |
| Total parameter model       | 23.377                 |
| Ukuran file                 | ±91,3 KB               |

File checkpoint menyimpan bobot model, pemetaan ID pengguna dan item, serta seluruh konfigurasi hyperparameter yang digunakan selama pelatihan.
