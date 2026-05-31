"""
Training loop model NCF dengan early stopping, evaluasi HR@10 train & test,
dan simpan kurva training sebagai PNG.

Standalone : python -m ncf.train
Grid search : diimport dari ncf.grid_search
"""

import os
import math
import random

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ncf.config import (
    EMBEDDING_DIM, MLP_LAYERS, DROPOUT,
    LR, WEIGHT_DECAY, BATCH_SIZE, NUM_EPOCHS, NUM_NEGATIVES,
    EARLY_STOPPING_PATIENCE, TOP_K, TRAIN_EVAL_SAMPLE,
    MODEL_DIR, MODEL_PATH,
)
from ncf.dataset import get_data, TrainDataset
from ncf.model import NCF


# ── Evaluasi (batched untuk efisiensi CPU) ────────────────────────────────────

def _evaluate(model: NCF, eval_list: list, device: torch.device, k: int = TOP_K):
    """
    Hitung HR@K dan NDCG@K secara batch.

    eval_list: list of (user_idx, pos_item_idx, [99 neg_item_idxs])
    """
    n_cand    = 100
    all_users = []
    all_items = []
    pos_scores_idx = []   # indeks posisi item positif dalam setiap blok 100

    for uidx, pos, negs in eval_list:
        all_users.extend([uidx] * n_cand)
        all_items.extend([pos] + negs)

    u_t = torch.tensor(all_users, dtype=torch.long).to(device)
    i_t = torch.tensor(all_items, dtype=torch.long).to(device)

    model.eval()
    with torch.no_grad():
        all_scores = model(u_t, i_t).cpu().tolist()

    hr_list, ndcg_list = [], []
    for i in range(len(eval_list)):
        s         = all_scores[i * n_cand : (i + 1) * n_cand]
        pos_score = s[0]                                    # positif selalu di indeks 0
        rank      = 1 + sum(1 for x in s[1:] if x > pos_score)

        if rank <= k:
            hr_list.append(1)
            ndcg_list.append(1.0 / math.log2(rank + 1))
        else:
            hr_list.append(0)
            ndcg_list.append(0.0)

    hr   = sum(hr_list)   / len(hr_list)
    ndcg = sum(ndcg_list) / len(ndcg_list)
    return hr, ndcg


def _candidates_to_eval_list(candidates: dict) -> list:
    """Konversi format {user_idx: (pos, negs)} → list of (uidx, pos, negs)."""
    return [(uidx, pos, negs) for uidx, (pos, negs) in candidates.items()]


def _build_train_eval_list(train_data, user_item_set, n_items,
                           sample_size: int = TRAIN_EVAL_SAMPLE) -> list:
    """
    Sample `sample_size` pair positif dari data latih, lalu tambahkan
    99 negatif acak per pair → digunakan untuk approximasi train HR@10.
    """
    sample = random.sample(train_data, min(sample_size, len(train_data)))
    result = []
    for uidx, pos_iidx in sample:
        seen    = user_item_set[uidx]
        negs    = []
        neg_set = set()
        while len(negs) < 99:
            neg = random.randint(0, n_items - 1)
            if neg not in seen and neg not in neg_set:
                negs.append(neg)
                neg_set.add(neg)
        result.append((uidx, pos_iidx, negs))
    return result


# ── Plot kurva training ───────────────────────────────────────────────────────

def _save_plot(history: dict, best_epoch: int, save_path: str, label: str = ""):
    try:
        import matplotlib
        matplotlib.use("Agg")          # non-interactive backend (aman di Windows)
        import matplotlib.pyplot as plt

        epochs = list(range(1, len(history["loss"]) + 1))
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        title_suffix = f" — {label}" if label else ""

        # ── Loss ──────────────────────────────────────────────────────────────
        ax1.plot(epochs, history["loss"], color="steelblue", label="Train Loss")
        ax1.axvline(best_epoch, color="red", linestyle="--", alpha=0.6,
                    label=f"Best (epoch {best_epoch})")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("BCE Loss")
        ax1.set_title(f"Training Loss{title_suffix}")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # ── HR@10 train vs test ────────────────────────────────────────────────
        ax2.plot(epochs, history["test_hr"],  color="green",  label="Test HR@10")
        ax2.plot(epochs, history["train_hr"], color="orange", linestyle="--",
                 alpha=0.8, label="Train HR@10 (approx)")
        ax2.axvline(best_epoch, color="red", linestyle="--", alpha=0.6,
                    label=f"Best (epoch {best_epoch})")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("HR@10")
        ax2.set_title(f"HR@10 Train vs Test{title_suffix}")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Plot disimpan → {save_path}")

    except ImportError:
        print("(matplotlib tidak tersedia, plot dilewati)")


# ── Training utama ────────────────────────────────────────────────────────────

