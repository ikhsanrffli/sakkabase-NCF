"""
Backend FastAPI — Sistem Rekomendasi NCF Sakka Base.

Menyediakan rekomendasi NCF real-time untuk user (termasuk USER BARU lewat
teknik *fold-in*) sekaligus evaluasi HR@10 & NDCG@10 secara leave-one-out.

Alur skenario pengujian:
  user baru pesan beberapa menu (urut) -> kirим ke /recommend ->
  backend menyembunyikan pesanan TERAKHIR (ground truth) ->
  melatih embedding user baru (fold-in, item-embedding & MLP dibekukan) ->
  hasilkan Top-10 + skor -> hitung HR@10 & NDCG@10 -> kembalikan ke website.

Jalankan:
  pip install fastapi "uvicorn[standard]" torch pandas scikit-learn numpy openpyxl
  # pastikan model sudah ada: cd ncf_pipeline && python train.py
  cd backend && uvicorn main:app --reload --port 8000
"""
import os, sys, re, json, math, random
import torch
import torch.nn as nn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PIPELINE = os.path.join(ROOT, "ncf_pipeline")
sys.path.insert(0, PIPELINE)

import config                       # noqa: E402
from dataset import prepare_data    # noqa: E402
from model import NCF               # noqa: E402

TOP_K = config.TOP_K
EMBED = config.CONFIGS[config.FINAL_CONFIG]["embed"]

# ---- Muat data, model, metadata menu saat startup ----
print("[backend] menyiapkan data & model ...")
DATA = prepare_data()
CFG = config.CONFIGS[config.FINAL_CONFIG]
MODEL = NCF(DATA.n_users, DATA.n_items, CFG["embed"], CFG["layers"], CFG["dropout"])
_mp = os.path.join(config.MODEL_DIR, f"ncf_config_{config.FINAL_CONFIG}.pth")
if not os.path.exists(_mp):
    raise SystemExit(f"Model {_mp} belum ada. Jalankan: cd ncf_pipeline && python train.py")
MODEL.load_state_dict(torch.load(_mp, map_location="cpu"))
MODEL.eval()
for p in MODEL.parameters():
    p.requires_grad_(False)         # bekukan seluruh model (fold-in hanya latih user baru)


