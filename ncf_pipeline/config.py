"""
config.py — Konfigurasi pipeline NCF Sakka Base (SKENARIO B: User = Pelanggan).

Bandingkan dengan config.py milik Anda. Yang WAJIB benar untuk Skenario B:
  - DATASET_PATH menunjuk ke dataset BARU
  - USER_COL = "Pelanggan"   (BUKAN "No Transaksi")
  - ITEM_BY_CODE = True       (item = kode produk, varian digabung)
  - MIN_INTERACT = 2          (filter pelanggan untuk Leave-One-Out)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# --- Sumber & keluaran ---
DATASET_PATH = os.path.join(ROOT, "src", "dataset.xlsx")
MODEL_DIR    = os.path.join(HERE, "models")
OUTPUT_DIR   = os.path.join(HERE, "outputs")

# --- Definisi data (INTI Skenario B) ---
USER_COL      = "Pelanggan"   # kolom yang dijadikan pengguna (bukan No Transaksi!)
DATE_COL      = "Tanggal"
PRODUCT_COL   = "Produk"
ITEM_BY_CODE  = True          # True: item = kode (mis. 'A00A'); False: produk+varian
MIN_INTERACT  = 2             # buang pengguna dengan interaksi unik < nilai ini

# --- Hyperparameter umum ---
SEED          = 42
WEIGHT_DECAY  = 1e-5
BATCH_SIZE    = 256
MAX_EPOCHS    = 50
NEG_TRAIN     = 4             # negatif per positif (training)
NEG_EVAL      = 99            # kandidat negatif per pengguna (evaluasi)
TOP_K         = 10
PATIENCE      = 5             # early stopping

# --- Konfigurasi arsitektur (Tabel 4.8 skripsi) ---
# layers[0] = dimensi concat (2*embed); elemen berikutnya = hidden layer.
CONFIGS = {
    "A": dict(embed=32, layers=[64, 32, 16], dropout=0.2, lr=0.001),
    "B": dict(embed=16, layers=[32, 16, 8],  dropout=0.3, lr=0.001),
    "C": dict(embed=32, layers=[64, 32],     dropout=0.2, lr=0.0005),  # final
}
FINAL_CONFIG = "C"
