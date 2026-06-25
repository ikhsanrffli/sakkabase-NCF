"""
predict.py — Inferensi Top-10 rekomendasi untuk satu pengguna (Tabel 4.12).

Memuat model final tersimpan (models/ncf_config_C.pth) lalu menghitung skor
untuk semua menu yang BELUM pernah dipesan pengguna, dan menampilkan Top-10.

  python predict.py "Rendi Ramadhan"
  python predict.py            # default: pengguna paling aktif
"""
import os, sys
import torch
import config
from dataset import prepare_data
from model import NCF

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def recommend(user_name=None, top_k=None):
    top_k = top_k or config.TOP_K
    data = prepare_data()
    name = config.FINAL_CONFIG
    cfg = config.CONFIGS[name]

    path = os.path.join(config.MODEL_DIR, f"ncf_config_{name}.pth")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model {path} belum ada. Jalankan dulu: python train.py")

    model = NCF(data.n_users, data.n_items, cfg["embed"], cfg["layers"], cfg["dropout"]).to(device)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()

    # pilih pengguna
    if user_name and user_name in data.u2i:
        uidx = data.u2i[user_name]
    else:
        if user_name:
            print(f"[!] '{user_name}' tidak ditemukan, memakai pengguna paling aktif.")
        uidx = int(data.df["u"].value_counts().idxmax())
        user_name = data.users[uidx]

    seen = data.user_items[uidx]
    cand = [j for j in range(data.n_items) if j not in seen]
    with torch.no_grad():
        uu = torch.full((len(cand),), uidx, dtype=torch.long, device=device)
        ii = torch.tensor(cand, dtype=torch.long, device=device)
        sc = model(uu, ii).cpu().numpy()
    top = sorted(zip(cand, sc), key=lambda x: -x[1])[:top_k]

    print("=" * 56)
    print(f"TOP-{top_k} REKOMENDASI — '{user_name}' (indeks {uidx})")
    print("=" * 56)
    print(f"{'Rank':>4} | {'Kode':>6} | {'Skor':>7}")
    for r, (j, s) in enumerate(top, 1):
        print(f"{r:>4} | {data.code_of[j]:>6} | {s:>7.4f}")
    return [(r + 1, data.code_of[j], float(s)) for r, (j, s) in enumerate(top)]


if __name__ == "__main__":
    recommend(sys.argv[1] if len(sys.argv) > 1 else None)
