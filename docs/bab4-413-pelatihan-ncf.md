# 4.1.3 Hasil Pelatihan Model Neural Collaborative Filtering (NCF)

Proses pelatihan model NCF dilakukan melalui dua tahap, yaitu pencarian konfigurasi terbaik menggunakan grid search dan pelatihan model final berdasarkan konfigurasi terpilih. Seluruh proses dijalankan menggunakan modul `ncf/grid_search.py` dan `ncf/train.py` pada perangkat lokal dengan GPU NVIDIA GeForce RTX 3050 Laptop GPU.

---

## Pencarian Konfigurasi Terbaik (Grid Search)

Grid search dijalankan terhadap tiga konfigurasi hyperparameter yang berbeda menggunakan modul `ncf/grid_search.py`. Ketiga konfigurasi menggunakan data latih dan data uji yang sama agar perbandingan berlangsung secara adil.

Tabel 4.8 menampilkan ketiga konfigurasi yang diuji beserta hasil evaluasinya pada data uji.

**Tabel 4.8 Hasil Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers   | Dropout | Learning Rate | Epoch Terbaik | HR@10  | NDCG@10 |
|-------------|-----------|--------------|---------|---------------|---------------|--------|---------|
| A           | 32        | [64, 32, 16] | 0,2     | 0,001         | 18            | 0,3312 | 0,1621  |
| **B**       | **16**    | **[32, 16, 8]** | **0,3** | **0,001**  | **22**        | **0,3620** | **0,1889** |
| C           | 32        | [64, 32]     | 0,2     | 0,0005        | 31            | 0,3408 | 0,1734  |

Konfigurasi B menghasilkan nilai HR@10 dan NDCG@10 tertinggi di antara ketiga konfigurasi, sehingga dipilih sebagai konfigurasi model final.

---

## Proses Pelatihan Konfigurasi B

Pelatihan Konfigurasi B dijalankan menggunakan optimizer Adam dengan fungsi loss Binary Cross-Entropy (BCE), batch size 256, dan learning rate 0,001. Mekanisme early stopping dengan patience = 5 menghentikan pelatihan secara otomatis apabila tidak terjadi peningkatan HR@10 pada data uji selama 5 epoch berturut-turut.

Tabel 4.9 menampilkan konfigurasi hyperparameter lengkap yang digunakan pada pelatihan Konfigurasi B.

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

Setiap epoch memproses total 18.870 sampel yang terdiri dari 3.774 sampel positif dan 15.096 sampel negatif (rasio 1:4). Sampel negatif dibangkitkan ulang secara acak di setiap awal epoch melalui fungsi `TrainDataset.resample()`.

Tabel 4.10 menampilkan perkembangan nilai training loss per epoch selama proses pelatihan berlangsung.

**Tabel 4.10 Perkembangan Training Loss per Epoch — Konfigurasi B**

| Epoch | Training Loss | Keterangan              |
|-------|---------------|-------------------------|
| 1     | 0,6823        | —                       |
| 5     | 0,5312        | —                       |
| 10    | 0,4701        | —                       |
| 15    | 0,4387        | —                       |
| 20    | 0,4201        | —                       |
| 22    | 0,4143        | Model terbaik tersimpan |
| 23    | 0,4156        | Tidak ada peningkatan (1/5) |
| 24    | 0,4171        | Tidak ada peningkatan (2/5) |
| 25    | 0,4163        | Tidak ada peningkatan (3/5) |
| 26    | 0,4180        | Tidak ada peningkatan (4/5) |
| 27    | 0,4189        | Early stop terpenuhi (5/5) |

Gambar 4.X menampilkan kurva training loss dan HR@10 selama proses pelatihan berlangsung.

**[Gambar 4.X Kurva Training Loss dan HR@10 — Konfigurasi B]**
*(Sisipkan file: `models/training_curves_Config_B.png`)*

---

## Model Final

Proses pelatihan berhenti pada epoch ke-27 karena kondisi early stopping terpenuhi. Model dengan performa terbaik pada epoch ke-22 disimpan secara otomatis ke `models/ncf_best.pth` melalui fungsi `torch.save()`.

Tabel 4.11 menampilkan informasi file model final yang tersimpan.

**Tabel 4.11 Informasi Model Final**

| Informasi                   | Nilai                  |
|-----------------------------|------------------------|
| Path file model             | `models/ncf_best.pth`  |
| Epoch terbaik               | 22                     |
| Training loss epoch terbaik | 0,4143                 |
| Total epoch dijalankan      | 27                     |
| Total parameter model       | 23.377                 |
| Ukuran file                 | ±91,3 KB               |

File checkpoint menyimpan state_dict model, mapping user2idx/item2idx, nilai n_users (1.212), n_items (207), nomor epoch, serta seluruh konfigurasi hyperparameter yang digunakan.
