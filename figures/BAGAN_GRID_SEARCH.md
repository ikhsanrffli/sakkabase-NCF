# Bagan Alur: Grid Search → Model Final → Sistem

Diagram ini menjelaskan hubungan antara **grid search** (pemilihan konfigurasi)
dan **model final** (Tabel 4.11) yang dipakai sistem.

```mermaid
flowchart TD
    DATA["Data Latih<br/>3.887 interaksi positif"] --> GS{"GRID SEARCH<br/>menguji 3 konfigurasi"}

    GS --> A["Konfigurasi A<br/>embed 32 - MLP 64-32-16<br/>HR@10 = 0,3524<br/>puncak epoch 1 (kurang stabil)"]
    GS --> B["Konfigurasi B<br/>embed 16 - MLP 32-16-8<br/>HR@10 = 0,3488<br/>kapasitas terbatas"]
    GS --> C["Konfigurasi C<br/>embed 32 - MLP 64-32<br/>HR@10 = 0,3500<br/>puncak epoch 5 (paling stabil)"]

    C ==>|TERPILIH jadi model final| FINAL["MODEL FINAL — Tabel 4.11<br/>file: models/ncf_config_C.pth<br/>HR@10 = 0,3500 - NDCG@10 = 0,1822<br/>32.833 parameter - epoch terbaik 5"]

    FINAL ==> SYS["SISTEM REKOMENDASI<br/>Top-10 menu untuk pelanggan"]

    classDef sel fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#155724;
    classDef notsel fill:#f3f3f3,stroke:#bbbbbb,color:#888888;
    classDef final fill:#fff3cd,stroke:#c9a227,stroke-width:2px,color:#7a5c00;
    classDef sys fill:#e7f1ff,stroke:#2f6fb0,stroke-width:2px,color:#1c4f86;

    class C sel;
    class A,B notsel;
    class FINAL final;
    class SYS sys;
```

## Cara membaca
1. **Data latih** masuk ke proses **Grid Search**.
2. Grid Search **menguji 3 konfigurasi** (A, B, C) dan membandingkannya.
3. **Konfigurasi C terpilih** (hijau) karena konvergensi paling stabil — meski HR A
   sedikit lebih tinggi, A tidak stabil (puncak di epoch 1).
4. Konfigurasi C yang terpilih **menjadi Model Final** (kuning) yang
   didokumentasikan lengkap di **Tabel 4.11** dan disimpan sebagai
   `ncf_config_C.pth`.
5. Model final itulah yang dipakai **Sistem Rekomendasi** untuk menghasilkan
   Top-10 menu bagi pelanggan.

> **Inti:** Konfigurasi C di grid search = model final di Tabel 4.11 (model yang
> sama). Grid Search adalah *proses memilih*, Tabel 4.11 adalah *profil pemenang*.