def _load_menu_meta():
    txt = open(os.path.join(ROOT, "src", "data", "initialData.js"), encoding="utf-8").read()
    m = re.search(r"MENUS_DATA\s*=\s*\[(.*?)\];", txt, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{"):
            o = json.loads(line)
            meta[o["id"]] = o
    return meta


MENU = _load_menu_meta()
print(f"[backend] siap. {DATA.n_users} user, {DATA.n_items} item, model {config.FINAL_CONFIG}.")


def forward_with_user(user_vec, item_idx):
    """Skor sigmoid untuk daftar item memakai vektor user kustom (fold-in)."""
    ue = user_vec.unsqueeze(0).expand(item_idx.size(0), -1)
    ie = MODEL.item_emb(item_idx)
    x = torch.cat([ue, ie], dim=-1)
    return torch.sigmoid(MODEL.out(MODEL.mlp(x))).squeeze(-1)


def fold_in(pos_idx, epochs=120, lr=0.05, neg_ratio=4):
    """Latih SATU embedding user baru dari item yang pernah dipesan."""
    pos_set = set(pos_idx)
    user_vec = torch.nn.Parameter(torch.randn(EMBED) * 0.01)
    opt = torch.optim.Adam([user_vec], lr=lr)
    bce = nn.BCELoss()
    for _ in range(epochs):
        items, labels = [], []
        for p in pos_idx:
            items.append(p); labels.append(1.0)
            for _ in range(neg_ratio):
                j = random.randint(0, DATA.n_items - 1)
                while j in pos_set:
                    j = random.randint(0, DATA.n_items - 1)
                items.append(j); labels.append(0.0)
        it = torch.tensor(items, dtype=torch.long)
        lb = torch.tensor(labels, dtype=torch.float)
        opt.zero_grad()
        loss = bce(forward_with_user(user_vec, it), lb)
        loss.backward(); opt.step()
    return user_vec.detach()


class RecRequest(BaseModel):
    orders: list[str]            # kode menu, urut kronologis (terakhir = ground truth)
    evaluate: bool = True        # True: sembunyikan pesanan terakhir untuk uji HR/NDCG


app = FastAPI(title="Sakka Base NCF API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "users": DATA.n_users, "items": DATA.n_items,
            "model": config.FINAL_CONFIG, "hr_at_10": 0.3439, "ndcg_at_10": 0.1825}


@app.post("/recommend")
def recommend(req: RecRequest):
    # ambil kode valid, dedupe jaga urutan
    seen, codes = set(), []
    for c in req.orders:
        c = c.strip()
        if c in DATA.i2i and c not in seen:
            seen.add(c); codes.append(c)

    if len(codes) == 0:
        return {"error": "Tidak ada riwayat menu yang dikenal model.",
                "top10": [], "evaluation": None}

    # Leave-One-Out: sembunyikan pesanan terakhir sebagai ground truth
    ground_truth = None
    if req.evaluate and len(codes) >= 2:
        ground_truth = codes[-1]
        history = codes[:-1]
    else:
        history = codes

    pos_idx = [DATA.i2i[c] for c in history]
    user_vec = fold_in(pos_idx)

    # kandidat = semua item yang TIDAK dipakai untuk fold-in
    hist_set = set(pos_idx)
    cand = [j for j in range(DATA.n_items) if j not in hist_set]
    with torch.no_grad():
        scores = forward_with_user(user_vec, torch.tensor(cand, dtype=torch.long)).numpy()
    ranked = sorted(zip(cand, scores), key=lambda x: -x[1])

    top10 = []
    for j, s in ranked[:TOP_K]:
        code = DATA.code_of[j]
        meta = MENU.get(code, {})
        top10.append({"menuId": code, "name": meta.get("name", code),
                      "category": meta.get("category", "-"),
                      "icon": meta.get("icon", "🍽️"), "score": round(float(s), 4)})

    evaluation = None
    if ground_truth is not None:
        gt_idx = DATA.i2i[ground_truth]
        # peringkat ground truth di antara seluruh kandidat (1-indeks)
        rank = next((r for r, (j, _) in enumerate(ranked, 1) if j == gt_idx), None)
        hit = 1 if (rank is not None and rank <= TOP_K) else 0
        ndcg = (1.0 / math.log2(rank + 1)) if hit else 0.0
        gt_meta = MENU.get(ground_truth, {})
        evaluation = {
            "groundTruth": ground_truth,
            "groundTruthName": gt_meta.get("name", ground_truth),
            "rank": rank, "hit": hit,
            "hr_at_10": hit,
            "ndcg_at_10": round(ndcg, 4),
        }

    return {"top10": top10, "evaluation": evaluation,
            "historyUsed": history, "groundTruth": ground_truth}


# ============================================================
#  Persistensi MySQL (write-through): registrasi & pemesanan
# ============================================================
from datetime import date as _date, datetime as _dt   # noqa: E402
from db import get_session, User, MenuItem, Order, OrderDetail   # noqa: E402


class RegisterReq(BaseModel):
    nama_lengkap: str
    username: str
    password: str


class OrderReq(BaseModel):
    username: str
    menuCodes: list[str]
    tanggal: str | None = None


@app.get("/db/health")
def db_health():
    try:
        s = get_session()
        n = s.query(User).count()
        s.close()
        return {"status": "ok", "users_in_db": n}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/db/register")
def db_register(req: RegisterReq):
    s = get_session()
    try:
        if s.query(User).filter(User.username == req.username).first():
            return {"ok": False, "message": "Username sudah digunakan."}
        u = User(nama_lengkap=req.nama_lengkap, username=req.username,
                 password=req.password, role="user", source="registered")
        s.add(u); s.commit(); s.refresh(u)
        return {"ok": True, "id": u.id, "username": u.username, "name": u.nama_lengkap}
    except Exception as e:
        s.rollback()
        return {"ok": False, "message": str(e)}
    finally:
        s.close()


@app.post("/db/order")
def db_order(req: OrderReq):
    s = get_session()
    try:
        u = s.query(User).filter(User.username == req.username).first()
        if not u:
            return {"ok": False, "message": "User tidak ditemukan di database."}
        tgl = _date.today()
        if req.tanggal:
            try:
                tgl = _dt.strptime(req.tanggal, "%Y-%m-%d").date()
            except Exception:
                pass
        order = Order(user_id=u.id, total=0, tanggal=tgl)
        s.add(order); s.flush()      # dapatkan order.id sebelum commit
        saved = 0
        for code in req.menuCodes:
            mi = s.query(MenuItem).filter(MenuItem.item_id == code).first()
            if mi:
                s.add(OrderDetail(order_id=order.id, menu_item_id=mi.id, qty=1, price=0))
                saved += 1
        s.commit()
        return {"ok": True, "orderId": order.id, "itemsSaved": saved}
    except Exception as e:
        s.rollback()
        return {"ok": False, "message": str(e)}
    finally:
        s.close()


@app.get("/db/users")
def db_users(limit: int = 20):
    s = get_session()
    try:
        rows = s.query(User).order_by(User.id.desc()).limit(limit).all()
        return [{"id": u.id, "name": u.nama_lengkap, "username": u.username,
                 "role": u.role, "source": u.source} for u in rows]
    finally:
        s.close()
