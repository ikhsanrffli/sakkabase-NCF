#!/usr/bin/env python3
"""
Konverter dataset Sakka Base -> src/data/initialData.js

Sumber  : src/dataset.xlsx  (export "Detil Penjualan": No Transaksi, Tanggal,
          Outlet, Pelanggan, Produk, Qty)
Keluaran: src/data/initialData.js  (USERS_DB, MENUS_DATA, MENU_CATEGORIES,
          CATEGORY_ICONS, ORDERS_DATA)

Jalankan setiap kali dataset berubah:
    pip install openpyxl
    python scripts/convert_dataset.py

Aturan penting:
- Satu baris produk = satu interaksi (implicit feedback) -> ORDERS_DATA.
- menuId diambil dari KODE produk (sebelum " - "); varian ukuran
  ("/ COLD LARGE" dst) digabung ke satu menu.
- Pelanggan unik -> USERS_DB (role 'user'). Dua pelanggan paling aktif
  diberi kredensial demo user1/user2; sisanya username otomatis + password
  default 'sakka123'. Akun admin selalu ditambahkan.
- Kategori tidak ada di Excel -> diambil dari SEED_MENU (kode lama) lalu
  aturan kata kunci, lalu fallback prefix kode.
"""
import openpyxl, re, json, unicodedata, os
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XLSX = os.path.join(ROOT, "src", "dataset.xlsx")
OUT  = os.path.join(ROOT, "src", "data", "initialData.js")

CATEGORY_ICONS = {
  "Barber":"✂️","Chicken Steak":"\U0001f357","Croissant & Pastry":"\U0001f950",
  "Gorengan & Snack":"\U0001f35f","Ice Cream":"\U0001f366","Indomie":"\U0001f35c",
  "Juice":"\U0001f964","Kopi & Espresso":"☕","Lainnya":"\U0001f4e6",
  "Mie & Bihun":"\U0001f35c","Minuman":"\U0001f4a7","Nasi Goreng":"\U0001f373",
  "Nasi Lauk":"\U0001f35a","Non-Kopi":"\U0001f375","Pasta":"\U0001f35d",
  "Pudding":"\U0001f36e","Ricebowl":"\U0001f371","Salad":"\U0001f957",
  "Sayur":"\U0001f96c","Snack Ringan":"\U0001f37f","Tambahan":"➕","Toast":"\U0001f35e",
}

