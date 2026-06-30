"""
train.py — Pelatihan satu konfigurasi NCF + evaluasi HR@10 / NDCG@10.

Dipakai oleh grid_search.py untuk ketiga konfigurasi. Jika dijalankan langsung,
melatih konfigurasi final (C) lalu menyimpan model & riwayat per-epoch.

  python train.py
"""
import os, csv, math, random
import numpy as np
import torch
import torch.nn as nn
import config
from dataset import prepare_data
from model import NCF

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _seed():
    random.seed(config.SEED); np.random.seed(config.SEED); torch.manual_seed(config.SEED)


def evaluate(model, data):
    """HR@10 & NDCG@10 dengan kandidat 1 positif + 99 negatif (peringkat-harapan)."""
    model.eval(); hr = ndcg = 0.0
    with torch.no_grad():
        for u, cand in data.eval_data.items():
            uu = torch.full((len(cand),), u, dtype=torch.long, device=device)
            ii = torch.tensor(cand, dtype=torch.long, device=device)
            sc = model(uu, ii).cpu().numpy()
            greater = float((sc > sc[0]).sum())
            ties = float((sc == sc[0]).sum() - 1)
            rank = greater + 0.5 * ties
            if rank < config.TOP_K:
                hr += 1.0; ndcg += 1.0 / math.log2(rank + 2)
    n = len(data.eval_data)
    return hr / n, ndcg / n


def train_config(data, cfg, name="C", verbose=False, save=False):
    _seed()
    model = NCF(data.n_users, data.n_items, cfg["embed"], cfg["layers"], cfg["dropout"]).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"], weight_decay=config.WEIGHT_DECAY)
    bce = nn.BCELoss()

    best = dict(hr=-1, ndcg=-1, epoch=0, loss=0.0, state=None,
                params=model.num_params(), total_epoch=0, history=[])
    wait = 0
    if verbose:
        print(f"{'Epoch':>5} | {'Loss':>7} | {'HR@10':>7} | {'NDCG@10':>8} | Keterangan")
    for epoch in range(1, config.MAX_EPOCHS + 1):
        best["total_epoch"] = epoch
        # bangun batch (resample negatif tiap epoch)
        U, I, Y = [], [], []
        for u, i in data.train_pairs:
            U.append(u); I.append(i); Y.append(1.0)
            for j in data.sample_negs(u, config.NEG_TRAIN):
                U.append(u); I.append(j); Y.append(0.0)
        U = torch.tensor(U); I = torch.tensor(I); Y = torch.tensor(Y, dtype=torch.float)
        perm = torch.randperm(len(U)); U, I, Y = U[perm], I[perm], Y[perm]

        model.train(); tot = nb = 0
        for s in range(0, len(U), config.BATCH_SIZE):
            bu = U[s:s+config.BATCH_SIZE].to(device)
            bi = I[s:s+config.BATCH_SIZE].to(device)
            by = Y[s:s+config.BATCH_SIZE].to(device)
            opt.zero_grad(); loss = bce(model(bu, bi), by); loss.backward(); opt.step()
            tot += loss.item(); nb += 1
        avg = tot / nb
        hr, ndcg = evaluate(model, data)
        if hr > best["hr"]:
            best.update(hr=hr, ndcg=ndcg, epoch=epoch, loss=avg,
                        state={k: v.clone() for k, v in model.state_dict().items()})
            wait = 0; note = "Model terbaik tersimpan"
        else:
            wait += 1; note = f"Tidak ada peningkatan ({wait}/{config.PATIENCE})"
        best["history"].append((epoch, avg, hr, ndcg, note))
        if verbose:
            print(f"{epoch:>5} | {avg:>7.4f} | {hr:>7.4f} | {ndcg:>8.4f} | {note}")
        if wait >= config.PATIENCE:
            if verbose:
                print(f"        Early stopping pada epoch {epoch}")
            break

    if save and best["state"]:
        os.makedirs(config.MODEL_DIR, exist_ok=True)
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        torch.save(best["state"], os.path.join(config.MODEL_DIR, f"ncf_config_{name}.pth"))
        with open(os.path.join(config.OUTPUT_DIR, f"history_{name}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["epoch", "training_loss", "hr_at_10", "ndcg_at_10", "keterangan"])
            for ep, ls, hr, nd, nt in best["history"]:
                w.writerow([ep, f"{ls:.4f}", f"{hr:.4f}", f"{nd:.4f}", nt])
    return best


def main():
    data = prepare_data()
    data.print_stats()
    name = config.FINAL_CONFIG
    print(f"\nMelatih konfigurasi final '{name}' ...\n")
    best = train_config(data, config.CONFIGS[name], name=name, verbose=True, save=True)
    print("\n" + "=" * 60)
    print(f"MODEL FINAL — Konfigurasi {name}")
    print("=" * 60)
    print(f"Epoch terbaik   : {best['epoch']}")
    print(f"Training loss   : {best['loss']:.4f}")
    print(f"Total epoch     : {best['total_epoch']}")
    print(f"Total parameter : {best['params']}")
    print(f"HR@10           : {best['hr']:.4f}")
    print(f"NDCG@10         : {best['ndcg']:.4f}")
    print(f"\nModel & riwayat tersimpan di: {config.MODEL_DIR} , {config.OUTPUT_DIR}")


if __name__ == "__main__":
    main()