def train(
    cfg:        dict | None = None,
    data:       dict | None = None,
    model_path: str         = MODEL_PATH,
    save_plot:  bool        = True,
    verbose:    bool        = True,
    label:      str         = "",
) -> dict:
    """
    Latih model NCF.

    cfg        : override hyperparameter (untuk grid search)
    data       : hasil get_data() yang sudah di-load (untuk grid search, hindari reload)
    model_path : path simpan model terbaik
    save_plot  : simpan kurva training ke PNG
    verbose    : cetak header dan progress
    label      : label untuk nama file plot (contoh: 'config_A')

    Returns dict: {best_hr, best_ndcg, best_epoch, total_epochs, history}
    """

    # ── Gabung config dengan default ──────────────────────────────────────────
    defaults = {
        "embed_dim":  EMBEDDING_DIM,
        "mlp_layers": MLP_LAYERS,
        "dropout":    DROPOUT,
        "lr":         LR,
        "weight_decay": WEIGHT_DECAY,
        "batch_size": BATCH_SIZE,
        "num_epochs": NUM_EPOCHS,
        "num_neg":    NUM_NEGATIVES,
        "patience":   EARLY_STOPPING_PATIENCE,
    }
    if cfg:
        defaults.update(cfg)
    c = defaults

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if verbose:
        print("=" * 60)
        header = f"  NCF Training{' — ' + label if label else ''}"
        print(header)
        print("=" * 60)
        print(f"  embed={c['embed_dim']}  mlp={c['mlp_layers']}  "
              f"dropout={c['dropout']}  lr={c['lr']}  wd={c['weight_decay']}")
        print(f"  Device: {device}\n")

    # ── Load data ─────────────────────────────────────────────────────────────
    if data is None:
        if verbose:
            print("[1/3] Memuat data dari database ...")
        data = get_data()
        if verbose:
            print()
    n_users = data["n_users"]
    n_items = data["n_items"]

    test_eval_list = _candidates_to_eval_list(data["test_candidates"])

    # ── Dataset & loader ──────────────────────────────────────────────────────
    train_dataset = TrainDataset(
        data["train_data"], data["user_item_set"], n_items, c["num_neg"]
    )

    # ── Model ─────────────────────────────────────────────────────────────────
    if verbose:
        print("[2/3] Membangun model NCF ...")
    model     = NCF(n_users, n_items, c["embed_dim"], c["mlp_layers"], c["dropout"]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=c["lr"], weight_decay=c["weight_decay"])
    criterion = nn.BCELoss()

    if verbose:
        total_params = sum(p.numel() for p in model.parameters())
        print(f"  Total parameter: {total_params:,}\n")
        print("[3/3] Training ...\n")
        print(f"{'Epoch':>6}  {'Loss':>8}  {'TrainHR':>8}  {'TestHR':>8}  {'NDCG':>8}  Status")
        print("-" * 58)

    os.makedirs(MODEL_DIR, exist_ok=True)

    best_hr    = 0.0
    best_ndcg  = 0.0
    best_epoch = 0
    no_improve = 0
    history    = {"loss": [], "train_hr": [], "test_hr": [], "test_ndcg": []}

    for epoch in range(1, c["num_epochs"] + 1):
        # Resample negatif setiap epoch
        train_dataset.resample()
        loader = DataLoader(
            train_dataset, batch_size=c["batch_size"], shuffle=True, num_workers=0
        )

        # ── Train satu epoch ──────────────────────────────────────────────────
        model.train()
        total_loss = 0.0
        for user_ids, item_ids, labels in loader:
            preds = model(user_ids.to(device), item_ids.to(device))
            loss  = criterion(preds, labels.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(loader)

        # ── Evaluasi train & test ─────────────────────────────────────────────
        train_eval_list = _build_train_eval_list(
            data["train_data"], data["user_item_set"], n_items
        )
        train_hr, _     = _evaluate(model, train_eval_list, device)
        test_hr, test_ndcg = _evaluate(model, test_eval_list, device)

        history["loss"].append(avg_loss)
        history["train_hr"].append(train_hr)
        history["test_hr"].append(test_hr)
        history["test_ndcg"].append(test_ndcg)

        # ── Early stopping + simpan best ──────────────────────────────────────
        status = ""
        if test_hr > best_hr:
            best_hr    = test_hr
            best_ndcg  = test_ndcg
            best_epoch = epoch
            no_improve = 0
            status     = "* best"
            torch.save(
                {
                    "epoch":       epoch,
                    "model_state": model.state_dict(),
                    "n_users":     n_users,
                    "n_items":     n_items,
                    "user2idx":    data["user2idx"],
                    "item2idx":    data["item2idx"],
                    "idx2user":    data["idx2user"],
                    "idx2item":    data["idx2item"],
                    "hr_at_10":    best_hr,
                    "ndcg_at_10":  best_ndcg,
                    "config":      c,
                },
                model_path,
            )
        else:
            no_improve += 1
            if no_improve >= c["patience"]:
                if verbose:
                    print(f"{epoch:>6}  {avg_loss:>8.4f}  {train_hr:>8.4f}  "
                          f"{test_hr:>8.4f}  {test_ndcg:>8.4f}  (early stop)")
                break

        if verbose:
            print(f"{epoch:>6}  {avg_loss:>8.4f}  {train_hr:>8.4f}  "
                  f"{test_hr:>8.4f}  {test_ndcg:>8.4f}  {status}")

    total_epochs = len(history["loss"])

    if verbose:
        print("-" * 58)
        print(f"Selesai — Best epoch {best_epoch}: "
              f"HR@10={best_hr:.4f}, NDCG@10={best_ndcg:.4f}")
        print(f"Model disimpan → {model_path}")

    if save_plot:
        plot_label  = label or os.path.splitext(os.path.basename(model_path))[0]
        plot_path   = os.path.join(MODEL_DIR, f"training_curves_{plot_label}.png")
        _save_plot(history, best_epoch, plot_path, label=label)

    return {
        "best_hr":     best_hr,
        "best_ndcg":   best_ndcg,
        "best_epoch":  best_epoch,
        "total_epochs": total_epochs,
        "history":     history,
    }


if __name__ == "__main__":
    result = train(model_path=MODEL_PATH, save_plot=True)