SEED_MENU = {'A00A': ['Americano Sakka', 'Kopi & Espresso', '☕'], 'A00B': ['Lychee Americano', 'Kopi & Espresso', '☕'], 'A00C': ['Coconut Americano', 'Kopi & Espresso', '☕'], 'A00D': ['Honey Americano', 'Kopi & Espresso', '☕'], 'A00E': ['Lemon Americano', 'Kopi & Espresso', '☕'], 'A01A': ['Espresso', 'Kopi & Espresso', '☕'], 'A01C': ['Split Coffee', 'Kopi & Espresso', '☕'], 'A01D': ['Sanger Sakka', 'Kopi & Espresso', '☕'], 'A01E': ['Cappuccino', 'Kopi & Espresso', '☕'], 'A01F': ['Magic - Double Ristretto', 'Kopi & Espresso', '☕'], 'A01G': ['Cafe Latte', 'Kopi & Espresso', '☕'], 'A01H': ['Piccolo', 'Kopi & Espresso', '☕'], 'A01I': ['Dirty Latte', 'Kopi & Espresso', '☕'], 'A01J': ['Mochaccino', 'Kopi & Espresso', '☕'], 'A01K': ['Matcha Coffee', 'Kopi & Espresso', '☕'], 'A01L': ['Latte With Caramel', 'Kopi & Espresso', '☕'], 'A01M': ['Latte With Hazelnut', 'Kopi & Espresso', '☕'], 'A01N': ['Latte With Vanilla', 'Kopi & Espresso', '☕'], 'A01O': ['Artisan Manual Brew', 'Kopi & Espresso', '☕'], 'A02A': ['Aren Latte', 'Kopi & Espresso', '☕'], 'A02B': ['Spanish Latte Cold', 'Kopi & Espresso', '☕'], 'A02C': ['Banana Latte Cold', 'Kopi & Espresso', '☕'], 'A02D': ['Creamy Oat Latte Cold', 'Kopi & Espresso', '☕'], 'A02E': ['Butterscotch Latte Cold', 'Kopi & Espresso', '☕'], 'A02F': ['Caramel Macchiato Cold', 'Kopi & Espresso', '☕'], 'A02G': ['Coconut Pandan Latte Cold', 'Kopi & Espresso', '☕'], 'A02H': ['Charcoal Espresso Latte Cold', 'Kopi & Espresso', '☕'], 'A02I': ['Sakka Jelly Coffee', 'Kopi & Espresso', '☕'], 'A03A': ['Butterscotch Cream Cheese Cold', 'Kopi & Espresso', '☕'], 'A03B': ['Banana Peanut Cream Cold', 'Kopi & Espresso', '☕'], 'A03C': ['Strawberry Matcha Cream Cold', 'Kopi & Espresso', '☕'], 'A03D': ['Citrus Matcha Sunrise Cold', 'Kopi & Espresso', '☕'], 'A03E': ['Tiramisu Cookie Cream Cold', 'Kopi & Espresso', '☕'], 'A04A': ['Buttermello Frappe', 'Kopi & Espresso', '☕'], 'A04B': ['Java Chip Chocolate Frappe', 'Kopi & Espresso', '☕'], 'A04C': ['Oreo Cookie Crunch Frappe', 'Kopi & Espresso', '☕'], 'A04D': ['Matcha Frappe', 'Kopi & Espresso', '☕'], 'A04E': ['Red Velvet Frappe', 'Kopi & Espresso', '☕'], 'A04F': ['Taro Frappe', 'Kopi & Espresso', '☕'], 'A04G': ['Baby Milo Frappe', 'Kopi & Espresso', '☕'], 'A05A': ['Purple Taro Latte', 'Non-Kopi', '🍵'], 'A05C': ['Chocolate Latte', 'Non-Kopi', '🍵'], 'A05D': ['Red Velvet Latte', 'Non-Kopi', '🍵'], 'A05E': ['Bamboo Charcoal Latte', 'Non-Kopi', '🍵'], 'A05F': ['Milo Latte', 'Non-Kopi', '🍵'], 'A05G': ['Sakka Jelly Pandan', 'Non-Kopi', '🍵'], 'A06A': ['Orange Juice', 'Juice', '🥤'], 'A06B': ['Mango Juice', 'Juice', '🥤'], 'A06C': ['Avocado Juice', 'Juice', '🥤'], 'A06D': ['Timun Juice', 'Juice', '🥤'], 'A06E': ['Tomato Juice', 'Juice', '🥤'], 'A06F': ['Red Dragon Juice', 'Juice', '🥤'], 'A06G': ['Sirsak Juice', 'Juice', '🥤'], 'A06H': ['Air Kelapa Asli', 'Juice', '🥤'], 'A07B': ['Le Mineral 600ml', 'Minuman', '💧'], 'A08A': ['Pure Tea', 'Minuman', '💧'], 'A08B': ['Tea Manis', 'Minuman', '💧'], 'A08C': ['Lemon Tea', 'Minuman', '💧'], 'A08D': ['Lychee Tea', 'Minuman', '💧'], 'A08E': ['Peach Tea', 'Minuman', '💧'], 'A08F': ['Styrawberry Tea', 'Minuman', '💧'], 'A09A': ['Butter Croissant', 'Croissant & Pastry', '🥐'], 'A09B': ['Ocean Blue', 'Croissant & Pastry', '🥐'], 'A09C': ['Pink Berry', 'Croissant & Pastry', '🥐'], 'A09D': ['Peach Sparkling', 'Croissant & Pastry', '🥐'], 'A09E': ['Pain Au Chocolat', 'Croissant & Pastry', '🥐'], 'A09F': ['Passion Valley', 'Croissant & Pastry', '🥐'], 'A09G': ['Cream Cheese Croissant', 'Croissant & Pastry', '🥐'], 'A09H': ['Choco Nut Croissant', 'Croissant & Pastry', '🥐'], 'A09I': ['Croissant Sandwich', 'Croissant & Pastry', '🥐'], 'A10A': ['Thai Aren Pudding', 'Pudding', '🍮'], 'A10B': ['Nata De Coco W Brown Sugar Pudding', 'Pudding', '🍮'], 'A10C': ['Chocolate Pudding', 'Pudding', '🍮'], 'A11A': ['Keripik Balado', 'Snack Ringan', '🍿'], 'A11C': ['Emping Besar', 'Snack Ringan', '🍿'], 'A11E': ['Emping Kecil', 'Snack Ringan', '🍿'], 'A12A': ['Cheesecake', 'Snack Ringan', '🍿'], 'A13A': ['Matcha Latte', 'Non-Kopi', '🍵'], 'A13B': ['Creamy Oat Matcha', 'Non-Kopi', '🍵'], 'A13C': ['Dirty Oat Matcha', 'Non-Kopi', '🍵'], 'AA01': ['(Pouch) Arabica Single Origin Mandheling 1kg', 'Lainnya', '📦'], 'AR12': ['Lemon Americano - L Size', 'Kopi & Espresso', '☕'], 'B01A': ['Sakka Regular Cut', 'Barber', '✂️'], 'B01B': ['Sakka Cut & Fresh', 'Barber', '✂️'], 'B01C': ['Sakka Premium Cut', 'Barber', '✂️'], 'B01D': ['The Base Full Service', 'Barber', '✂️'], 'B01E': ['Sakka Executive Plus', 'Barber', '✂️'], 'B01F': ['Free Cut & Fresh (Claim Loyalty Card)', 'Barber', '✂️'], 'B02A': ['Sakka Confidence Booster', 'Barber', '✂️'], 'B02B': ['Sakka Stress Relief', 'Barber', '✂️'], 'B02C': ['Facial Mask', 'Barber', '✂️'], 'B02D': ['Face Refresh', 'Barber', '✂️'], 'B02E': ['Hair Styling', 'Barber', '✂️'], 'B02F': ['Shaving', 'Barber', '✂️'], 'B03A': ['Basic Colour', 'Barber', '✂️'], 'B03B': ['Full Colour', 'Barber', '✂️'], 'B03C': ['Highlight', 'Barber', '✂️'], 'B03D': ['Hair Color Fix (Retouch Roots)', 'Barber', '✂️'], 'B04A': ['Hair Perm', 'Barber', '✂️'], 'B04B': ['Downperm', 'Barber', '✂️'], 'B04C': ['Hair Tattoo', 'Barber', '✂️'], 'B05A': ['Marlboro Black Anchor Clay Hitam', 'Lainnya', '📦'], 'B05B': ['Marlboro Biru', 'Lainnya', '📦'], 'B05C': ['Marlboro Merah', 'Lainnya', '📦'], 'B05D': ['Bubur Takjil', 'Lainnya', '📦'], 'C01': ['Taichan Sakka', 'Gorengan & Snack', '🍟'], 'C01A': ['French Fries', 'Gorengan & Snack', '🍟'], 'C01B': ['Ubi Goreng Ketumbar', 'Gorengan & Snack', '🍟'], 'C01C': ['Tahu Cabe Garam', 'Gorengan & Snack', '🍟'], 'C01D': ['Potato Wedges', 'Gorengan & Snack', '🍟'], 'C01E': ['Pisang Goreng Coklat Keju', 'Gorengan & Snack', '🍟'], 'C01F': ['Pisang Goreng Srikaya', 'Gorengan & Snack', '🍟'], 'C01G': ['Pisang Bakar Coklat Keju', 'Gorengan & Snack', '🍟'], 'C01H': ['Chicken Nugget', 'Gorengan & Snack', '🍟'], 'C01I': ['Crispy Tempeh', 'Gorengan & Snack', '🍟'], 'C01J': ['Chicken Popcorn', 'Gorengan & Snack', '🍟'], 'C01K': ['Bakwan Jagung', 'Gorengan & Snack', '🍟'], 'C01L': ['Corn Ribs', 'Gorengan & Snack', '🍟'], 'C01M': ['Risol Sakka', 'Gorengan & Snack', '🍟'], 'C01N': ['Chicken Tortilla', 'Gorengan & Snack', '🍟'], 'C01O': ['Snack Platter', 'Gorengan & Snack', '🍟'], 'C01P': ['Dragon Ball', 'Gorengan & Snack', '🍟'], 'C02A': ['Choco Cheese Toast', 'Toast', '🍞'], 'C02B': ['Kaya Butter Toast', 'Toast', '🍞'], 'C02C': ['Choco Banana Toast', 'Toast', '🍞'], 'C02D': ['Chicken Sandwich Toast', 'Toast', '🍞'], 'C03A': ['Nasi Goreng Telur', 'Nasi Goreng', '🍳'], 'C03B': ['Nasi Goreng Kampung', 'Nasi Goreng', '🍳'], 'C03C': ['Nasi Goreng Seafood', 'Nasi Goreng', '🍳'], 'C03D': ['Nasi Goreng Cabe Ijo', 'Nasi Goreng', '🍳'], 'C03E': ['Nasi Goreng Special', 'Nasi Goreng', '🍳'], 'C03F': ['Nasi Goreng Vegetarian', 'Nasi Goreng', '🍳'], 'C04A': ['Nasi Ayam Bakar', 'Nasi Lauk', '🍚'], 'C04B': ['Nasi Ayam Penyet Cabe Ijo', 'Nasi Lauk', '🍚'], 'C04C': ['Nasi Ayam Geprek', 'Nasi Lauk', '🍚'], 'C04D': ['Nasi Soto Ayam', 'Nasi Lauk', '🍚'], 'C04E': ['Nasi Ayam Rica Rica', 'Nasi Lauk', '🍚'], 'C04F': ['Nasi Katsu Sakka', 'Nasi Lauk', '🍚'], 'C04G': ['Nasi Capcay Seafood', 'Nasi Lauk', '🍚'], 'C04H': ['Nasi Ayam Kecombrang', 'Nasi Lauk', '🍚'], 'C04I': ['Nasi Dori Sambal Matah + Sup Kentang', 'Nasi Lauk', '🍚'], 'C04J': ['Tomyum', 'Nasi Lauk', '🍚'], 'C05A': ['Bihun Kuah', 'Mie & Bihun', '🍜'], 'C05B': ['Bihun Goreng Polos', 'Mie & Bihun', '🍜'], 'C05C': ['Mie Goreng Jawa', 'Mie & Bihun', '🍜'], 'C05D': ['Mie Sop Sakka', 'Mie & Bihun', '🍜'], 'C05F': ['Bihun Goreng Seafood', 'Mie & Bihun', '🍜'], 'C06A': ['Spaghetti Aglio E Olio', 'Pasta', '🍝'], 'C06B': ['Fettucini Spicy Chicken', 'Pasta', '🍝'], 'C06C': ['Linguine Pasta & Grilled Chicken', 'Pasta', '🍝'], 'C06D': ['Fettucini Carbonara', 'Pasta', '🍝'], 'C06E': ['Spaghetti Seafood', 'Pasta', '🍝'], 'C07A': ['Indomie Kuah', 'Indomie', '🍜'], 'C07B': ['Indomie Goreng', 'Indomie', '🍜'], 'C07C': ['Indomie Bangladesh', 'Indomie', '🍜'], 'C08A': ['Crispy Chicken Chop', 'Chicken Steak', '🍗'], 'C08B': ['Crispy Chicken Mushroom Steak', 'Chicken Steak', '🍗'], 'C08C': ['Grilled Chicken Chop', 'Chicken Steak', '🍗'], 'C08D': ['Grilled Chicken Mushroom Steak', 'Chicken Steak', '🍗'], 'C08E': ['Crispy Blackpepper Chicken Steak', 'Chicken Steak', '🍗'], 'C08F': ['Grilled Blackpepper Chicken Steak', 'Chicken Steak', '🍗'], 'C08G': ['Fish & Chips', 'Chicken Steak', '🍗'], 'C09A': ['Chicken Salad', 'Salad', '🥗'], 'C09B': ['Caesar Salad', 'Salad', '🥗'], 'C09C': ['Vegetarian Salad', 'Salad', '🥗'], 'C09D': ['Gado-Gado', 'Salad', '🥗'], 'C10A': ['Chicken Korean Ricebowl', 'Ricebowl', '🍱'], 'C10B': ['Chicken Cheese Ricebowl', 'Ricebowl', '🍱'], 'C10C': ['Chicken Spicy Ricebowl', 'Ricebowl', '🍱'], 'C10D': ['Takikomi Ricebowl', 'Ricebowl', '🍱'], 'C11A': ['Tauco Vegetarian', 'Sayur', '🥬'], 'C11B': ['Tauco Vegetarian Kecil', 'Sayur', '🥬'], 'C11C': ['Tauge Tahu Tumis', 'Sayur', '🥬'], 'CA01': ['Nasi Putih', 'Tambahan', '➕'], 'CA02': ['Telur', 'Tambahan', '➕'], 'CA03': ['Kerupuk', 'Tambahan', '➕'], 'CA04': ['Emping', 'Tambahan', '➕'], 'CA05': ['Ayam Goreng', 'Tambahan', '➕'], 'CA06': ['Sambal All Varian', 'Tambahan', '➕'], 'CA07': ['Srikaya Addon', 'Tambahan', '➕'], 'CA08': ['Extra Sauce Chicken Steak Mushroom', 'Tambahan', '➕'], 'CA09': ['Extra Sauce Chicken Chop', 'Tambahan', '➕'], 'CA10': ['Bumbu Rujak', 'Lainnya', '📦'], 'D01A': ['Crunchy Choco Lava Ice Cream', 'Ice Cream', '🍦'], 'D01B': ['Crunchy Cookies Cream Ice Cream', 'Ice Cream', '🍦'], 'D01C': ['Crunchy Chocolate Blueberry Ice Cream', 'Ice Cream', '🍦'], 'D01D': ['Fruitti Frizz Ice Cream', 'Ice Cream', '🍦'], 'D01E': ['Coffee Latte Ice Cream', 'Ice Cream', '🍦'], 'D01F': ['Kacang Ijo Ice Cream', 'Ice Cream', '🍦'], 'D01G': ['Choco O Malt Ice Cream', 'Ice Cream', '🍦'], 'D01H': ['Kokomi Ice Cream', 'Ice Cream', '🍦'], 'D01I': ['Es Susu Ice Cream', 'Ice Cream', '🍦'], 'D01J': ['Cool Watermelon Apple Ice Cream', 'Ice Cream', '🍦']}

