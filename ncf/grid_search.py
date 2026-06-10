"""
Grid search kecil untuk memilih konfigurasi model NCF terbaik.

3 konfigurasi yang diuji (semua share data yang sama agar perbandingan adil):
  A : embed=32, mlp=[64,32,16], dropout=0.2, lr=0.001
  B : embed=16, mlp=[32,16,8],  dropout=0.3, lr=0.001
  C : embed=32, mlp=[64,32],    dropout=0.2, lr=0.0005

Jalankan: python -m ncf.grid_search
"""

import os
from ncf.config import MODEL_DIR, EARLY_STOPPING_PATIENCE
from ncf.dataset import get_data
from ncf.train import train


# ── Definisi grid ─────────────────────────────────────────────────────────────

GRID = [
    {
        "label":       "A",
        "embed_dim":   32,
        "mlp_layers":  [64, 32, 16],
        "dropout":     0.2,
        "lr":          0.001,
        "weight_decay": 1e-5,
        "patience":    EARLY_STOPPING_PATIENCE,
    },
    {
        "label":       "B",
        "embed_dim":   16,
        "mlp_layers":  [32, 16, 8],
        "dropout":     0.3,
        "lr":          0.001,
        "weight_decay": 1e-5,
        "patience":    EARLY_STOPPING_PATIENCE,
    },
    {
        "label":       "C",
        "embed_dim":   32,
        "mlp_layers":  [64, 32],
        "dropout":     0.2,
        "lr":          0.0005,
        "weight_decay": 1e-5,
        "patience":    EARLY_STOPPING_PATIENCE,
    },
]


# ── Jalankan grid search ──────────────────────────────────────────────────────

def run_grid_search():
    print("=" * 70)
    print("  NCF Grid Search — Sakka Base Recommendation System")
    print("=" * 70)

    # Load data sekali, dipakai oleh semua konfigurasi (evaluasi adil)
    print("\nMemuat data dari database (sekali untuk semua konfigurasi)...")
    data = get_data()
    print()

    results = []
    os.makedirs(MODEL_DIR, exist_ok=True)

    for cfg in GRID:
        label      = cfg["label"]
        model_path = os.path.join(MODEL_DIR, f"ncf_config_{label}.pth")

        print(f"\n{'─'*70}")
        print(f"  Konfigurasi {label}: "
              f"embed={cfg['embed_dim']}, mlp={cfg['mlp_layers']}, "
              f"dropout={cfg['dropout']}, lr={cfg['lr']}")
        print(f"{'─'*70}")

        result = train(
            cfg        = cfg,
            data       = data,
            model_path = model_path,
            save_plot  = True,
            verbose    = True,
            label      = f"Config_{label}",
        )
        results.append({
            "label":        label,
            "embed":        cfg["embed_dim"],
            "mlp":          str(cfg["mlp_layers"]),
            "dropout":      cfg["dropout"],
            "lr":           cfg["lr"],
            "best_epoch":   result["best_epoch"],
            "total_epochs": result["total_epochs"],
            "hr_at_10":     result["best_hr"],
            "ndcg_at_10":   result["best_ndcg"],
        })

    # ── Tabel hasil ───────────────────────────────────────────────────────────
    print("\n")
    print("=" * 70)
    print("  HASIL GRID SEARCH")
    print("=" * 70)
    print(f"{'Config':<8} {'Embed':<6} {'MLP':<14} {'Drop':<6} "
          f"{'LR':<8} {'BestEp':>7} {'HR@10':>8} {'NDCG@10':>9}")
    print("-" * 70)

    best_result = max(results, key=lambda x: x["hr_at_10"])
    for r in results:
        marker = " ◄ BEST" if r["label"] == best_result["label"] else ""
        print(f"  {r['label']:<6} {r['embed']:<6} {r['mlp']:<14} "
              f"{r['dropout']:<6} {r['lr']:<8} "
              f"{r['best_epoch']:>7} {r['hr_at_10']:>8.4f} "
              f"{r['ndcg_at_10']:>9.4f}{marker}")

    # ── Rekomendasi ───────────────────────────────────────────────────────────
    b = best_result
    print("\n" + "=" * 70)
    print(f"  REKOMENDASI: Konfigurasi {b['label']}")
    print(f"  HR@10={b['hr_at_10']:.4f}  NDCG@10={b['ndcg_at_10']:.4f}  "
          f"(epoch terbaik: {b['best_epoch']})")
    print()
    print(f"  Update ncf/config.py dengan:")
    best_cfg = next(c for c in GRID if c["label"] == b["label"])
    print(f"    EMBEDDING_DIM = {best_cfg['embed_dim']}")
    print(f"    MLP_LAYERS    = {best_cfg['mlp_layers']}")
    print(f"    DROPOUT       = {best_cfg['dropout']}")
    print(f"    LR            = {best_cfg['lr']}")
    print()
    best_model_path = os.path.join(MODEL_DIR, f"ncf_config_{b['label']}.pth")
    print(f"  Model terbaik tersimpan di: {best_model_path}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_grid_search()
