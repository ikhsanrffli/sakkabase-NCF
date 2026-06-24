#!/usr/bin/env python3
"""
Pelatihan & evaluasi model Neural Collaborative Filtering (NCF) untuk skripsi
Sakka Base — SKENARIO B (User = Pelanggan asli).

Arsitektur & hyperparameter mengikuti "Konfigurasi C" pada skripsi:
  - Embedding pengguna & item: dimensi 32
  - Concatenation -> 64
  - Hidden MLP: Linear(64 -> 32) + ReLU + Dropout(0.2)
  - Output: Linear(32 -> 1) + Sigmoid
  - Optimizer Adam, lr 0.0005, weight_decay 1e-5
  - Loss Binary Cross-Entropy, batch 256, negative sampling 4:1
  - Early stopping patience 5, maksimum 50 epoch
  - Split Leave-One-Out, evaluasi 1 positif + 99 negatif (HR@10, NDCG@10)

Keputusan Skenario B:
  - USER  = kolom Pelanggan (nama asli)
  - ITEM  = KODE produk (varian ukuran digabung) -> 141 menu
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
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "src", "dataset.xlsx")

# ---- Hyperparameter (Konfigurasi C) ----
EMBED_DIM      = 32
HIDDEN         = 32          # MLP: 64 -> 32
DROPOUT        = 0.2
LR             = 0.0005
WEIGHT_DECAY   = 1e-5
BATCH_SIZE     = 256
MAX_EPOCHS     = 50
NEG_TRAIN      = 4           # negatif per positif saat latih
NEG_EVAL       = 99          # kandidat negatif per pengguna saat evaluasi
TOP_K          = 10
PATIENCE       = 5
MIN_INTERACT   = 2           # filter pengguna >= 2 item unik

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_interactions():
    """Baca xlsx -> DataFrame [user, item, ts] dengan forward-fill, item=KODE."""
    raw = pd.read_excel(XLSX, dtype=str)
    raw = raw.rename(columns={c: c.strip() for c in raw.columns})
    # forward-fill kolom transaksi (baris item lanjutan kosong)
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
    # implicit feedback biner: dedupe (user,item), simpan timestamp TERAKHIR
    df = df.sort_values("ts").drop_duplicates(["user", "item"], keep="last")
    return df


def main():
    df = load_interactions()
    raw_users = df["user"].nunique()
    raw_inter = len(df)

    # filter pengguna >= MIN_INTERACT item unik
    counts = df["user"].value_counts()
    keep = counts[counts >= MIN_INTERACT].index
    dropped_users = raw_users - len(keep)
    df = df[df["user"].isin(keep)].copy()

    # label encoding
    users = sorted(df["user"].unique())
    items = sorted(df["item"].unique())
    u2i = {u: k for k, u in enumerate(users)}
    i2i = {it: k for k, it in enumerate(items)}
    df["u"] = df["user"].map(u2i)
    df["i"] = df["item"].map(i2i)
    n_users, n_items = len(users), len(items)

    # himpunan item per user (untuk negative sampling)
    user_items = df.groupby("u")["i"].apply(set).to_dict()

    # Leave-One-Out: item dengan timestamp terbaru jadi test
    df = df.sort_values(["u", "ts"])
    test = df.groupby("u").tail(1)
    test_pos = dict(zip(test["u"], test["i"]))
    train = df.drop(test.index)
    train_pairs = list(zip(train["u"].tolist(), train["i"].tolist()))

    all_items = np.arange(n_items)

    def sample_negs(u, n, exclude):
        out = []
        while len(out) < n:
            j = random.randint(0, n_items - 1)
            if j not in exclude:
                out.append(j)
        return out

    # kandidat evaluasi: 1 positif + 99 negatif (tetap per epoch agar adil)
    eval_data = {}
    for u, pos in test_pos.items():
        negs = sample_negs(u, NEG_EVAL, user_items[u])
        eval_data[u] = [pos] + negs

    print("=" * 64)
    print("STATISTIK DATASET — SKENARIO B (User = Pelanggan, Item = kode)")
    print("=" * 64)
    print(f"Pengguna unik (mentah)            : {raw_users}")
    print(f"Dibuang (<{MIN_INTERACT} interaksi)            : {dropped_users}")
    print(f"Pengguna dipakai (>= {MIN_INTERACT})           : {n_users}")
    print(f"Item menu unik (kode)             : {n_items}")
    print(f"Interaksi positif unik            : {len(df)}")
    print(f"Rata-rata interaksi per pengguna  : {len(df)/n_users:.2f}")
    print(f"Data latih (train positif)        : {len(train_pairs)}")
    print(f"Data uji (test pengguna, LOO)     : {len(test_pos)}")
    print(f"Sampel/epoch (positif+negatif)    : {len(train_pairs)*(1+NEG_TRAIN)}")

    # ---- Model NCF (Konfigurasi C) ----
    class NCF(nn.Module):
        def __init__(self, nu, ni, d, h, p):
            super().__init__()
            self.ue = nn.Embedding(nu, d)
            self.ie = nn.Embedding(ni, d)
            self.mlp = nn.Sequential(
                nn.Linear(2 * d, h), nn.ReLU(), nn.Dropout(p))
            self.out = nn.Linear(h, 1)
            nn.init.normal_(self.ue.weight, std=0.01)
            nn.init.normal_(self.ie.weight, std=0.01)

        def forward(self, u, i):
            x = torch.cat([self.ue(u), self.ie(i)], dim=-1)
            return torch.sigmoid(self.out(self.mlp(x))).squeeze(-1)

    model = NCF(n_users, n_items, EMBED_DIM, HIDDEN, DROPOUT).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameter model             : {n_params}")
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    bce = nn.BCELoss()

    def evaluate():
        model.eval()
        hr = ndcg = 0.0
        with torch.no_grad():
            for u, cand in eval_data.items():
                uu = torch.full((len(cand),), u, dtype=torch.long, device=device)
                ii = torch.tensor(cand, dtype=torch.long, device=device)
                scores = model(uu, ii).cpu().numpy()
                # posisi 0 = item positif
                rank = (scores > scores[0]).sum()  # berapa kandidat berskor lebih tinggi
                if rank < TOP_K:
                    hr += 1.0
                    ndcg += 1.0 / math.log2(rank + 2)
        n = len(eval_data)
        return hr / n, ndcg / n

    print("\n" + "=" * 64)
    print("PELATIHAN (Konfigurasi C)")
    print("=" * 64)
    print(f"{'Epoch':>5} | {'Loss':>7} | {'HR@10':>7} | {'NDCG@10':>8} | Keterangan")
    best_hr, best_ndcg, best_epoch, best_loss = -1, -1, 0, 0
    best_state, wait, total_epoch = None, 0, 0
    history = []
    for epoch in range(1, MAX_EPOCHS + 1):
        total_epoch = epoch
        # bangun sampel latih (resample negatif tiap epoch)
        U, I, Y = [], [], []
        for u, i in train_pairs:
            U.append(u); I.append(i); Y.append(1.0)
            for j in sample_negs(u, NEG_TRAIN, user_items[u]):
                U.append(u); I.append(j); Y.append(0.0)
        U = torch.tensor(U, dtype=torch.long); I = torch.tensor(I, dtype=torch.long)
        Y = torch.tensor(Y, dtype=torch.float)
        perm = torch.randperm(len(U))
        U, I, Y = U[perm], I[perm], Y[perm]

        model.train()
        tot, nb = 0.0, 0
        for s in range(0, len(U), BATCH_SIZE):
            bu = U[s:s+BATCH_SIZE].to(device)
            bi = I[s:s+BATCH_SIZE].to(device)
            by = Y[s:s+BATCH_SIZE].to(device)
            opt.zero_grad()
            loss = bce(model(bu, bi), by)
            loss.backward(); opt.step()
            tot += loss.item(); nb += 1
        avg = tot / nb
        hr, ndcg = evaluate()
        note = "-"
        if hr > best_hr:
            best_hr, best_ndcg, best_epoch, best_loss = hr, ndcg, epoch, avg
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            wait = 0; note = "Model terbaik tersimpan"
        else:
            wait += 1; note = f"Tidak ada peningkatan ({wait}/{PATIENCE})"
        history.append((epoch, avg, hr, ndcg, note))
        print(f"{epoch:>5} | {avg:>7.4f} | {hr:>7.4f} | {ndcg:>8.4f} | {note}")
        if wait >= PATIENCE:
            print(f"{'':>5}   Early stopping terpenuhi pada epoch {epoch}")
            break

    print("\n" + "=" * 64)
    print("HASIL AKHIR — MODEL FINAL (Konfigurasi C, Skenario B)")
    print("=" * 64)
    print(f"Epoch terbaik            : {best_epoch}")
    print(f"Training loss epoch best : {best_loss:.4f}")
    print(f"Total epoch dijalankan   : {total_epoch}")
    print(f"Total parameter model    : {n_params}")
    print(f"HR@10  (data uji)        : {best_hr:.4f}")
    print(f"NDCG@10 (data uji)       : {best_ndcg:.4f}")

    # ---- Contoh inferensi Top-10 untuk satu pengguna (mis. paling aktif) ----
    if best_state:
        model.load_state_dict(best_state)
    model.eval()
    active_u = int(df["u"].value_counts().idxmax())
    active_name = users[active_u]
    seen = user_items[active_u]
    cand = [j for j in range(n_items) if j not in seen]
    with torch.no_grad():
        uu = torch.full((len(cand),), active_u, dtype=torch.long, device=device)
        ii = torch.tensor(cand, dtype=torch.long, device=device)
        sc = model(uu, ii).cpu().numpy()
    code_of = {v: k for k, v in i2i.items()}
    top = sorted(zip(cand, sc), key=lambda x: -x[1])[:TOP_K]
    print("\n" + "=" * 64)
    print(f"CONTOH TOP-10 REKOMENDASI — Pengguna '{active_name}' (idx {active_u})")
    print("=" * 64)
    for r, (j, s) in enumerate(top, 1):
        print(f"{r:>2}. {code_of[j]:<6}  skor={s:.4f}")


if __name__ == "__main__":
    main()