def classify(code, name):
    if code in SEED_MENU:
        nm, cat, icon = SEED_MENU[code]
        return cat, icon, nm
    n = name.upper()
    rules = [
      (("BARBER","CUT","SHAV","COLOUR","COLOR","PERM","HIGHLIGHT","FACIAL","HAIR","STYLING","TATTOO","CONFIDENCE","STRESS RELIEF","FACE REFRESH"),"Barber"),
      (("AMERICANO","ESPRESSO","LATTE","CAPPUCCINO","SANGER","COFFEE","MOCHA","PICCOLO","RISTRETTO","FRAPPE","MACCHIATO","KOPI","BREW"),"Kopi & Espresso"),
      (("MATCHA","CHOCOLATE LATTE","TARO","MILO","RED VELVET LATTE","CHARCOAL LATTE"),"Non-Kopi"),
      (("JUICE","KELAPA"),"Juice"),
      (("TEA","MINERAL"),"Minuman"),
      (("CROISSANT","PASTRY","PAIN AU"),"Croissant & Pastry"),
      (("PUDDING",),"Pudding"),
      (("ICE CREAM",),"Ice Cream"),
      (("NASI GORENG",),"Nasi Goreng"),
      (("RICEBOWL",),"Ricebowl"),
      (("NASI ",),"Nasi Lauk"),
      (("BIHUN","KWETIAU","MIE "),"Mie & Bihun"),
      (("INDOMIE",),"Indomie"),
      (("SPAGHETTI","FETTUCINI","LINGUINE","PASTA","CARBONARA"),"Pasta"),
      (("CHICKEN CHOP","CHICKEN STEAK","CHICKEN MUSHROOM","FISH & CHIPS","BLACKPEPPER CHICKEN"),"Chicken Steak"),
      (("SALAD","GADO"),"Salad"),
      (("TOAST",),"Toast"),
      (("TAUCO","TAUGE","SAYUR","TUMIS"),"Sayur"),
      (("FRENCH FRIES","WEDGES","PISANG","UBI","TAHU","NUGGET","TEMPEH","POPCORN","BAKWAN","CORN RIBS","RISOL","TORTILLA","PLATTER","DRAGON BALL","TAICHAN","GORENG"),"Gorengan & Snack"),
      (("KERIPIK","EMPING","CHEESECAKE"),"Snack Ringan"),
      (("NASI PUTIH","TELUR","KERUPUK","AYAM GORENG","SAMBAL","SRIKAYA","EXTRA SAUCE"),"Tambahan"),
      (("MARLBORO","ROKOK","POUCH","ARABICA","ES KOSONG","BUBUR","BUMBU","CLAY"),"Lainnya"),
    ]
    for kws,cat in rules:
        if any(k in n for k in kws):
            return cat, CATEGORY_ICONS[cat], None
    cat = {"B":"Barber","A":"Minuman","C":"Gorengan & Snack","D":"Ice Cream"}.get(code[:1],"Lainnya")
    return cat, CATEGORY_ICONS[cat], None

