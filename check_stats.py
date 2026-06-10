import sys
import os
sys.path.insert(0, os.getcwd())

import mysql.connector

conn = mysql.connector.connect(
    host='localhost', user='root', password='',
    database='sakkabase_ncf', charset='utf8mb4'
)
cur = conn.cursor()

print("=== STATISTIK DATABASE ===")
queries = [
    ("Total baris order_details",         "SELECT COUNT(*) FROM order_details"),
    ("Total transaksi orders",             "SELECT COUNT(*) FROM orders"),
    ("Users historical",                   "SELECT COUNT(*) FROM users WHERE source='historical'"),
    ("Menu items",                         "SELECT COUNT(*) FROM menu_items"),
    ("Order details dengan qty > 1",       "SELECT COUNT(*) FROM order_details WHERE qty > 1"),
    ("Order details dengan qty = 1",       "SELECT COUNT(*) FROM order_details WHERE qty = 1"),
]
for label, sql in queries:
    cur.execute(sql)
    print(f"  {label:<40}: {cur.fetchone()[0]}")

print()
print("=== STATISTIK NCF DATASET ===")
from ncf.dataset import load_interactions, build_mappings, leave_one_out_split
from collections import defaultdict

rows = load_interactions()
user2idx, item2idx, idx2user, idx2item = build_mappings(rows)
train_data, test_data, user_item_set = leave_one_out_split(rows, user2idx, item2idx)

total_interactions = len(rows)
n_users = len(user2idx)
n_items = len(item2idx)
n_train = len(train_data)
n_test  = len(test_data)

# Users dengan hanya 1 interaksi
only_one = sum(1 for uidx in user_item_set if len(user_item_set[uidx]) < 2)

print(f"  Total interaksi (rows)          : {total_interactions}")
print(f"  Users unik                      : {n_users}")
print(f"  Items unik                      : {n_items}")
print(f"  Rata-rata interaksi per user    : {total_interactions/n_users:.2f}")
print(f"  Train set                       : {n_train} interaksi")
print(f"  Test set                        : {n_test} users")
print(f"  Users dengan 1 interaksi saja   : {only_one}")

cur.close()
conn.close()
