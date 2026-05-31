"""
Konfigurasi terpusat untuk model NCF dan koneksi database.
Nilai dapat di-override via environment variable.
"""

import os

# ── Database ──────────────────────────────────────────────────────────────────

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", "3306")),
    "database": os.environ.get("DB_NAME",     "sakkabase_ncf"),
    "user":     os.environ.get("DB_USER",     "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "charset":  "utf8mb4",
}

# ── Arsitektur NCF ────────────────────────────────────────────────────────────
# Config B — hasil grid search terbaik (HR@10=0.3620, NDCG@10=0.1889)
# Dataset sparse (avg 3.1 interaksi/user) → model kapasitas kecil cukup
# MLP_LAYERS[0] harus = EMBEDDING_DIM * 2 (dimensi setelah concat)

EMBEDDING_DIM = 16
MLP_LAYERS    = [32, 16, 8]
DROPOUT       = 0.3

# ── Training ──────────────────────────────────────────────────────────────────

LR            = 0.001
WEIGHT_DECAY  = 1e-5        # L2 regularisasi di Adam optimizer
BATCH_SIZE    = 256
NUM_EPOCHS    = 50          # early stopping biasanya berhenti lebih awal
NUM_NEGATIVES = 4

# ── Early stopping ────────────────────────────────────────────────────────────

EARLY_STOPPING_PATIENCE = 5  # stop jika HR@10 tidak naik selama N epoch berturut-turut

# ── Evaluasi (leave-one-out) ──────────────────────────────────────────────────

TOP_K             = 10
NUM_TEST_NEG      = 99    # negatif di set kandidat uji (+ 1 positif = 100 total)
TRAIN_EVAL_SAMPLE = 300   # jumlah pair positif yang di-sample untuk train HR@10

# ── Path ──────────────────────────────────────────────────────────────────────

MODEL_DIR  = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "ncf_best.pth")
