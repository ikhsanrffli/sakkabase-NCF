#!/usr/bin/env python3
"""
Pelatihan & evaluasi model Neural Collaborative Filtering (NCF) untuk skripsi
Sakka Base — SKENARIO B (User = Pelanggan asli).

Melatih TIGA konfigurasi (A, B, C) seperti pada skripsi lalu memilih yang
terbaik berdasarkan HR@10 (Tabel perbandingan konfigurasi).

Arsitektur umum (mengikuti skripsi):
  - Embedding pengguna & item (dimensi = embed_dim)
  - Concatenation -> 2*embed_dim
  - MLP berlapis (mlp_layers) dengan ReLU + Dropout di tiap lapis
  - Output: Linear(layer_terakhir -> 1) + Sigmoid
  - Optimizer Adam (+weight_decay 1e-5), loss BCE, batch 256
  - Negative sampling 4:1, early stopping patience 5, maks 50 epoch
  - Split Leave-One-Out, evaluasi 1 positif + 99 negatif (HR@10, NDCG@10)

Konfigurasi:
  A: embed 32, MLP [64,32,16], dropout 0.2, lr 0.001
  B: embed 16, MLP [32,16,8],  dropout 0.3, lr 0.001
  C: embed 32, MLP [64,32],     dropout 0.2, lr 0.0005   (final di skripsi)

Keputusan Skenario B:
  - USER  = kolom Pelanggan (nama asli)
  - ITEM  = KODE produk (varian ukuran digabung)
  - Filter pengguna dengan >= 2 item unik (agar bisa Leave-One-Out)

Jalankan:
  pip install torch pandas scikit-learn numpy openpyxl
  python scripts/train_ncf.py
"""
import os, random, math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime

SEED = 42
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "src", "dataset.xlsx")

# ---- Pengaturan umum ----
WEIGHT_DECAY = 1e-5
BATCH_SIZE   = 256
MAX_EPOCHS   = 50
NEG_TRAIN    = 4
NEG_EVAL     = 99
TOP_K        = 10
PATIENCE     = 5
MIN_INTERACT = 2

CONFIGS = {
    "A": dict(embed=32, layers=[64, 32, 16], dropout=0.2, lr=0.001),
    "B": dict(embed=16, layers=[32, 16, 8],  dropout=0.3, lr=0.001),
    "C": dict(embed=32, layers=[64, 32],     dropout=0.2, lr=0.0005),
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_all():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)


def load_interactions():
    raw = pd.read_excel(XLSX, dtype=str)
    raw = raw.rename(columns={c: c.strip() for c in raw.columns})
    raw["Pelanggan"] = raw["Pelanggan"].ffill()
    raw["Tanggal"]   = raw["Tanggal"].ffill()
    raw = raw.dropna(subset=["Produk"])
    rec = []
    for _, r in raw.iterrows():
        prod = str(r["Produk"]).strip()
        if not prod or prod.lower() == "nan":
            continue
        code = prod.split(" - ")[0].strip() if " - " in prod else prod
        ts = 0.0
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                ts = datetime.strptime(str(r["Tanggal"]).strip(), fmt).timestamp(); break
            except Exception:
                pass
        rec.append((str(r["Pelanggan"]).strip(), code, ts))
    df = pd.DataFrame(rec, columns=["user", "item", "ts"])
    df = df.sort_values("ts").drop_duplicates(["user", "item"], keep="last")
    return df


class NCF(nn.Module):
    def __init__(self, nu, ni, embed, layers, dropout):
        super().__init__()
        self.ue = nn.Embedding(nu, embed)
        self.ie = nn.Embedding(ni, embed)
        seq = []
        # layers[0] = dimensi concat (2*embed); lapis berikutnya = hidden
        for a, b in zip(layers[:-1], layers[1:]):
            seq += [nn.Linear(a, b), nn.ReLU(), nn.Dropout(dropout)]
        self.mlp = nn.Sequential(*seq)
        self.out = nn.Linear(layers[-1], 1)
        nn.init.normal_(self.ue.weight, std=0.01)
        nn.init.normal_(self.ie.weight, std=0.01)

    def forward(self, u, i):
        x = torch.cat([self.ue(u), self.ie(i)], dim=-1)
        return torch.sigmoid(self.out(self.mlp(x))).squeeze(-1)


