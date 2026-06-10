"""
Modul dataset NCF:
  - Memuat interaksi dari MySQL
  - Membangun mapping user/item ID → indeks embedding
  - Split leave-one-out (item terakhir per user = data uji)
  - Dataset PyTorch dengan negative sampling runtime (4:1)
  - Kandidat uji: 1 positif + 99 negatif acak per user
"""

import random
from collections import defaultdict

import torch
from torch.utils.data import Dataset
import mysql.connector

from ncf.config import DB_CONFIG, NUM_NEGATIVES, NUM_TEST_NEG


# ── Load dari MySQL ───────────────────────────────────────────────────────────

def load_interactions() -> list[tuple]:
    """
    Ambil semua (user_id, menu_item_id, tanggal) dari tabel orders,
    diurutkan per user dan tanggal agar leave-one-out deterministik.
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    cur.execute("""
        SELECT o.user_id, od.menu_item_id, o.tanggal
        FROM   orders o
        JOIN   order_details od ON od.order_id = o.id
        ORDER  BY o.user_id, o.tanggal, o.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ── Mapping ID ────────────────────────────────────────────────────────────────

def build_mappings(rows: list[tuple]):
    """
    Petakan MySQL integer ID → indeks 0-based yang dipakai embedding layer.
    Returns: user2idx, item2idx, idx2user, idx2item
    """
    user_ids = sorted({r[0] for r in rows})
    item_ids = sorted({r[1] for r in rows})

    user2idx = {uid: i  for i,  uid in enumerate(user_ids)}
    item2idx = {iid: i  for i,  iid in enumerate(item_ids)}
    idx2user = {i:  uid for uid, i  in user2idx.items()}
    idx2item = {i:  iid for iid, i  in item2idx.items()}

    return user2idx, item2idx, idx2user, idx2item


# ── Leave-one-out split ───────────────────────────────────────────────────────

def leave_one_out_split(rows, user2idx, item2idx):
    """
    Untuk setiap user: item terakhir (berdasarkan urutan tanggal) → set uji.
    Sisa interaksi → set latih.

    Returns:
        train_data      : list of (user_idx, item_idx)
        test_data       : dict {user_idx: item_idx}
        user_item_set   : dict {user_idx: set of item_idx}  — semua interaksi
    """
    user_items = defaultdict(list)
    for uid, iid, _ in rows:
        user_items[user2idx[uid]].append(item2idx[iid])

    train_data    = []
    test_data     = {}
    user_item_set = {}

    for uidx, items in user_items.items():
        user_item_set[uidx] = set(items)
        if len(items) < 2:
            # Hanya 1 interaksi → masuk train saja, tidak dievaluasi
            train_data.extend((uidx, iidx) for iidx in items)
        else:
            test_data[uidx] = items[-1]
            train_data.extend((uidx, iidx) for iidx in items[:-1])

    return train_data, test_data, user_item_set


# ── Dataset PyTorch ───────────────────────────────────────────────────────────

class TrainDataset(Dataset):
    """
    Dataset latih dengan negative sampling (NUM_NEGATIVES negatif per positif).
    Negatif di-resample setiap awal epoch agar variasi tiap epoch.
    """

    def __init__(self, train_data, user_item_set, n_items,
                 num_neg: int = NUM_NEGATIVES):
        self.positives     = train_data
        self.user_item_set = user_item_set
        self.n_items       = n_items
        self.num_neg       = num_neg
        self.samples: list = []
        self.resample()

    def resample(self):
        """Buat ulang daftar sampel (positif + negatif baru). Panggil tiap epoch."""
        samples = []
        for uidx, iidx in self.positives:
            samples.append((uidx, iidx, 1.0))
            seen     = self.user_item_set[uidx]
            neg_count = 0
            while neg_count < self.num_neg:
                neg = random.randint(0, self.n_items - 1)
                if neg not in seen:
                    samples.append((uidx, neg, 0.0))
                    neg_count += 1
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        u, i, label = self.samples[idx]
        return (
            torch.tensor(u,     dtype=torch.long),
            torch.tensor(i,     dtype=torch.long),
            torch.tensor(label, dtype=torch.float),
        )


# ── Kandidat uji ─────────────────────────────────────────────────────────────

def build_test_candidates(test_data, user_item_set, n_items,
                          num_neg: int = NUM_TEST_NEG) -> dict:
    """
    Untuk setiap user uji: 1 item positif + num_neg negatif acak.
    Returns: {user_idx: (pos_item_idx, [neg_item_idx, ...])}
    """
    candidates = {}
    for uidx, pos_item in test_data.items():
        seen      = user_item_set[uidx]
        neg_items = []
        neg_set   = set()
        while len(neg_items) < num_neg:
            neg = random.randint(0, n_items - 1)
            if neg not in seen and neg not in neg_set:
                neg_items.append(neg)
                neg_set.add(neg)
        candidates[uidx] = (pos_item, neg_items)
    return candidates


# ── Entry point ───────────────────────────────────────────────────────────────

def get_data() -> dict:
    """Load data dari MySQL dan kembalikan semua artefak yang dibutuhkan training."""
    rows                                       = load_interactions()
    user2idx, item2idx, idx2user, idx2item     = build_mappings(rows)
    train_data, test_data, user_item_set       = leave_one_out_split(rows, user2idx, item2idx)

    n_users = len(user2idx)
    n_items = len(item2idx)

    print(f"  Users  : {n_users}")
    print(f"  Items  : {n_items}")
    print(f"  Train  : {len(train_data)} interaksi")
    print(f"  Test   : {len(test_data)} users")

    test_candidates = build_test_candidates(test_data, user_item_set, n_items)

    return {
        "n_users":         n_users,
        "n_items":         n_items,
        "train_data":      train_data,
        "test_data":       test_data,
        "test_candidates": test_candidates,
        "user_item_set":   user_item_set,
        "user2idx":        user2idx,
        "item2idx":        item2idx,
        "idx2user":        idx2user,
        "idx2item":        idx2item,
    }
