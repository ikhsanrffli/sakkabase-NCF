#!/usr/bin/env python3
"""
Generator SQL untuk basis data MySQL Sakka Base — SKENARIO B.

Membaca:
  - src/data/initialData.js  (sumber resmi users & menu agar identik dgn aplikasi)
  - src/dataset.xlsx         (untuk mengelompokkan transaksi -> orders/order_details)

Menghasilkan:
  - database/sakkabase_seed.sql

Skema mengikuti rancangan Bab 3.3.2 skripsi: users, menu_items, orders,
order_details, recommendations, model_log.

Catatan:
  - User = Pelanggan asli (sumber 'historical'); admin ditandai 'registered'.
  - menu_items.item_id = KODE produk (141 menu, varian digabung) -> konsisten app.
  - orders = satu No Transaksi; order_details = tiap baris produk.
  - price/total tidak ada di dataset -> diisi 0 (silakan diperbarui kemudian).
  - recommendations dibiarkan kosong (diisi saat inferensi model).
  - model_log diisi satu baris hasil evaluasi (HR@10/NDCG@10).

Jalankan:
  python scripts/export_mysql.py
"""
import os, re, json
import openpyxl
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INIT = os.path.join(ROOT, "src", "data", "initialData.js")
XLSX = os.path.join(ROOT, "src", "dataset.xlsx")
OUTDIR = os.path.join(ROOT, "database")
OUT = os.path.join(OUTDIR, "sakkabase_seed.sql")

# Hasil evaluasi model final (Konfigurasi C, Skenario B) — untuk model_log
HR_AT_10 = 0.3500
NDCG_AT_10 = 0.1822


def parse_initdata():
    """Ambil USERS_DB & MENUS_DATA dari initialData.js (objek JSON per baris)."""
    txt = open(INIT, encoding="utf-8").read()

    def grab(const):
        m = re.search(const + r"\s*=\s*\[(.*?)\];", txt, re.S)
        body = m.group(1)
        out = []
        for line in body.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith("{") and line.endswith("}"):
                out.append(json.loads(line))
        return out

    return grab("USERS_DB"), grab("MENUS_DATA")