def prepare():
    df = load_interactions()
    raw_users = df["user"].nunique()
    counts = df["user"].value_counts()
    keep = counts[counts >= MIN_INTERACT].index
    dropped = raw_users - len(keep)
    df = df[df["user"].isin(keep)].copy()

    users = sorted(df["user"].unique())
    items = sorted(df["item"].unique())
    u2i = {u: k for k, u in enumerate(users)}
    i2i = {it: k for k, it in enumerate(items)}
    df["u"] = df["user"].map(u2i); df["i"] = df["item"].map(i2i)
    n_users, n_items = len(users), len(items)
    user_items = df.groupby("u")["i"].apply(set).to_dict()

    df = df.sort_values(["u", "ts"])
    test = df.groupby("u").tail(1)
    test_pos = dict(zip(test["u"], test["i"]))
    train = df.drop(test.index)
    train_pairs = list(zip(train["u"].tolist(), train["i"].tolist()))

    def sample_negs(u, n):
        ex = user_items[u]; out = []
        while len(out) < n:
            j = random.randint(0, n_items - 1)
            if j not in ex:
                out.append(j)
        return out

    seed_all()
    eval_data = {u: [pos] + sample_negs(u, NEG_EVAL) for u, pos in test_pos.items()}

    stats = dict(raw_users=raw_users, dropped=dropped, n_users=n_users,
                 n_items=n_items, inter=len(df), train=len(train_pairs),
                 test=len(test_pos))
    return dict(df=df, users=users, items=items, i2i=i2i, n_users=n_users,
                n_items=n_items, user_items=user_items, train_pairs=train_pairs,
                eval_data=eval_data, sample_negs=sample_negs, stats=stats)


def train_config(name, cfg, D, verbose=False):
    seed_all()
    n_users, n_items = D["n_users"], D["n_items"]
    train_pairs, user_items = D["train_pairs"], D["user_items"]
    sample_negs, eval_data = D["sample_negs"], D["eval_data"]

    model = NCF(n_users, n_items, cfg["embed"], cfg["layers"], cfg["dropout"]).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"], weight_decay=WEIGHT_DECAY)
    bce = nn.BCELoss()

    def evaluate():
        model.eval(); hr = ndcg = 0.0
        with torch.no_grad():
            for u, cand in eval_data.items():
                uu = torch.full((len(cand),), u, dtype=torch.long, device=device)
                ii = torch.tensor(cand, dtype=torch.long, device=device)
                sc = model(uu, ii).cpu().numpy()
                # peringkat item positif (indeks 0). Skor seri ditangani sebagai
                # peringkat harapan (rata-rata) agar adil & deterministik.
                greater = float((sc > sc[0]).sum())
                ties = float((sc == sc[0]).sum() - 1)
                rank = greater + 0.5 * ties      # posisi 0-indeks
                if rank < TOP_K:
                    hr += 1.0; ndcg += 1.0 / math.log2(rank + 2)
        n = len(eval_data); return hr / n, ndcg / n

    best = dict(hr=-1, ndcg=-1, epoch=0, loss=0, state=None)
    wait, total = 0, 0; history = []
    for epoch in range(1, MAX_EPOCHS + 1):
        total = epoch
        U, I, Y = [], [], []
        for u, i in train_pairs:
            U.append(u); I.append(i); Y.append(1.0)
            for j in sample_negs(u, NEG_TRAIN):
                U.append(u); I.append(j); Y.append(0.0)
        U = torch.tensor(U); I = torch.tensor(I); Y = torch.tensor(Y, dtype=torch.float)
        perm = torch.randperm(len(U)); U, I, Y = U[perm], I[perm], Y[perm]
        model.train(); tot = nb = 0
        for s in range(0, len(U), BATCH_SIZE):
            bu, bi, by = U[s:s+BATCH_SIZE].to(device), I[s:s+BATCH_SIZE].to(device), Y[s:s+BATCH_SIZE].to(device)
            opt.zero_grad(); loss = bce(model(bu, bi), by); loss.backward(); opt.step()
            tot += loss.item(); nb += 1
        avg = tot / nb; hr, ndcg = evaluate()
        if hr > best["hr"]:
            best = dict(hr=hr, ndcg=ndcg, epoch=epoch, loss=avg,
                        state={k: v.clone() for k, v in model.state_dict().items()})
            wait = 0; note = "Model terbaik tersimpan"
        else:
            wait += 1; note = f"Tidak ada peningkatan ({wait}/{PATIENCE})"
        history.append((epoch, avg, hr, ndcg, note))
        if verbose:
            print(f"{epoch:>5} | {avg:>7.4f} | {hr:>7.4f} | {ndcg:>8.4f} | {note}")
        if wait >= PATIENCE:
            if verbose: print(f"        Early stopping pada epoch {epoch}")
            break
    best["params"] = n_params; best["total_epoch"] = total; best["history"] = history
    return best, model


