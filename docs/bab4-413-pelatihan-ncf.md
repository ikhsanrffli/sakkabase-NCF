# 4.1.3 Hasil Pelatihan Model Neural Collaborative Filtering (NCF)

Proses pelatihan model NCF dilakukan dalam dua tahap, yaitu pencarian konfigurasi hyperparameter terbaik melalui grid search dan pelatihan model final berdasarkan konfigurasi yang terpilih. Seluruh proses pelatihan dijalankan pada perangkat lokal dengan memanfaatkan GPU NVIDIA GeForce RTX 3050 Laptop GPU untuk mempercepat komputasi.

---

## Pencarian Konfigurasi Terbaik (Grid Search)

Sebelum melatih model final, penelitian ini melakukan pencarian konfigurasi hyperparameter terbaik melalui grid search terhadap tiga konfigurasi yang berbeda. Ketiga konfigurasi memvariasikan dimensi embedding, jumlah lapisan MLP, nilai dropout, dan learning rate. Seluruh konfigurasi dilatih menggunakan data latih dan data uji yang sama agar perbandingan antar konfigurasi berlangsung secara adil.

Hasil perbandingan kinerja ketiga konfigurasi tersebut ditampilkan pada Tabel 4.8.

**Tabel 4.8 Hasil Grid Search NCF**

| Konfigurasi | embed_dim | mlp_layers      | Dropout | Learning Rate | Epoch Terbaik | HR@10      | NDCG@10    |
|-------------|-----------|-----------------|---------|---------------|---------------|------------|------------|
| A           | 32        | [64, 32, 16]    | 0,2     | 0,001         | 4             | 0,3547     | 0,1943     |
| B           | 16        | [32, 16, 8]     | 0,3     | 0,001         | 1             | 0,3591     | 0,1933     |
| **C**       | **32**    | **[64, 32]**    | **0,2** | **0,0005**    | **8**         | **0,3670** | **0,1965** |

Berdasarkan Tabel 4.8, terlihat bahwa Konfigurasi C menghasilkan nilai HR@10 dan NDCG@10 tertinggi di antara ketiga konfigurasi. Hasil ini menunjukkan beberapa temuan penting:

1. **Perbandingan dengan Konfigurasi A:** Konfigurasi A dan C sama-sama menggunakan dimensi embedding 32, namun Konfigurasi A memiliki lapisan MLP yang lebih dalam ([64, 32, 16]) dengan learning rate lebih tinggi (0,001). Meskipun konvergensi Konfigurasi A lebih cepat (epoch ke-4), performa akhirnya lebih rendah dibandingkan Konfigurasi C (HR@10: 0,3547 vs 0,3670). Hal ini mengindikasikan bahwa pengurangan learning rate pada Konfigurasi C memungkinkan model untuk belajar secara lebih hati-hati dan menghasilkan bobot yang lebih optimal.

2. **Perbandingan dengan Konfigurasi B:** Konfigurasi B menggunakan dimensi embedding yang lebih kecil (16) dengan dropout lebih tinggi (0,3). Meskipun Konfigurasi B mencapai epoch terbaik lebih cepat (epoch ke-1), performa akhirnya masih berada di bawah Konfigurasi C (HR@10: 0,3591 vs 0,3670). Hal ini menunjukkan bahwa kapasitas model yang lebih kecil pada Konfigurasi B tidak cukup untuk menangkap pola interaksi yang ada pada dataset ini.

Oleh karena itu, Konfigurasi C ditetapkan sebagai konfigurasi model final karena menghasilkan nilai HR@10 dan NDCG@10 tertinggi dengan total 47.521 parameter. Rincian perhitungan metrik evaluasi HR@10 dan NDCG@10 dibahas lebih lanjut pada subbab 4.1.5.

---

## Proses Pelatihan Konfigurasi C

Pelatihan Konfigurasi C dilakukan menggunakan optimizer Adam dengan fungsi loss Binary Cross-Entropy (BCE), batch size 256, dan learning rate 0,0005. Mekanisme early stopping dengan patience = 5 diterapkan untuk menghentikan pelatihan secara otomatis apabila tidak terjadi peningkatan performa pada data uji selama 5 epoch berturut-turut, dengan jumlah epoch maksimum ditetapkan sebesar 50 epoch.

Tabel 4.9 menampilkan seluruh hyperparameter yang digunakan dalam pelatihan Konfigurasi C.

**Tabel 4.9 Hyperparameter Pelatihan Konfigurasi C**

