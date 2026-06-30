"""
export_recommendations.py — Precompute Top-10 rekomendasi NYATA dari model final
untuk SEMUA pengguna aplikasi, lalu simpan ke src/data/recommendations.json.

Tujuan: agar halaman Rekomendasi di aplikasi React menampilkan skor asli dari
model NCF (bukan simulasi), konsisten dengan Tabel 4.12 skripsi.

Keluaran JSON: { "u1": [{"menuId":"A00A","score":0.5413}, ...], ... }
  - Pengguna yang ada di model (≥2 interaksi): skor asli model.
  - Pengguna terfilter (<2 interaksi): fallback berbasis popularitas global.

  python export_recommendations.py   (jalankan setelah train.py)
"""
import os, re, json
from collections import Counter
import torch
import config
from dataset import prepare_data, load_interactions
from model import NCF

ROOT = config.ROOT
INIT = os.path.join(ROOT, "src", "data", "initialData.js")
OUT = os.path.join(ROOT, "src", "data", "recommendations.json")
TOP_K = config.TOP_K


def parse_users():
    txt = open(INIT, encoding="utf-8").read()
    m = re.search(r"USERS_DB\s*=\s*\[(.*?)\];", txt, re.S)
    users = []
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{"):
            users.append(json.loads(line))
    return users


def main():
    app_users = parse_users()
    data = prepare_data()
    cfg = config.CONFIGS[config.FINAL_CONFIG]

    model = NCF(data.n_users, data.n_items, cfg["embed"], cfg["layers"], cfg["dropout"])
    mp = os.path.join(config.MODEL_DIR, f"ncf_config_{config.FINAL_CONFIG}.pth")
    if not os.path.exists(mp):
        raise FileNotFoundError(f"{mp} belum ada. Jalankan: python train.py")
    model.load_state_dict(torch.load(mp, map_location="cpu"))
    model.eval()

    # popularitas global + riwayat tiap pelanggan (dari SEMUA data, sebelum filter)
    full = load_interactions()
    pop = [c for c, _ in Counter(full["item"]).most_common()]
    hist = full.groupby("user")["item"].apply(set).to_dict()

    def model_top(uidx, seen):
        cand = [j for j in range(data.n_items) if j not in seen]
        with torch.no_grad():
            uu = torch.full((len(cand),), uidx, dtype=torch.long)
            ii = torch.tensor(cand)
            sc = model(uu, ii).numpy()
        top = sorted(zip(cand, sc), key=lambda x: -x[1])[:TOP_K]
        return [{"menuId": data.code_of[j], "score": round(float(s), 4)} for j, s in top]

    def pop_top(name):
        seen = hist.get(name, set())
        out = []
        for c in pop:
            if c in seen:
                continue
            out.append({"menuId": c, "score": round(0.50 - 0.01 * len(out), 4)})
            if len(out) >= TOP_K:
                break
        return out

    recs = {}
    n_model = n_pop = 0
    for u in app_users:
        if u["role"] == "admin":
            continue
        name = u["name"]
        if name in data.u2i:
            recs[u["id"]] = model_top(data.u2i[name], data.user_items[data.u2i[name]])
            n_model += 1
        else:
            recs[u["id"]] = pop_top(name)
            n_pop += 1

    json.dump(recs, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"OK -> {OUT}")
    print(f"  pengguna model (skor asli) : {n_model}")
    print(f"  pengguna fallback popular   : {n_pop}")
    print(f"  contoh u1 (Jenny Sanjaya)   : {recs.get('u1', [])[:3]}")


if __name__ == "__main__":
    main()
