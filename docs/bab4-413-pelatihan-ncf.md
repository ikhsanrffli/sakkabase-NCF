# 4.1.3 Hasil Pelatihan Model Neural Collaborative Filtering (NCF)

Pelatihan model NCF dilakukan menggunakan modul `ncf/train.py` dan `ncf/grid_search.py`. Sebelum pelatihan final, dilakukan pencarian konfigurasi terbaik melalui grid search terhadap tiga konfigurasi model yang berbeda. Seluruh konfigurasi dilatih menggunakan data yang sama agar perbandingan hasil berjalan secara adil.

---

## Arsitektur Model NCF

Model NCF terdiri dari dua lapisan embedding dan tiga lapisan fully connected (MLP). User embedding memetakan ID pengguna ke vektor berdimensi 16, dan item embedding memetakan ID item ke vektor berdimensi 16. Kedua vektor tersebut digabungkan (concatenate) menjadi vektor berdimensi 32, kemudian diproses oleh MLP untuk menghasilkan skor prediksi interaksi. Kelas NCF didefinisikan pada modul `ncf/model.py` dengan inisialisasi bobot distribusi normal (std=0.01) untuk lapisan embedding dan Xavier Uniform untuk lapisan linear.

Tabel 4.8 menampilkan rincian arsitektur model NCF Konfigurasi B yang digunakan sebagai model final.

**Tabel 4.8 Arsitektur Model NCF Konfigurasi B**

| Lapisan       | Dimensi Input     | Dimensi Output | Aktivasi | Jumlah Parameter |
|---------------|-------------------|----------------|----------|------------------|
| User Embedding | 1.212 pengguna    | 16             | —        | 19.392           |
| Item Embedding | 207 item          | 16             | —        | 3.312            |
| Concatenate   | 16 + 16           | 32             | —        | 0                |
| FC Layer 1    | 32                | 16             | ReLU     | 528              |
| FC Layer 2    | 16                | 8              | ReLU     | 136              |
| Output Layer  | 8                 | 1              | Sigmoid  | 9                |
| **Total**     |                   |                |          | **23.377**       |

---

## Konfigurasi Pelatihan

Pelatihan model menggunakan optimizer Adam dengan fungsi loss Binary Cross-Entropy (BCE). Mekanisme early stopping menghentikan pelatihan secara otomatis apabila tidak terjadi peningkatan performa pada data uji selama 5 epoch berturut-turut (patience = 5).

Tabel 4.9 menampilkan seluruh hyperparameter yang digunakan dalam proses pelatihan.

**Tabel 4.9 Hyperparameter Pelatihan Model NCF**

| Parameter                        | Nilai                         |
|----------------------------------|-------------------------------|
| Dimensi Embedding (embed_dim)    | 16                            |
| Lapisan MLP (mlp_layers)         | [32, 16, 8]                   |
| Dropout                          | 0,3                           |
| Learning Rate (lr)               | 0,001                         |
| Weight Decay                     | 1 × 10⁻⁵                     |
| Batch Size                       | 256                           |
| Jumlah Epoch Maksimum            | 50                            |
| Negative Sampling (per positif)  | 4                             |
| Early Stopping Patience          | 5                             |
| Optimizer                        | Adam                          |
| Loss Function                    | Binary Cross-Entropy (BCE)    |

---

## Pencarian Konfigurasi Terbaik (Grid Search)

Untuk menentukan konfigurasi model yang optimal, dilakukan grid search terhadap tiga konfigurasi berbeda menggunakan modul `ncf/grid_search.py`. Ketiga konfigurasi memvariasikan dimensi embedding, jumlah lapisan MLP, nilai dropout, dan learning rate.

Tabel 4.10 menampilkan ketiga konfigurasi yang diuji dalam proses grid search.

**Tabel 4.10 Konfigurasi Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers   | Dropout | Learning Rate | Weight Decay |
|-------------|-----------|--------------|---------|---------------|--------------|
| A           | 32        | [64, 32, 16] | 0,2     | 0,001         | 1 × 10⁻⁵    |
| **B**       | **16**    | **[32, 16, 8]** | **0,3** | **0,001** | **1 × 10⁻⁵** |
| C           | 32        | [64, 32]     | 0,2     | 0,0005        | 1 × 10⁻⁵    |

Berdasarkan hasil evaluasi pada data uji, Konfigurasi B menghasilkan performa tertinggi dan dipilih sebagai konfigurasi model final. Rincian hasil evaluasi masing-masing konfigurasi dibahas pada subbab 4.1.5.

---

## Proses Pelatihan

Pelatihan Konfigurasi B dijalankan melalui fungsi `train()` pada modul `ncf/train.py` menggunakan perangkat GPU (NVIDIA GeForce RTX 3050 Laptop GPU). Setiap epoch, fungsi `TrainDataset.resample()` membangkitkan ulang sampel negatif secara acak sehingga model mendapatkan variasi negatif yang berbeda di setiap iterasi.

Jumlah sampel yang diproses per epoch:

| Jenis Sampel   | Jumlah    |
|----------------|-----------|
| Sampel positif | 3.774     |
| Sampel negatif (4:1) | 15.096 |
| **Total per epoch** | **18.870** |

Tabel 4.11 menampilkan perkembangan nilai training loss per epoch selama proses pelatihan Konfigurasi B berlangsung.

**Tabel 4.11 Perkembangan Training Loss per Epoch — Konfigurasi B**

| Epoch | Training Loss | Keterangan         |
|-------|---------------|--------------------|
| 1     | 0,6823        | —                  |
| 5     | 0,5312        | —                  |
| 10    | 0,4701        | —                  |
| 15    | 0,4387        | —                  |
| 20    | 0,4201        | —                  |
| 22    | 0,4143        | Model terbaik tersimpan |
| 23    | 0,4156        | Tidak ada peningkatan (1) |
| 24    | 0,4171        | Tidak ada peningkatan (2) |
| 25    | 0,4163        | Tidak ada peningkatan (3) |
| 26    | 0,4180        | Tidak ada peningkatan (4) |
| 27    | 0,4189        | Early stop terpenuhi (5) |

Gambar 4.X menampilkan kurva training loss selama proses pelatihan berlangsung.

**[Gambar 4.X Kurva Training Loss Konfigurasi B]**
*(Sisipkan file: models/training_curves_Config_B.png)*

Proses pelatihan berhenti secara otomatis pada epoch ke-27 karena kondisi early stopping terpenuhi (tidak ada peningkatan performa selama 5 epoch berturut-turut). Model dengan performa terbaik pada epoch ke-22 disimpan secara otomatis ke `models/ncf_best.pth` melalui fungsi `torch.save()`.

Tabel 4.12 menampilkan informasi file model final yang tersimpan.

**Tabel 4.12 Informasi Model Final yang Tersimpan**

| Informasi                  | Nilai                          |
|----------------------------|--------------------------------|
| Path file model            | `models/ncf_best.pth`          |
| Epoch terbaik              | 22                             |
| Training loss epoch terbaik | 0,4143                        |
| Total epoch dijalankan     | 27                             |
| Total parameter model      | 23.377                         |
| Estimasi ukuran file       | ±91,3 KB                       |
| Format penyimpanan         | PyTorch checkpoint (`.pth`)    |

File checkpoint menyimpan: state_dict model, mapping user2idx/item2idx, n_users, n_items, epoch, dan konfigurasi hyperparameter yang digunakan.
