"""
Import data dari Detil_Penjualan.xlsx ke database sakkabase_ncf.

Jalankan setelah schema.sql dieksekusi:
    python database/import_data.py

Env vars (opsional):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    EXCEL_PATH  — path ke file Excel
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl belum terinstall. Jalankan: pip install openpyxl")

try:
    import mysql.connector
except ImportError:
    sys.exit("mysql-connector-python belum terinstall. Jalankan: pip install mysql-connector-python")


# ── Konfigurasi ──────────────────────────────────────────────────────────────

EXCEL_PATH = os.environ.get("EXCEL_PATH", "src/Detil_Penjualan).xlsx")

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "localhost"),
    "port":     int(os.environ.get("DB_PORT", "3306")),
    "database": os.environ.get("DB_NAME",     "sakkabase_ncf"),
    "user":     os.environ.get("DB_USER",     "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "charset":  "utf8mb4",
}

KATEGORI_MAP = {
    "A": "Minuman",
    "C": "Makanan",
    "D": "Ice Cream",
    "P": "Paket",
}

# ── Estimasi Harga (Rupiah) ───────────────────────────────────────────────────
# Kunci = 4-char kode item (A01G, B01A, dll)
# Fallback: 3-char prefix → 2-char prefix → huruf pertama

PRICE_LOOKUP = {
    # ── Minuman ───────────────────────────────────────────────────────────────
    # Americano (A00x)
    "A00": 22000,
    # Espresso & Milk-based (A01x)
    "A01A": 18000, "A01C": 28000, "A01D": 28000, "A01E": 28000,
    "A01F": 32000, "A01G": 30000, "A01H": 28000, "A01I": 30000,
    "A01J": 30000, "A01K": 32000, "A01L": 32000, "A01M": 32000,
    "A01N": 32000, "A01O": 35000,
    # Signature Cold Latte (A02x)
    "A02A": 30000, "A02B": 32000, "A02C": 32000, "A02D": 32000,
    "A02E": 34000, "A02F": 34000, "A02G": 34000, "A02H": 34000,
    "A02I": 35000,
    # Cream Series (A03x)
    "A03": 38000,
    # Frappe (A04x)
    "A04A": 35000, "A04B": 36000, "A04C": 35000, "A04D": 35000,
    "A04E": 36000, "A04F": 36000, "A04G": 36000,
    # Non-Kopi (A05x)
    "A05A": 28000, "A05C": 28000, "A05D": 28000, "A05E": 30000,
    "A05F": 25000, "A05G": 32000,
    # Juice (A06x)
    "A06A": 22000, "A06B": 22000, "A06C": 25000, "A06D": 20000,
    "A06E": 20000, "A06F": 22000, "A06G": 22000, "A06H": 15000,
    # Air Mineral (A07x)
    "A07B": 8000,
    # Tea (A08x)
    "A08A": 10000, "A08B": 12000, "A08C": 15000, "A08D": 15000,
    "A08E": 15000, "A08F": 15000,
    # Croissant & Pastry (A09x)
    "A09A": 28000, "A09B": 30000, "A09C": 30000, "A09D": 30000,
    "A09E": 32000, "A09F": 32000, "A09G": 32000, "A09H": 32000,
    "A09I": 42000,
    # Pudding (A10x)
    "A10": 20000,
    # Snack Ringan (A11x)
    "A11A": 12000, "A11C": 10000, "A11E": 10000,
    # Cheesecake (A12x)
    "A12A": 32000,
    # Matcha (A13x)
    "A13A": 30000, "A13B": 32000, "A13C": 32000,
    # Lainnya
    "AA01": 120000, "AR12": 28000,

    # ── Barber ────────────────────────────────────────────────────────────────
    "B01A": 35000,  "B01B": 55000,  "B01C": 80000,
    "B01D": 110000, "B01E": 135000, "B01F": 0,
    "B02A": 75000,  "B02B": 65000,  "B02C": 55000,
    "B02D": 45000,  "B02E": 35000,  "B02F": 40000,
    "B03A": 120000, "B03B": 200000, "B03C": 175000, "B03D": 90000,
    "B04A": 185000, "B04B": 250000, "B04C": 65000,
    "B05A": 35000,  "B05B": 35000,  "B05C": 35000,  "B05D": 15000,

    # ── Makanan ───────────────────────────────────────────────────────────────
    # Gorengan & Snack (C01x)
    "C01":  25000,
    "C01A": 22000, "C01B": 18000, "C01C": 18000, "C01D": 25000,
    "C01E": 20000, "C01F": 18000, "C01G": 22000, "C01H": 25000,
    "C01I": 18000, "C01J": 25000, "C01K": 18000, "C01L": 25000,
    "C01M": 22000, "C01N": 28000, "C01O": 55000, "C01P": 22000,
    # Toast (C02x)
    "C02A": 25000, "C02B": 22000, "C02C": 25000, "C02D": 32000,
    # Nasi Goreng (C03x)
    "C03A": 25000, "C03B": 28000, "C03C": 32000, "C03D": 28000,
    "C03E": 30000, "C03F": 25000,
    # Nasi Lauk (C04x)
    "C04A": 32000, "C04B": 30000, "C04C": 28000, "C04D": 30000,
    "C04E": 32000, "C04F": 35000, "C04G": 38000, "C04H": 35000,
    "C04I": 42000, "C04J": 40000,
    # Mie & Bihun (C05x)
    "C05A": 22000, "C05B": 22000, "C05C": 28000,
    "C05D": 28000, "C05F": 32000,
    # Pasta (C06x)
    "C06A": 40000, "C06B": 45000, "C06C": 48000,
    "C06D": 45000, "C06E": 52000,
    # Indomie (C07x)
    "C07A": 15000, "C07B": 15000, "C07C": 18000,
    # Chicken Steak (C08x)
    "C08A": 48000, "C08B": 52000, "C08C": 48000, "C08D": 52000,
    "C08E": 55000, "C08F": 55000, "C08G": 55000,
    # Salad (C09x)
    "C09A": 32000, "C09B": 35000, "C09C": 28000, "C09D": 22000,
    # Ricebowl (C10x)
    "C10A": 32000, "C10B": 35000, "C10C": 32000, "C10D": 35000,
    # Sayur (C11x)
    "C11A": 20000, "C11B": 15000, "C11C": 18000,
    # Tambahan (CAxx)
    "CA01": 5000,  "CA02": 5000,  "CA03": 3000,  "CA04": 3000,
    "CA05": 15000, "CA06": 5000,  "CA07": 8000,  "CA08": 8000,
    "CA09": 8000,  "CA10": 10000,

    # ── Ice Cream (D01x) ──────────────────────────────────────────────────────
    "D01A": 22000, "D01B": 22000, "D01C": 22000, "D01D": 20000,
    "D01E": 22000, "D01F": 20000, "D01G": 22000, "D01H": 20000,
    "D01I": 18000, "D01J": 20000,
}

# Default harga berdasarkan huruf pertama item_id
_CATEGORY_DEFAULT = {"A": 20000, "B": 50000, "C": 25000, "D": 20000}


def get_price(item_id: str) -> int:
    """Estimasi harga berdasarkan kode item (prefix 4-char, 3-char, lalu huruf pertama)."""
    m = re.match(r'^([A-Z]{1,2}\d{1,2}[A-Z]?)', item_id.upper())
    if not m:
        return 0
    code = m.group(1)
    for length in (len(code), len(code) - 1, 2, 1):
        prefix = code[:length]
        if prefix in PRICE_LOOKUP:
            return PRICE_LOOKUP[prefix]
    return _CATEGORY_DEFAULT.get(code[0].upper(), 15000)


# ── Helper functions ──────────────────────────────────────────────────────────

def parse_produk(produk_str: str) -> tuple:
    """
    Parse string produk POS → (item_id, nama_menu, kategori, price).
    item_id = string penuh, e.g. 'A01G - CAFE LATTE / COLD LARGE'
    """
    produk_str = produk_str.strip()
    first_char = produk_str[0].upper() if produk_str else ""
    kategori   = KATEGORI_MAP.get(first_char, "Lainnya")
    price      = get_price(produk_str)

    if " - " in produk_str:
        _, nama_menu = produk_str.split(" - ", 1)
        return produk_str, nama_menu.strip(), kategori, price

    return produk_str, produk_str, kategori, price


def parse_tanggal(raw) -> "datetime.date | None":
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw).strip(), "%d/%m/%Y %H:%M").date()
    except ValueError:
        return None


# ── Load Excel ────────────────────────────────────────────────────────────────

def load_excel(path: str) -> list[dict]:
    print(f"[1/4] Membaca file: {path}")
    if not os.path.exists(path):
        sys.exit(f"File tidak ditemukan: {path}")

    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active

    rows = []
    current_no_trans = None
    current_tanggal  = None

    for row in ws.iter_rows(min_row=2, values_only=True):
        no_trans_raw = str(row[0]).strip() if row[0] else ""
        tanggal_raw  = str(row[1]).strip() if row[1] else ""
        produk_raw   = str(row[4]).strip() if row[4] else ""

        if no_trans_raw:
            current_no_trans = no_trans_raw
            current_tanggal  = parse_tanggal(tanggal_raw)

        if not current_no_trans or not produk_raw:
            continue

        # Coba baca qty dari kolom ke-6 (index 5), fallback ke 1
        try:
            qty = int(float(str(row[5]))) if row[5] else 1
            qty = max(1, qty)
        except (ValueError, TypeError):
            qty = 1

        rows.append({
            "no_trans": current_no_trans,
            "tanggal":  current_tanggal,
            "produk":   produk_raw,
            "qty":      qty,
        })

    wb.close()
    print(f"    {len(rows)} baris item dimuat")
    return rows


# ── Import ke MySQL ───────────────────────────────────────────────────────────

def import_to_db(rows: list[dict]) -> None:
    print("[2/4] Menghubungkan ke database ...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        sys.exit(f"Gagal koneksi ke database: {e}")

    cur = conn.cursor()

    # ── 1. users (historical) ────────────────────────────────────────────────
    print("[3/4] Insert users, menu_items, orders, order_details ...")
    unique_trans = {r["no_trans"] for r in rows}

    cur.executemany(
        "INSERT IGNORE INTO users (nama_lengkap, username, password, role, source) "
        "VALUES (%s, %s, NULL, %s, %s)",
        [(f"No. Transaksi {nt}", nt, "user", "historical") for nt in unique_trans],
    )
    conn.commit()

    cur.execute("SELECT id, username FROM users WHERE source = 'historical'")
    user_id_map = {username: uid for uid, username in cur.fetchall()}
    print(f"    {len(user_id_map)} users (historical)")

    # ── 2. menu_items (dengan price) ─────────────────────────────────────────
    unique_produk = {r["produk"] for r in rows}
    menu_rows = []
    for produk in unique_produk:
        item_id, nama_menu, kategori, price = parse_produk(produk)
        menu_rows.append((item_id, nama_menu, kategori, price))

    cur.executemany(
        "INSERT IGNORE INTO menu_items (item_id, nama_menu, kategori, price) "
        "VALUES (%s, %s, %s, %s)",
        menu_rows,
    )
    conn.commit()

    cur.execute("SELECT id, item_id FROM menu_items")
    menu_id_map    = {item_id: mid  for mid, item_id in cur.fetchall()}
    menu_price_map = {}
    cur.execute("SELECT item_id, price FROM menu_items")
    menu_price_map = {item_id: price for item_id, price in cur.fetchall()}
    print(f"    {len(menu_id_map)} menu_items")

    # ── 3. orders + order_details ─────────────────────────────────────────────
    # Kelompokkan baris berdasarkan no_trans
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["no_trans"]].append(r)

    order_count  = 0
    detail_count = 0
    skipped      = 0

    for no_trans, items in grouped.items():
        user_id = user_id_map.get(no_trans)
        tanggal = items[0]["tanggal"]

        if not user_id or not tanggal:
            skipped += len(items)
            continue

        # Hitung total harga transaksi
        total = 0
        valid_items = []
        for item in items:
            item_id, _, _, _ = parse_produk(item["produk"])
            mid   = menu_id_map.get(item_id)
            price = menu_price_map.get(item_id, 0)
            qty   = item.get("qty", 1)
            if mid:
                total += price * qty
                valid_items.append((mid, qty, price))

        if not valid_items:
            skipped += len(items)
            continue

        # Insert satu baris orders
        cur.execute(
            "INSERT INTO orders (user_id, tanggal, total) VALUES (%s, %s, %s)",
            (user_id, tanggal, total),
        )
        order_id = cur.lastrowid
        order_count += 1

        # Insert order_details
        cur.executemany(
            "INSERT INTO order_details (order_id, menu_item_id, qty, price) "
            "VALUES (%s, %s, %s, %s)",
            [(order_id, mid, qty, price) for mid, qty, price in valid_items],
        )
        detail_count += len(valid_items)

    conn.commit()
    print(f"    {order_count} orders  |  {detail_count} order_details  "
          f"({skipped} baris dilewati)")

    cur.close()
    conn.close()


# ── Verifikasi ────────────────────────────────────────────────────────────────

def verify() -> None:
    print("\n── Verifikasi ──────────────────────────────────────────────────────")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"Tidak bisa koneksi untuk verifikasi: {e}")
        return

    cur = conn.cursor()
    queries = [
        ("users (historical)", "SELECT COUNT(*) FROM users WHERE source = 'historical'"),
        ("menu_items",         "SELECT COUNT(*) FROM menu_items"),
        ("orders",             "SELECT COUNT(*) FROM orders"),
        ("order_details",      "SELECT COUNT(*) FROM order_details"),
        ("menu_items (harga>0)", "SELECT COUNT(*) FROM menu_items WHERE price > 0"),
    ]

    for label, sql in queries:
        cur.execute(sql)
        count = cur.fetchone()[0]
        print(f"  {label:<30} {count:>6}")

    # Contoh harga
    cur.execute("SELECT item_id, nama_menu, price FROM menu_items "
                "WHERE price > 0 ORDER BY RAND() LIMIT 5")
    print("\n  Contoh harga (5 random):")
    for item_id, nama, price in cur.fetchall():
        print(f"    {item_id:<40} {nama:<30} Rp {price:>7,}")

    cur.close()
    conn.close()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rows = load_excel(EXCEL_PATH)
    import_to_db(rows)
    verify()