def sql_str(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("\\", "\\\\").replace("'", "''") + "'"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    users, menus = parse_initdata()

    # peta id string app -> id int DB, dan nama pelanggan -> id int
    uid_int = {}
    name_to_int = {}
    for n, u in enumerate(users, 1):
        uid_int[u["id"]] = n
        name_to_int[u["name"]] = n

    # peta kode menu -> id int DB
    code_to_int = {}
    for n, m in enumerate(menus, 1):
        code_to_int[m["id"]] = n

    # baca transaksi dari xlsx
    ws = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)["Sheet1"]
    cust = tgl = no = None
    orders = {}          # no_transaksi -> dict(user_int, tanggal)
    details = []         # (no_transaksi, menu_int, qty)
    order_seq = {}       # no_transaksi -> id int berurutan
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        rno, rtgl, _, rpel, rprod, rqty = r[:6]
        if rno not in (None, ""):
            no = str(rno).strip()
        if rtgl not in (None, ""):
            tgl = str(rtgl).strip()
        if rpel not in (None, ""):
            cust = str(rpel).strip()
        if rprod in (None, ""):
            continue
        prod = str(rprod).strip()
        code = prod.split(" - ")[0].strip() if " - " in prod else prod
        if code not in code_to_int:
            continue
        d = ""
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                d = datetime.strptime(tgl, fmt).strftime("%Y-%m-%d"); break
            except Exception:
                pass
        if no not in orders:
            order_seq[no] = len(order_seq) + 1
            orders[no] = dict(user_int=name_to_int.get(cust), tanggal=d)
        try:
            qty = int(float(rqty))
        except Exception:
            qty = 1
        details.append((no, code_to_int[code], qty))

    # ---- tulis SQL ----
    L = []
    L.append("-- Seed basis data Sakka Base (SKENARIO B: User = Pelanggan)")
    L.append("-- AUTO-GENERATED oleh scripts/export_mysql.py — jangan edit manual.")
    L.append("-- PERHATIAN: skrip ini MENGHAPUS tabel lama lalu membuat & mengisi ulang.")
    L.append("SET FOREIGN_KEY_CHECKS = 0;")
    L.append("SET NAMES utf8mb4;")
    L.append("")
    for t in ["model_log", "recommendations", "order_details", "orders",
              "menu_items", "users"]:
        L.append(f"DROP TABLE IF EXISTS `{t}`;")
    L.append("")

    L.append("""CREATE TABLE `users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nama_lengkap` VARCHAR(100) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('admin','user') NOT NULL DEFAULT 'user',
  `source` ENUM('historical','registered') NOT NULL DEFAULT 'historical',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`), UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

    L.append("""CREATE TABLE `menu_items` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `item_id` VARCHAR(100) NOT NULL,
  `nama_menu` VARCHAR(150) NOT NULL,
  `kategori` VARCHAR(100) DEFAULT NULL,
  `price` INT DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`), KEY `item_id` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

    L.append("""CREATE TABLE `orders` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) DEFAULT NULL,
  `total` INT DEFAULT 0,
  `tanggal` DATE DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`), KEY `user_id` (`user_id`),
  CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

    L.append("""CREATE TABLE `order_details` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `menu_item_id` INT NOT NULL,
  `qty` TINYINT DEFAULT 1,
  `price` INT DEFAULT 0,
  PRIMARY KEY (`id`), KEY `order_id` (`order_id`), KEY `menu_item_id` (`menu_item_id`),
  CONSTRAINT `fk_od_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `fk_od_menu` FOREIGN KEY (`menu_item_id`) REFERENCES `menu_items` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

    L.append("""CREATE TABLE `recommendations` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `menu_item_id` INT(11) NOT NULL,
  `rank` TINYINT(4) NOT NULL,
  `score` FLOAT NOT NULL,
  `generated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

    L.append("""CREATE TABLE `model_log` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `status` ENUM('training','ready','error') NOT NULL DEFAULT 'ready',
  `model_path` VARCHAR(255) DEFAULT NULL,
  `hr_at_10` FLOAT DEFAULT NULL,
  `ndcg_at_10` FLOAT DEFAULT NULL,
  `trained_at` DATETIME DEFAULT NULL,
  `error_log` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
    L.append("")

    # users
    L.append("INSERT INTO `users` (`id`,`nama_lengkap`,`username`,`password`,`role`,`source`) VALUES")
    rows = []
    for u in users:
        src = "registered" if u["role"] == "admin" else "historical"
        rows.append(f"({uid_int[u['id']]},{sql_str(u['name'])},{sql_str(u['username'])},"
                    f"{sql_str(u['password'])},{sql_str(u['role'])},{sql_str(src)})")
    L.append(",\n".join(rows) + ";\n")

    # menu_items
    L.append("INSERT INTO `menu_items` (`id`,`item_id`,`nama_menu`,`kategori`,`price`) VALUES")
    rows = [f"({code_to_int[m['id']]},{sql_str(m['id'])},{sql_str(m['name'])},"
            f"{sql_str(m['category'])},0)" for m in menus]
    L.append(",\n".join(rows) + ";\n")

    # orders
    L.append("INSERT INTO `orders` (`id`,`user_id`,`total`,`tanggal`) VALUES")
    rows = []
    for no, o in orders.items():
        uid = o["user_int"] if o["user_int"] else "NULL"
        tg = sql_str(o["tanggal"]) if o["tanggal"] else "NULL"
        rows.append(f"({order_seq[no]},{uid},0,{tg})")
    L.append(",\n".join(rows) + ";\n")

    # order_details
    L.append("INSERT INTO `order_details` (`order_id`,`menu_item_id`,`qty`,`price`) VALUES")
    rows = [f"({order_seq[no]},{mid},{qty},0)" for no, mid, qty in details]
    L.append(",\n".join(rows) + ";\n")

    # model_log
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    L.append("INSERT INTO `model_log` (`status`,`model_path`,`hr_at_10`,`ndcg_at_10`,`trained_at`) VALUES")
    L.append(f"('ready','models/ncf_config_C.pth',{HR_AT_10},{NDCG_AT_10},{sql_str(now)});\n")

    L.append("SET FOREIGN_KEY_CHECKS = 1;")
    open(OUT, "w", encoding="utf-8").write("\n".join(L))

    print(f"OK -> {OUT}")
    print(f"  users        : {len(users)}")
    print(f"  menu_items   : {len(menus)}")
    print(f"  orders       : {len(orders)}")
    print(f"  order_details: {len(details)}")
    miss = sum(1 for o in orders.values() if not o['user_int'])
    print(f"  orders tanpa user terpetakan: {miss}")
    print(f"  ukuran file  : {os.path.getsize(OUT)//1024} KB")


if __name__ == "__main__":
    main()
