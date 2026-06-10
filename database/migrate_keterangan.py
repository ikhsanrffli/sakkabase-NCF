"""
Migrasi: tambah kolom keterangan ke tabel menu_items dan isi dengan deskripsi otomatis.

Jalankan:
    python database/migrate_keterangan.py
"""

import sys

try:
    import mysql.connector
except ImportError:
    sys.exit("mysql-connector-python belum terinstall. Jalankan: pip install mysql-connector-python")


DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "database": "sakkabase_ncf",
    "user":     "root",
    "password": "",
    "charset":  "utf8mb4",
}

_STRIP_SUFFIXES = [
    "/ HOT REGULAR", "/ COLD REGULAR", "/ HOT LARGE", "/ COLD LARGE",
    "/ HOT", "/ COLD", "/ REGULAR", "/ LARGE", "/ SMALL", "/ 50K", "/ 25K",
]


def _base_title(nama_menu: str) -> str:
    name = nama_menu.strip()
    for suffix in _STRIP_SUFFIXES:
        if name.upper().endswith(suffix):
            name = name[: -len(suffix)].strip()
            break
    return name.title()


def _generate_keterangan(nama_menu: str, kategori: str) -> str:
    upper = nama_menu.upper()
    base  = _base_title(nama_menu)

    if kategori == "Ice Cream":
        return f"Es krim {base} dengan cita rasa yang segar dan lezat."

    if kategori == "Minuman":
        if any(kw in upper for kw in ["AMERICANO","LATTE","CAPPUCCINO","ESPRESSO","FRAPPE","SANGER","KOPI"]):
            return f"Minuman kopi {base} dengan cita rasa khas Sakka Base."
        if "JUICE" in upper:
            return f"Minuman jus {base} segar dari bahan pilihan."
        if "TEA" in upper:
            return f"Minuman teh {base} dengan rasa yang menenangkan."
        if "MATCHA" in upper:
            return f"Minuman matcha {base} yang kaya rasa."
        return f"Minuman {base} segar pilihan Sakka Base."

    if kategori == "Makanan":
        if "NASI" in upper:
            return f"Nasi {base} dengan lauk pilihan yang mengenyangkan."
        if any(kw in upper for kw in ["MIE","BIHUN","KWETIAU"]):
            return f"Hidangan {base} dengan bumbu pilihan."
        if any(kw in upper for kw in ["CHICKEN","AYAM"]):
            return f"Hidangan ayam {base} yang lezat dan mengenyangkan."
        if "TOAST" in upper:
            return f"Roti panggang {base} dengan topping spesial."
        if "SALAD" in upper:
            return f"Salad {base} segar dengan dressing pilihan."
        if any(kw in upper for kw in ["PASTA","LINGUINE","FETTUCINI"]):
            return f"Pasta {base} dengan saus autentik."
        if "INDOMIE" in upper:
            return f"Indomie {base} dengan bumbu istimewa."
        if "RICEBOWL" in upper:
            return f"Ricebowl {base} dengan isian yang lezat."
        if any(kw in upper for kw in ["CRISPY","NUGGET","POPCORN","BAKWAN","FRENCH FRIES","CORN RIBS"]):
            return f"Camilan {base} yang renyah dan gurih."
        return f"Hidangan {base} pilihan Sakka Base."

    if kategori == "Paket":
        return f"Paket {base} yang hemat dan lengkap."

    return f"{base} — menu pilihan dari Sakka Base."


def main():
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Menambahkan kolom keterangan (jika belum ada)...")
    cursor.execute("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS keterangan TEXT NULL")
    conn.commit()
    print("  Kolom keterangan siap.")

    cursor.execute("SELECT id, item_id, nama_menu, kategori FROM menu_items")
    rows = cursor.fetchall()
    print(f"  Ditemukan {len(rows)} menu item.")

    updated = 0
    for row_id, item_id, nama_menu, kategori in rows:
        keterangan = _generate_keterangan(nama_menu, kategori)
        cursor.execute(
            "UPDATE menu_items SET keterangan = %s WHERE id = %s AND (keterangan IS NULL OR keterangan = '')",
            (keterangan, row_id),
        )
        if cursor.rowcount > 0:
            updated += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nSelesai. {updated} dari {len(rows)} baris diperbarui.")


if __name__ == "__main__":
    main()
