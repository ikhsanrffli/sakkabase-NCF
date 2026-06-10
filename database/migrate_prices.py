"""
Migrasi: update kolom price di menu_items berdasarkan PRICE_LOOKUP.

Jalankan:
    python database/migrate_prices.py
"""

import re
import sys

try:
    import mysql.connector
except ImportError:
    sys.exit("mysql-connector-python belum terinstall.")

DB_CONFIG = {
    "host": "localhost", "port": 3306,
    "database": "sakkabase_ncf", "user": "root", "password": "", "charset": "utf8mb4",
}

PRICE_LOOKUP = {
    "A00": 22000,
    "A01A": 18000, "A01C": 28000, "A01D": 28000, "A01E": 28000,
    "A01F": 32000, "A01G": 30000, "A01H": 28000, "A01I": 30000,
    "A01J": 30000, "A01K": 32000, "A01L": 32000, "A01M": 32000,
    "A01N": 32000, "A01O": 35000,
    "A02A": 30000, "A02B": 32000, "A02C": 32000, "A02D": 32000,
    "A02E": 34000, "A02F": 34000, "A02G": 34000, "A02H": 34000, "A02I": 35000,
    "A03": 38000,
    "A04A": 35000, "A04B": 36000, "A04C": 35000, "A04D": 35000,
    "A04E": 36000, "A04F": 36000, "A04G": 36000,
    "A05A": 28000, "A05C": 28000, "A05D": 28000, "A05E": 30000,
    "A05F": 25000, "A05G": 32000,
    "A06A": 22000, "A06B": 22000, "A06C": 25000, "A06D": 20000,
    "A06E": 20000, "A06F": 22000, "A06G": 22000, "A06H": 15000,
    "A07B": 8000,
    "A08A": 10000, "A08B": 12000, "A08C": 15000, "A08D": 15000,
    "A08E": 15000, "A08F": 15000,
    "A09A": 28000, "A09B": 30000, "A09C": 30000, "A09D": 30000,
    "A09E": 32000, "A09F": 32000, "A09G": 32000, "A09H": 32000, "A09I": 42000,
    "A10": 20000,
    "A11A": 12000, "A11C": 10000, "A11E": 10000,
    "A12A": 32000,
    "A13A": 30000, "A13B": 32000, "A13C": 32000,
    "AA01": 120000, "AR12": 28000,
    "B01A": 35000, "B01B": 55000, "B01C": 80000, "B01D": 110000, "B01E": 135000, "B01F": 0,
    "B02A": 75000, "B02B": 65000, "B02C": 55000, "B02D": 45000, "B02E": 35000, "B02F": 40000,
    "B03A": 120000, "B03B": 200000, "B03C": 175000, "B03D": 90000,
    "B04A": 185000, "B04B": 250000, "B04C": 65000,
    "B05A": 35000, "B05B": 35000, "B05C": 35000, "B05D": 15000,
    "C01": 25000,
    "C01A": 22000, "C01B": 18000, "C01C": 18000, "C01D": 25000,
    "C01E": 20000, "C01F": 18000, "C01G": 22000, "C01H": 25000,
    "C01I": 18000, "C01J": 25000, "C01K": 18000, "C01L": 25000,
    "C01M": 22000, "C01N": 28000, "C01O": 55000, "C01P": 22000,
    "C02A": 25000, "C02B": 22000, "C02C": 25000, "C02D": 32000,
    "C03A": 25000, "C03B": 28000, "C03C": 32000, "C03D": 28000,
    "C03E": 30000, "C03F": 25000,
    "C04A": 32000, "C04B": 30000, "C04C": 28000, "C04D": 30000,
    "C04E": 32000, "C04F": 35000, "C04G": 38000, "C04H": 35000,
    "C04I": 42000, "C04J": 40000,
    "C05A": 22000, "C05B": 22000, "C05C": 28000, "C05D": 28000, "C05F": 32000,
    "C06A": 40000, "C06B": 45000, "C06C": 48000, "C06D": 45000, "C06E": 52000,
    "C07A": 15000, "C07B": 15000, "C07C": 18000,
    "C08A": 48000, "C08B": 52000, "C08C": 48000, "C08D": 52000,
    "C08E": 55000, "C08F": 55000, "C08G": 55000,
    "C09A": 32000, "C09B": 35000, "C09C": 28000, "C09D": 22000,
    "C10A": 32000, "C10B": 35000, "C10C": 32000, "C10D": 35000,
    "C11A": 20000, "C11B": 15000, "C11C": 18000,
    "CA01": 5000, "CA02": 5000, "CA03": 3000, "CA04": 3000,
    "CA05": 15000, "CA06": 5000, "CA07": 8000, "CA08": 8000,
    "CA09": 8000, "CA10": 10000,
    "D01A": 22000, "D01B": 22000, "D01C": 22000, "D01D": 20000,
    "D01E": 22000, "D01F": 20000, "D01G": 22000, "D01H": 20000,
    "D01I": 18000, "D01J": 20000,
    "P01": 50000, "P02": 65000,
}

_CATEGORY_DEFAULT = {"A": 20000, "B": 50000, "C": 25000, "D": 20000, "P": 50000}


_LARGE_KEYWORDS = ["/ LARGE", "/LARGE", "/ HOT LARGE", "/ COLD LARGE"]
_LARGE_PREMIUM  = 5000


def get_price(item_id: str, nama_menu: str = "") -> int:
    m = re.match(r'^([A-Z]{1,2}\d{1,2}[A-Z]?)', item_id.upper())
    if not m:
        return 0
    code = m.group(1)
    base_price = 0
    for length in (len(code), len(code) - 1, 2, 1):
        prefix = code[:length]
        if prefix in PRICE_LOOKUP:
            base_price = PRICE_LOOKUP[prefix]
            break
    if base_price == 0:
        base_price = _CATEGORY_DEFAULT.get(code[0].upper(), 15000)

    upper_name = nama_menu.upper()
    if any(kw in upper_name for kw in _LARGE_KEYWORDS):
        base_price += _LARGE_PREMIUM

    return base_price


def main():
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT id, item_id, nama_menu, price FROM menu_items")
    rows = cursor.fetchall()
    print(f"Ditemukan {len(rows)} menu item.")

    updated = zero_before = 0
    for row_id, item_id, nama_menu, current_price in rows:
        if current_price == 0:
            zero_before += 1
        new_price = get_price(item_id, nama_menu)
        if new_price != current_price:
            cursor.execute("UPDATE menu_items SET price = %s WHERE id = %s", (new_price, row_id))
            updated += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Sebelumnya {zero_before} item dengan harga 0.")
    print(f"Selesai. {updated} harga diperbarui.")


if __name__ == "__main__":
    main()
