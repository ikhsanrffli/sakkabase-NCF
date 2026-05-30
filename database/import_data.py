"""
Import data dari Detil_Penjualan.xlsx ke database sakkabase_ncf.

Jalankan setelah schema.sql dieksekusi:
    python database/import_data.py

Env vars (opsional, ada nilai default):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    EXCEL_PATH  — path ke file Excel (default: src/Detil_Penjualan).xlsx)
"""

import os
import sys
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

# Mapping huruf pertama item_id → kategori
KATEGORI_MAP = {
    "A": "Minuman",
    "C": "Makanan",
    "D": "Ice Cream",
    "P": "Paket",
}


# ── Helper functions ──────────────────────────────────────────────────────────

def parse_produk(produk_str: str) -> tuple[str, str, str]:
    """
    Parsing string produk dari POS.

    Format POS: 'A01G - CAFE LATTE / COLD LARGE'
    Returns: (item_id, nama_menu, kategori)
      - item_id   = string penuh, contoh: 'A01G - CAFE LATTE / COLD LARGE'
      - nama_menu = bagian setelah ' - ', contoh: 'CAFE LATTE / COLD REGULAR'
      - kategori  = derived dari huruf pertama
    """
    produk_str = produk_str.strip()
    first_char = produk_str[0].upper() if produk_str else ""
    kategori = KATEGORI_MAP.get(first_char, "Lainnya")

    if " - " in produk_str:
        _, nama_menu = produk_str.split(" - ", 1)
        return produk_str, nama_menu.strip(), kategori

    return produk_str, produk_str, kategori


def parse_tanggal(raw) -> "datetime.date | None":
    """Parse string 'DD/MM/YYYY HH:MM' → date object."""
    if not raw:
        return None
    try:
        return datetime.strptime(str(raw).strip(), "%d/%m/%Y %H:%M").date()
    except ValueError:
        return None


# ── Load Excel ────────────────────────────────────────────────────────────────

def load_excel(path: str) -> list[dict]:
    """
    Baca semua baris dari Excel dan kembalikan list of dict.
    Kolom No Transaksi dan Tanggal di-forward-fill karena POS hanya mengisi
    baris pertama dari tiap transaksi.
    """
    print(f"[1/4] Membaca file: {path}")
    if not os.path.exists(path):
        sys.exit(f"File tidak ditemukan: {path}")

    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb.active

    rows = []
    current_no_trans = None
    current_tanggal = None

    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        no_trans_raw = str(row[0]).strip() if row[0] else ""
        tanggal_raw  = str(row[1]).strip() if row[1] else ""
        produk_raw   = str(row[4]).strip() if row[4] else ""

        if no_trans_raw:
            current_no_trans = no_trans_raw
            current_tanggal  = parse_tanggal(tanggal_raw)

        if not current_no_trans or not produk_raw:
            continue

        rows.append({
            "no_trans": current_no_trans,
            "tanggal":  current_tanggal,
            "produk":   produk_raw,
        })

    wb.close()
    print(f"    {len(rows)} baris order dimuat")
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
    print("[3/4] Insert users (historical) ...")
    unique_trans = {r["no_trans"] for r in rows}

    user_rows = [
        (f"No. Transaksi {nt}", nt, "user", "historical")
        for nt in unique_trans
    ]
    cur.executemany(
        """
        INSERT IGNORE INTO users (nama_lengkap, username, password, role, source)
        VALUES (%s, %s, NULL, %s, %s)
        """,
        user_rows,
    )
    conn.commit()

    # Ambil mapping username → id
    cur.execute("SELECT id, username FROM users WHERE source = 'historical'")
    user_id_map = {username: uid for uid, username in cur.fetchall()}
    print(f"    {len(user_id_map)} users (historical) tersimpan")

    # ── 2. menu_items ────────────────────────────────────────────────────────
    print("      Insert menu_items ...")
    unique_produk = {r["produk"] for r in rows}

    menu_rows = []
    for produk in unique_produk:
        item_id, nama_menu, kategori = parse_produk(produk)
        menu_rows.append((item_id, nama_menu, kategori))

    cur.executemany(
        """
        INSERT IGNORE INTO menu_items (item_id, nama_menu, kategori)
        VALUES (%s, %s, %s)
        """,
        menu_rows,
    )
    conn.commit()

    # Ambil mapping item_id → id
    cur.execute("SELECT id, item_id FROM menu_items")
    menu_id_map = {item_id: mid for mid, item_id in cur.fetchall()}
    print(f"    {len(menu_id_map)} menu items tersimpan")

    # ── 3. orders ────────────────────────────────────────────────────────────
    print("[4/4] Insert orders ...")
    order_rows = []
    skipped = 0

    for r in rows:
        user_id      = user_id_map.get(r["no_trans"])
        item_id, _, _ = parse_produk(r["produk"])
        menu_item_id = menu_id_map.get(item_id)
        tanggal      = r["tanggal"]

        if not (user_id and menu_item_id and tanggal):
            skipped += 1
            continue

        order_rows.append((user_id, menu_item_id, tanggal))

    cur.executemany(
        "INSERT INTO orders (user_id, menu_item_id, tanggal) VALUES (%s, %s, %s)",
        order_rows,
    )
    conn.commit()

    print(f"    {len(order_rows)} orders tersimpan  ({skipped} baris dilewati karena data kosong)")

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
    ]
    expected = [1211, 207, 4909]

    all_ok = True
    for (label, sql), exp in zip(queries, expected):
        cur.execute(sql)
        count = cur.fetchone()[0]
        status = "✓" if count == exp else f"✗ (expected {exp})"
        print(f"  {label:<25} {count:>6}  {status}")
        if count != exp:
            all_ok = False

    cur.close()
    conn.close()
    print()
    if all_ok:
        print("Semua data berhasil diimport sesuai target dataset.")
    else:
        print("Ada perbedaan jumlah — periksa log di atas.")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rows = load_excel(EXCEL_PATH)
    import_to_db(rows)
    verify()
