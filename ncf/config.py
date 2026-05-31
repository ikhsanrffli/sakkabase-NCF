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

EMBEDDING_DIM = 64          # dimensi embedding user & item
MLP_LAYERS    = [128, 64, 32]  # 128 = concat(user_emb, item_emb)
DROPOUT       = 0.2

# ── Training ──────────────────────────────────────────────────────────────────

LR            = 0.001
BATCH_SIZE    = 256
NUM_EPOCHS    = 20
NUM_NEGATIVES = 4           # negative sample per 1 interaksi positif

# ── Evaluasi (leave-one-out) ──────────────────────────────────────────────────

TOP_K        = 10
NUM_TEST_NEG = 99           # negatif di set kandidat uji (+ 1 positif = 100 total)

# ── Path ──────────────────────────────────────────────────────────────────────

MODEL_DIR  = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "ncf_best.pth")