def titlecase(s):
    return " ".join(w.capitalize() for w in s.split())

def slug(name, used):
    base = unicodedata.normalize("NFKD", name).encode("ascii","ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+","", base).lower() or "user"
    u=base; i=1
    while u in used:
        i+=1; u=f"{base}{i}"
    used.add(u); return u

def parse_date(t):
    if not t: return ""
    for fmt in ("%d/%m/%Y %H:%M","%d/%m/%Y","%Y-%m-%d %H:%M:%S","%Y-%m-%d"):
        try: return datetime.strptime(t,fmt).strftime("%Y-%m-%d")
        except: pass
    return ""

def main():
    ws = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)["Sheet1"]
    rows=[]; cust=tgl=None
    for i,r in enumerate(ws.iter_rows(values_only=True)):
        if i==0: continue
        _,rtgl,_,rpel,rprod,_ = r[:6]
        if rtgl not in (None,""): tgl=str(rtgl).strip()
        if rpel not in (None,""): cust=str(rpel).strip()
        if rprod in (None,""): continue
        prod=str(rprod).strip()
        code = prod.split(" - ")[0].strip() if " - " in prod else prod
        rest = prod.split(" - ",1)[1] if " - " in prod else prod
        base = rest.split(" / ")[0].strip()
        rows.append((cust,code,base,parse_date(tgl)))

    menus={}
    for cust,code,base,d in rows:
        if code in menus: continue
        cat,icon,old = classify(code, base)
        menus[code]={"id":code,"name":old or titlecase(base),"category":cat,"icon":icon}
    menus_list=sorted(menus.values(), key=lambda m:m["id"])

    counts=Counter(c for c,_,_,_ in rows)
    used={"admin","user1","user2"}
    users=[{"id":"admin","username":"admin","password":"admin123","role":"admin","name":"Administrator"}]
    cust2id={}
    for idx,(c,_) in enumerate(counts.most_common()):
        uid=f"u{idx+1}"; cust2id[c]=uid
        if idx==0: un,pw="user1","user123"
        elif idx==1: un,pw="user2","user456"
        else: un,pw=slug(c,used),"sakka123"
        users.append({"id":uid,"username":un,"password":pw,"role":"user","name":c})

    orders=[{"id":f"ORD{n:05d}","userId":cust2id[c],"userName":c,
             "menuId":code,"menuName":menus[code]["name"],"date":d}
            for n,(c,code,base,d) in enumerate(rows,1)]

    cats=sorted({m["category"] for m in menus_list})
    j=lambda o: json.dumps(o, ensure_ascii=False)
    L=["// AUTO-GENERATED oleh scripts/convert_dataset.py dari src/dataset.xlsx.",
       "// Jangan edit baris data manual; jalankan ulang skrip bila dataset berubah.\n",
       "export const USERS_DB = ["]
    L+=["  "+j(u)+"," for u in users]; L+=["];\n","export const MENUS_DATA = ["]
    L+=["  "+j(m)+"," for m in menus_list]; L+=["];\n",
        "export const MENU_CATEGORIES = "+j(cats)+";\n",
        "export const CATEGORY_ICONS = "+j({c:CATEGORY_ICONS[c] for c in cats})+";\n",
        "export const ORDERS_DATA = ["]
    L+=["  "+j(o)+"," for o in orders]; L+=["];"]
    open(OUT,"w").write("\n".join(L))
    print(f"OK -> {OUT}")
    print(f"   users={len(users)} (user role={len(users)-1}) menus={len(menus_list)} orders={len(orders)} categories={len(cats)}")

if __name__=="__main__":
    main()
