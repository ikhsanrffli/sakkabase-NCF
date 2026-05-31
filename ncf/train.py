"""
Training loop model NCF.
Jalankan: python -m ncf.train
"""

import os
import math

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ncf.config import LR, BATCH_SIZE, NUM_EPOCHS, TOP_K, MODEL_DIR, MODEL_PATH
from ncf.dataset import get_data, TrainDataset
from ncf.model import NCF


# ── Evaluasi HR@K dan NDCG@K ─────────────────────────────────────────────────

def evaluate(model: NCF, test_candidates: dict, device: torch.device, k: int = TOP_K):
    """
    Hitung HR@K dan NDCG@K pada set kandidat uji.
    Tiap user: 1 positif + 99 negatif → ranking → cek apakah positif masuk top-K.
    """
    model.eval()
    hr_list, ndcg_list = [], []

    with torch.no_grad():
        for uidx, (pos_item, neg_items) in test_candidates.items():
            candidates = [pos_item] + neg_items          # 100 item

            u_tensor = torch.tensor([uidx] * len(candidates), dtype=torch.long).to(device)
            i_tensor = torch.tensor(candidates,               dtype=torch.long).to(device)

            scores = model(u_tensor, i_tensor).cpu().tolist()

            # Urutkan skor tertinggi → terendah
            ranked = sorted(zip(scores, candidates), key=lambda x: -x[0])
            top_k  = [item for _, item in ranked[:k]]

            if pos_item in top_k:
                rank = top_k.index(pos_item) + 1    # 1-based
                hr_list.append(1)
                ndcg_list.append(1.0 / math.log2(rank + 1))
            else:
                hr_list.append(0)
                ndcg_list.append(0.0)

    hr   = sum(hr_list)   / len(hr_list)
    ndcg = sum(ndcg_list) / len(ndcg_list)
    return hr, ndcg


# ── Training ──────────────────────────────────────────────────────────────────

def train():
    print("=" * 60)
    print("  NCF Training — Sakka Base Recommendation System")
    print("=" * 60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device  : {device}\n")

    # ── 1. Data ──────────────────────────────────────────────────────────────
    print("[1/3] Memuat data dari database ...")
    data = get_data()
    print()

    train_dataset = TrainDataset(
        data["train_data"],
        data["user_item_set"],
        data["n_items"],
    )

    # ── 2. Model & optimizer ─────────────────────────────────────────────────
    print("[2/3] Membangun model NCF ...")
    model     = NCF(data["n_users"], data["n_items"]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.BCELoss()

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Total parameter: {total_params:,}\n")

    os.makedirs(MODEL_DIR, exist_ok=True)
    best_hr    = 0.0
    best_ndcg  = 0.0
    best_epoch = 0

    # ── 3. Training loop ─────────────────────────────────────────────────────
    print("[3/3] Training ...\n")
    print(f"{'Epoch':>6}  {'Loss':>8}  {'HR@10':>7}  {'NDCG@10':>9}  {'Status'}")
    print("-" * 52)

    for epoch in range(1, NUM_EPOCHS + 1):
        # Resample negatif setiap epoch
        train_dataset.resample()
        loader = DataLoader(
            train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0
        )

        model.train()
        total_loss = 0.0

        for user_ids, item_ids, labels in loader:
            user_ids = user_ids.to(device)
            item_ids = item_ids.to(device)
            labels   = labels.to(device)

            preds = model(user_ids, item_ids)
            loss  = criterion(preds, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        hr, ndcg = evaluate(model, data["test_candidates"], device)

        status = ""
        if hr > best_hr:
            best_hr    = hr
            best_ndcg  = ndcg
            best_epoch = epoch
            status     = "* best"
            torch.save(
                {
                    "epoch":       epoch,
                    "model_state": model.state_dict(),
                    "n_users":     data["n_users"],
                    "n_items":     data["n_items"],
                    "user2idx":    data["user2idx"],
                    "item2idx":    data["item2idx"],
                    "idx2user":    data["idx2user"],
                    "idx2item":    data["idx2item"],
                    "hr_at_10":    hr,
                    "ndcg_at_10":  ndcg,
                },
                MODEL_PATH,
            )

        print(f"{epoch:>6}  {avg_loss:>8.4f}  {hr:>7.4f}  {ndcg:>9.4f}  {status}")

    print("-" * 52)
    print(f"Selesai! Best epoch {best_epoch}: HR@10={best_hr:.4f}, NDCG@10={best_ndcg:.4f}")
    print(f"Model disimpan → {MODEL_PATH}")

    return best_hr, best_ndcg


if __name__ == "__main__":
    train()