def main():
    D = prepare(); s = D["stats"]
    print("=" * 64)
    print("STATISTIK DATASET — SKENARIO B (User = Pelanggan, Item = kode)")
    print("=" * 64)
    print(f"Pengguna unik (mentah)            : {s['raw_users']}")
    print(f"Dibuang (<{MIN_INTERACT} interaksi)            : {s['dropped']}")
    print(f"Pengguna dipakai (>= {MIN_INTERACT})           : {s['n_users']}")
    print(f"Item menu unik (kode)             : {s['n_items']}")
    print(f"Interaksi positif unik            : {s['inter']}")
    print(f"Rata-rata interaksi per pengguna  : {s['inter']/s['n_users']:.2f}")
    print(f"Data latih (train positif)        : {s['train']}")
    print(f"Data uji (test pengguna, LOO)     : {s['test']}")
    print(f"Sampel/epoch (positif+negatif)    : {s['train']*(1+NEG_TRAIN)}")

    results = {}
    for name, cfg in CONFIGS.items():
        verbose = (name == "C")
        if verbose:
            print("\n" + "=" * 64)
            print(f"PELATIHAN DETAIL — Konfigurasi {name} (final)")
            print("=" * 64)
            print(f"{'Epoch':>5} | {'Loss':>7} | {'HR@10':>7} | {'NDCG@10':>8} | Keterangan")
        best, _ = train_config(name, cfg, D, verbose=verbose)
        results[name] = (cfg, best)

    print("\n" + "=" * 64)
    print("TABEL PERBANDINGAN KONFIGURASI (pengganti Tabel 4.8)")
    print("=" * 64)
    print(f"{'Konf':>4} | {'embed':>5} | {'mlp_layers':>14} | {'drop':>4} | {'lr':>6} | {'epoch':>5} | {'HR@10':>7} | {'NDCG@10':>8}")
    for name, (cfg, b) in results.items():
        print(f"{name:>4} | {cfg['embed']:>5} | {str(cfg['layers']):>14} | {cfg['dropout']:>4} | {cfg['lr']:>6} | {b['epoch']:>5} | {b['hr']:>7.4f} | {b['ndcg']:>8.4f}")

    best_name = max(results, key=lambda k: results[k][1]["hr"])
    bc = results[best_name][1]
    print("\n" + "=" * 64)
    print(f"MODEL FINAL — Konfigurasi {best_name}")
    print("=" * 64)
    print(f"Epoch terbaik            : {bc['epoch']}")
    print(f"Training loss epoch best : {bc['loss']:.4f}")
    print(f"Total epoch dijalankan   : {bc['total_epoch']}")
    print(f"Total parameter model    : {bc['params']}")
    print(f"HR@10  (data uji)        : {bc['hr']:.4f}")
    print(f"NDCG@10 (data uji)       : {bc['ndcg']:.4f}")


if __name__ == "__main__":
    main()
