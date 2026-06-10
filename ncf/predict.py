"""
Inferensi model NCF: generate Top-10 rekomendasi untuk satu user
dan simpan ke tabel recommendations.

Jalankan: python -m ncf.predict --user_id 1
"""

import argparse

import torch
import mysql.connector

from ncf.config import DB_CONFIG, TOP_K, MODEL_PATH
from ncf.model import NCF


# ── Load model ────────────────────────────────────────────────────────────────

def load_checkpoint(path: str = MODEL_PATH) -> tuple:
    ckpt  = torch.load(path, map_location="cpu")
    model = NCF(ckpt["n_users"], ckpt["n_items"])
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt


# ── Helpers DB ────────────────────────────────────────────────────────────────

def _get_ordered_items(conn, user_id: int) -> set:
    cur = conn.cursor()
    cur.execute("""
        SELECT od.menu_item_id
        FROM   order_details od
        JOIN   orders o ON o.id = od.order_id
        WHERE  o.user_id = %s
    """, (user_id,))
    result = {row[0] for row in cur.fetchall()}
    cur.close()
    return result


# ── Inferensi ─────────────────────────────────────────────────────────────────

def recommend(user_id: int, top_k: int = TOP_K,
              model_path: str = MODEL_PATH) -> list[dict]:
    """
    Generate top_k rekomendasi untuk user_id.

    Returns list of dict: [{"menu_item_id": int, "score": float, "rank": int}, ...]
    List kosong jika user tidak dikenali model (cold-start → tangani di FastAPI).
    """
    model, ckpt = load_checkpoint(model_path)

    user2idx = ckpt["user2idx"]
    item2idx = ckpt["item2idx"]
    idx2item = ckpt["idx2item"]

    if user_id not in user2idx:
        return []   # cold-start — FastAPI akan pakai popularity fallback

    uidx = user2idx[user_id]

    conn          = mysql.connector.connect(**DB_CONFIG)
    ordered_items = _get_ordered_items(conn, user_id)
    conn.close()

    # Semua item yang belum pernah dipesan oleh user ini
    candidate_idxs = [
        iidx for iidx in range(len(item2idx))
        if idx2item[iidx] not in ordered_items
    ]

    if not candidate_idxs:
        return []

    u_tensor = torch.tensor([uidx] * len(candidate_idxs), dtype=torch.long)
    i_tensor = torch.tensor(candidate_idxs,               dtype=torch.long)

    with torch.no_grad():
        scores = model(u_tensor, i_tensor).numpy()

    ranked = sorted(zip(scores, candidate_idxs), key=lambda x: -x[0])[:top_k]

    return [
        {
            "menu_item_id": idx2item[iidx],
            "score":        float(score),
            "rank":         rank + 1,
        }
        for rank, (score, iidx) in enumerate(ranked)
    ]


# ── Simpan ke DB ──────────────────────────────────────────────────────────────

def save_recommendations(user_id: int, recs: list[dict]) -> None:
    """Hapus rekomendasi lama user dan ganti dengan yang baru (full refresh)."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()

    cur.execute("DELETE FROM recommendations WHERE user_id = %s", (user_id,))

    cur.executemany(
        "INSERT INTO recommendations (user_id, menu_item_id, `rank`, score) "
        "VALUES (%s, %s, %s, %s)",
        [(user_id, r["menu_item_id"], r["rank"], r["score"]) for r in recs],
    )
    conn.commit()
    cur.close()
    conn.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate rekomendasi NCF untuk satu user")
    parser.add_argument("--user_id", type=int, required=True, help="MySQL user.id")
    parser.add_argument("--save",    action="store_true",     help="Simpan hasil ke DB")
    args = parser.parse_args()

    recs = recommend(args.user_id)

    if not recs:
        print(f"Tidak ada rekomendasi untuk user_id={args.user_id} "
              "(cold-start atau semua item sudah pernah dipesan)")
    else:
        print(f"Top-{TOP_K} rekomendasi untuk user_id={args.user_id}:")
        for r in recs:
            print(f"  Rank {r['rank']:>2}: menu_item_id={r['menu_item_id']:<4}  "
                  f"score={r['score']:.4f}")

        if args.save:
            save_recommendations(args.user_id, recs)
            print("\nRekomendasi tersimpan ke tabel recommendations.")
