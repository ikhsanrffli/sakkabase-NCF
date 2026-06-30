"""
dataset.py — Praproses & penyiapan data NCF (SKENARIO B).

Alur (sesuai Bab 3 skripsi):
  1. Baca xlsx + forward-fill kolom transaksi
  2. Item = kode produk (varian digabung); dedupe pasangan (Pelanggan, item) -> biner
  3. Filter pengguna < MIN_INTERACT interaksi unik
  4. Label Encoding pengguna & item
  5. Split Leave-One-Out (item terbaru per pengguna jadi data uji)
  6. Siapkan negative sampler & kandidat evaluasi (1 positif + 99 negatif)

PERBEDAAN UTAMA vs versi lama: USER_COL = "Pelanggan" (bukan No Transaksi).
"""
import random
from datetime import datetime
import numpy as np
import pandas as pd
import config


def _seed():
    random.seed(config.SEED); np.random.seed(config.SEED)


def load_interactions(path=None):
    """Kembalikan DataFrame [user, item, ts] (interaksi biner unik)."""
    path = path or config.DATASET_PATH
    raw = pd.read_excel(path, dtype=str)
    raw = raw.rename(columns={c: c.strip() for c in raw.columns})
    raw[config.USER_COL] = raw[config.USER_COL].ffill()
    raw[config.DATE_COL] = raw[config.DATE_COL].ffill()
    raw = raw.dropna(subset=[config.PRODUCT_COL])

    rec = []
    for _, r in raw.iterrows():
        prod = str(r[config.PRODUCT_COL]).strip()
        if not prod or prod.lower() == "nan":
            continue
        if config.ITEM_BY_CODE and " - " in prod:
            item = prod.split(" - ")[0].strip()      # kode, mis. 'A00A'
        else:
            item = prod
        ts = 0.0
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                ts = datetime.strptime(str(r[config.DATE_COL]).strip(), fmt).timestamp(); break
            except Exception:
                pass
        rec.append((str(r[config.USER_COL]).strip(), item, ts))

    df = pd.DataFrame(rec, columns=["user", "item", "ts"])
    # implicit feedback biner: satu pasangan (user,item) = satu interaksi
    df = df.sort_values("ts").drop_duplicates(["user", "item"], keep="last")
    return df


class Data:
    """Wadah hasil praproses agar mudah dipakai train/grid_search/predict."""
    def __init__(self, df, path):
        raw_users = df["user"].nunique()
        counts = df["user"].value_counts()
        keep = counts[counts >= config.MIN_INTERACT].index
        self.dropped = raw_users - len(keep)
        df = df[df["user"].isin(keep)].copy()

        self.users = sorted(df["user"].unique())
        self.items = sorted(df["item"].unique())
        self.u2i = {u: k for k, u in enumerate(self.users)}
        self.i2i = {it: k for k, it in enumerate(self.items)}
        self.code_of = {v: k for k, v in self.i2i.items()}
        df["u"] = df["user"].map(self.u2i)
        df["i"] = df["item"].map(self.i2i)
        self.n_users = len(self.users)
        self.n_items = len(self.items)
        self.user_items = df.groupby("u")["i"].apply(set).to_dict()

        df = df.sort_values(["u", "ts"])
        test = df.groupby("u").tail(1)
        self.test_pos = dict(zip(test["u"], test["i"]))
        train = df.drop(test.index)
        self.train_pairs = list(zip(train["u"].tolist(), train["i"].tolist()))
        self.df = df
        self.raw_users = raw_users

        _seed()
        self.eval_data = {u: [pos] + self.sample_negs(u, config.NEG_EVAL)
                          for u, pos in self.test_pos.items()}

    def sample_negs(self, u, n):
        ex = self.user_items[u]; out = []
        while len(out) < n:
            j = random.randint(0, self.n_items - 1)
            if j not in ex:
                out.append(j)
        return out

    def print_stats(self):
        print("=" * 60)
        print("STATISTIK DATASET (SKENARIO B)")
        print("=" * 60)
        print(f"Pengguna mentah             : {self.raw_users}")
        print(f"Dibuang (<{config.MIN_INTERACT} interaksi)        : {self.dropped}")
        print(f"Pengguna dipakai            : {self.n_users}")
        print(f"Item menu unik              : {self.n_items}")
        print(f"Interaksi positif unik      : {len(self.df)}")
        print(f"Rata-rata interaksi/pengguna: {len(self.df)/self.n_users:.2f}")
        print(f"Data latih (positif)        : {len(self.train_pairs)}")
        print(f"Data uji (pengguna, LOO)    : {len(self.test_pos)}")
        print(f"Sampel/epoch (pos+neg)      : {len(self.train_pairs)*(1+config.NEG_TRAIN)}")


def prepare_data(path=None):
    return Data(load_interactions(path), path or config.DATASET_PATH)