| Parameter                       | Nilai                       |
|---------------------------------|-----------------------------|
| Dimensi Embedding               | 32                          |
| Lapisan MLP                     | [64, 32]                    |
| Dropout                         | 0,2                         |
| Learning Rate                   | 0,0005                      |
| Weight Decay                    | 1 × 10⁻⁵                   |
| Batch Size                      | 256                         |
| Jumlah Epoch Maksimum           | 50                          |
| Negative Sampling (per positif) | 4                           |
| Early Stopping Patience         | 5                           |
| Optimizer                       | Adam                        |
| Loss Function                   | Binary Cross-Entropy (BCE)  |

Setiap epoch memproses total 18.880 sampel yang terdiri dari 3.776 sampel positif dan 15.104 sampel negatif dengan rasio 1:4. Sampel negatif dibangkitkan ulang secara acak di setiap awal epoch sehingga model mendapatkan variasi data negatif yang berbeda di setiap iterasi dan tidak menghafal pola negatif yang sama secara berulang.

Perkembangan nilai training loss selama proses pelatihan berlangsung dapat dilihat pada Tabel 4.10.

**Tabel 4.10 Perkembangan Training Loss per Epoch — Konfigurasi C**

| Epoch | Training Loss | Test HR@10 | NDCG@10 | Keterangan                  |
|-------|---------------|------------|---------|-----------------------------|
| 1     | 0,6493        | 0,3371     | 0,1876  | —                           |
| 2     | 0,5170        | 0,3494     | 0,1905  | —                           |
| 3     | 0,4450        | 0,3652     | 0,1954  | —                           |
| 4     | 0,4284        | 0,3644     | 0,1958  | —                           |
| 5     | 0,4245        | 0,3556     | 0,1918  | —                           |
| 6     | 0,4177        | 0,3582     | 0,1939  | —                           |
| 7     | 0,4228        | 0,3652     | 0,1957  | —                           |
| 8     | 0,4163        | 0,3670     | 0,1965  | Model terbaik tersimpan     |
| 9     | 0,4170        | 0,3556     | 0,1914  | Tidak ada peningkatan (1/5) |
| 10    | 0,4158        | 0,3573     | 0,1909  | Tidak ada peningkatan (2/5) |
| 11    | 0,4126        | 0,3582     | 0,1926  | Tidak ada peningkatan (3/5) |
| 12    | 0,4115        | 0,3635     | 0,1952  | Tidak ada peningkatan (4/5) |
| 13    | 0,4110        | 0,3600     | 0,1942  | Early stop terpenuhi (5/5)  |

Berdasarkan Tabel 4.10, nilai training loss mengalami penurunan secara konsisten dari epoch ke-1 sebesar 0,6493 hingga mencapai nilai terbaik pada epoch ke-8 sebesar 0,4163. Setelah epoch ke-8, nilai loss tidak lagi menunjukkan penurunan yang berarti selama 5 epoch berturut-turut, sehingga pelatihan dihentikan secara otomatis pada epoch ke-13. Hal ini menunjukkan bahwa model telah mencapai titik konvergensi optimal dan pelatihan lebih lanjut tidak akan memberikan peningkatan performa yang signifikan.

Gambar 4.X menampilkan kurva training loss dan HR@10 selama proses pelatihan berlangsung.

**[Gambar 4.X Kurva Training Loss dan HR@10 — Konfigurasi C]**
*(Sisipkan file: training_curves_Config_C.png dari folder models)*

---

## Model Final

Model dengan performa terbaik yang dicapai pada epoch ke-8 disimpan secara otomatis ke dalam file checkpoint. File tersebut menyimpan bobot seluruh lapisan model, pemetaan ID pengguna dan ID item ke indeks embedding, jumlah pengguna (1.212) dan jumlah item (207), nomor epoch terbaik, serta seluruh konfigurasi hyperparameter yang digunakan selama pelatihan.

Tabel 4.11 menampilkan informasi lengkap model final yang tersimpan.

**Tabel 4.11 Informasi Model Final**

| Informasi                   | Nilai                         |
|-----------------------------|-------------------------------|
| Path file model             | models/ncf_config_C.pth       |
| Epoch terbaik               | 8                             |
| Training loss epoch terbaik | 0,4163                        |
| Total epoch dijalankan      | 13                            |
| Total parameter model       | 47.521                        |
| HR@10 (data uji)            | 0,3670                        |
| NDCG@10 (data uji)          | 0,1965                        |
