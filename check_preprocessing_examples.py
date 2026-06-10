"""
Script untuk mengambil contoh nyata dari setiap tahapan preprocessing
agar bisa digunakan sebagai tabel di skripsi BAB IV.
"""

import sys, os
sys.path.insert(0, os.getcwd())

import mysql.connector
from ncf.dataset import load_interactions, build_mappings, leave_one_out_split
from ncf.config  import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cur  = conn.cursor()

rows = load_interactions()
user2idx, item2idx, idx2user, idx2item = build_mappings(rows)
train_data, test_data, user_item_set   = leave_one_out_split(rows, user2idx, item2idx)

# ── Tabel 1: Label Encoding — 5 user + 5 item pertama ──────────────────────
print("=" * 70)
print("TABEL: LABEL ENCODING — PENGGUNA")
print("=" * 70)
print(f"{'No':<4} {'user_id (MySQL)':<18} {'Nama Pengguna':<35} {'Indeks Encoding'}")
print("-" * 70)

# Ambil 5 user pertama berdasarkan indeks encoding
sample_users = sorted(user2idx.items(), key=lambda x: x[1])[:5]
for db_uid, idx in sample_users:
    cur.execute("SELECT nama_lengkap FROM users WHERE id = %s", (db_uid,))
    row = cur.fetchone()
    nama = row[0] if row else "—"
    print(f"{idx+1:<4} {db_uid:<18} {nama:<35} {idx}")

print()
print("=" * 70)
print("TABEL: LABEL ENCODING — ITEM MENU")
print("=" * 70)
print(f"{'No':<4} {'menu_item_id (MySQL)':<22} {'item_id':<40} {'Indeks Encoding'}")
print("-" * 70)

sample_items = sorted(item2idx.items(), key=lambda x: x[1])[:5]
for db_iid, idx in sample_items:
    cur.execute("SELECT item_id FROM menu_items WHERE id = %s", (db_iid,))
    row = cur.fetchone()
    item_id = row[0] if row else "—"
    print(f"{idx+1:<4} {db_iid:<22} {item_id:<40} {idx}")

# ── Tabel 2: Implicit Feedback — ambil user nyata dengan interaksinya ───────
print()
print("=" * 70)
print("TABEL: CONTOH IMPLICIT FEEDBACK (user index 0)")
print("=" * 70)

# Ambil semua item yang dipesan user index 0
uid_0_db = idx2user[0]
pos_items = sorted(user_item_set[0])[:3]  # 3 item positif

# Ambil 2 item yang TIDAK pernah dipesan (negatif)
all_items = set(range(len(item2idx)))
neg_items = sorted(all_items - user_item_set[0])[:2]

print(f"{'User Index':<12} {'Item Index':<12} {'Label':<8} {'Keterangan'}")
print("-" * 70)
for iidx in pos_items:
    db_iid = idx2item[iidx]
    cur.execute("SELECT item_id, nama_menu FROM menu_items WHERE id = %s", (db_iid,))
    row = cur.fetchone()
    nama = row[1][:30] if row else "—"
    print(f"{'0':<12} {iidx:<12} {'1':<8} Pernah dipesan: {nama}")

for iidx in neg_items:
    db_iid = idx2item[iidx]
    cur.execute("SELECT item_id, nama_menu FROM menu_items WHERE id = %s", (db_iid,))
    row = cur.fetchone()
    nama = row[1][:30] if row else "—"
    print(f"{'0':<12} {iidx:<12} {'0':<8} Tidak pernah dipesan: {nama}")

# ── Tabel 3: Negative Sampling nyata ────────────────────────────────────────
print()
print("=" * 70)
print("TABEL: CONTOH NEGATIVE SAMPLING 4:1 (user index 0, item positif pertama)")
print("=" * 70)

import random
random.seed(42)

pos_iidx = list(user_item_set[0])[0]
db_pos   = idx2item[pos_iidx]
cur.execute("SELECT nama_menu FROM menu_items WHERE id = %s", (db_pos,))
pos_nama = cur.fetchone()[0][:35]

neg_pool = list(all_items - user_item_set[0])
random.shuffle(neg_pool)
neg_samples = neg_pool[:4]

print(f"{'No':<4} {'User':<6} {'Item Index':<12} {'Nama Menu':<40} {'Label':<6} {'Jenis'}")
print("-" * 80)
print(f"{'1':<4} {'0':<6} {pos_iidx:<12} {pos_nama:<40} {'1':<6} Positif")
for i, iidx in enumerate(neg_samples, 2):
    db_iid = idx2item[iidx]
    cur.execute("SELECT nama_menu FROM menu_items WHERE id = %s", (db_iid,))
    nama = cur.fetchone()[0][:35]
    print(f"{i:<4} {'0':<6} {iidx:<12} {nama:<40} {'0':<6} Negatif")

# ── Tabel 4: Leave-One-Out Split nyata ──────────────────────────────────────
print()
print("=" * 70)
print("TABEL: CONTOH LEAVE-ONE-OUT SPLIT (3 user nyata)")
print("=" * 70)
print(f"{'User Idx':<10} {'Total Interaksi':<18} {'Data Latih':<14} {'Data Uji (item terakhir)'}")
print("-" * 70)

# Cari 2 user yang masuk test, 1 yang tidak
test_uids   = sorted(test_data.keys())[:2]
nottest_uid = next(u for u in user_item_set if u not in test_data)

for uidx in test_uids + [nottest_uid]:
    total = len(list(filter(lambda x: x[0] == uidx, rows)))  # slow but ok for example
    db_uid = idx2user[uidx]
    # count actual interactions
    cur.execute("""
        SELECT COUNT(*) FROM order_details od
        JOIN orders o ON o.id = od.order_id
        WHERE o.user_id = %s
    """, (db_uid,))
    total_actual = cur.fetchone()[0]

    if uidx in test_data:
        test_iidx = test_data[uidx]
        db_tiid   = idx2item[test_iidx]
        cur.execute("SELECT nama_menu FROM menu_items WHERE id = %s", (db_tiid,))
        test_nama = cur.fetchone()[0][:30]
        print(f"{uidx:<10} {total_actual:<18} {total_actual-1:<14} {test_nama}")
    else:
        print(f"{uidx:<10} {total_actual:<18} {total_actual:<14} — (tidak dievaluasi)")

cur.close()
conn.close()
print()
print("Selesai.")
