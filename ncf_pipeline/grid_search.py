"""
grid_search.py — Melatih ketiga konfigurasi (A, B, C) lalu menampilkan tabel
perbandingan HR@10 / NDCG@10 (pengganti Tabel 4.8 skripsi).

  python grid_search.py
"""
import config
from dataset import prepare_data
from train import train_config


def main():
    data = prepare_data()
    data.print_stats()

    results = {}
    for name, cfg in config.CONFIGS.items():
        verbose = (name == config.FINAL_CONFIG)
        if verbose:
            print(f"\n--- Detail pelatihan Konfigurasi {name} (final) ---")
        results[name] = train_config(data, cfg, name=name, verbose=verbose,
                                     save=(name == config.FINAL_CONFIG))

    print("\n" + "=" * 72)
    print("PERBANDINGAN KONFIGURASI (Tabel 4.8)")
    print("=" * 72)
    print(f"{'Konf':>4} | {'embed':>5} | {'mlp_layers':>14} | {'drop':>4} | "
          f"{'lr':>6} | {'epoch':>5} | {'HR@10':>7} | {'NDCG@10':>8} | {'param':>6}")
    for name, b in results.items():
        c = config.CONFIGS[name]
        print(f"{name:>4} | {c['embed']:>5} | {str(c['layers']):>14} | {c['dropout']:>4} | "
              f"{c['lr']:>6} | {b['epoch']:>5} | {b['hr']:>7.4f} | {b['ndcg']:>8.4f} | {b['params']:>6}")

    best = max(results, key=lambda k: results[k]["hr"])
    print(f"\nHR@10 tertinggi: Konfigurasi {best} "
          f"({results[best]['hr']:.4f}). Model final skripsi: {config.FINAL_CONFIG}.")


if __name__ == "__main__":
    main()
