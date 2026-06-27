-- ============================================================
-- Update harga menu + hitung ulang total belanja
-- Harga = sama dengan tampilan frontend (menuInfo.js)
-- Jalankan SELURUH file ini di tab SQL phpMyAdmin (DB: sakkabase / nama db kamu)
-- ============================================================

START TRANSACTION;

-- 1) Set harga tiap menu di menu_items
UPDATE menu_items SET price = 28000 WHERE item_id = 'A00A';
UPDATE menu_items SET price = 29000 WHERE item_id = 'A00B';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A00C';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A00D';
UPDATE menu_items SET price = 19000 WHERE item_id = 'A00E';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A01A';
UPDATE menu_items SET price = 21000 WHERE item_id = 'A01B';
UPDATE menu_items SET price = 22000 WHERE item_id = 'A01C';
UPDATE menu_items SET price = 23000 WHERE item_id = 'A01D';
UPDATE menu_items SET price = 24000 WHERE item_id = 'A01E';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A01F';
UPDATE menu_items SET price = 26000 WHERE item_id = 'A01G';
UPDATE menu_items SET price = 27000 WHERE item_id = 'A01H';
UPDATE menu_items SET price = 28000 WHERE item_id = 'A01I';
UPDATE menu_items SET price = 29000 WHERE item_id = 'A01J';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A01K';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A01L';
UPDATE menu_items SET price = 19000 WHERE item_id = 'A01M';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A01N';
UPDATE menu_items SET price = 21000 WHERE item_id = 'A01O';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A02A';
UPDATE menu_items SET price = 26000 WHERE item_id = 'A02B';
UPDATE menu_items SET price = 27000 WHERE item_id = 'A02C';
UPDATE menu_items SET price = 28000 WHERE item_id = 'A02D';
UPDATE menu_items SET price = 29000 WHERE item_id = 'A02E';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A02F';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A02G';
UPDATE menu_items SET price = 19000 WHERE item_id = 'A02H';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A02I';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A03A';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A03B';
UPDATE menu_items SET price = 19000 WHERE item_id = 'A03C';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A03D';
UPDATE menu_items SET price = 21000 WHERE item_id = 'A03E';
UPDATE menu_items SET price = 22000 WHERE item_id = 'A04A';
UPDATE menu_items SET price = 23000 WHERE item_id = 'A04B';
UPDATE menu_items SET price = 24000 WHERE item_id = 'A04C';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A04D';
UPDATE menu_items SET price = 26000 WHERE item_id = 'A04E';
UPDATE menu_items SET price = 27000 WHERE item_id = 'A04F';
UPDATE menu_items SET price = 28000 WHERE item_id = 'A04G';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A05A';
UPDATE menu_items SET price = 27000 WHERE item_id = 'A05C';
UPDATE menu_items SET price = 28000 WHERE item_id = 'A05D';
UPDATE menu_items SET price = 29000 WHERE item_id = 'A05E';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A05F';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A05G';
UPDATE menu_items SET price = 20000 WHERE item_id = 'A06A';
UPDATE menu_items SET price = 21000 WHERE item_id = 'A06B';
UPDATE menu_items SET price = 22000 WHERE item_id = 'A06C';
UPDATE menu_items SET price = 23000 WHERE item_id = 'A06D';
UPDATE menu_items SET price = 24000 WHERE item_id = 'A06E';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A06F';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A06G';
UPDATE menu_items SET price = 19000 WHERE item_id = 'A06H';
UPDATE menu_items SET price = 14000 WHERE item_id = 'A07A';
UPDATE menu_items SET price = 15000 WHERE item_id = 'A07B';
UPDATE menu_items SET price = 13000 WHERE item_id = 'A08A';
UPDATE menu_items SET price = 14000 WHERE item_id = 'A08B';
UPDATE menu_items SET price = 15000 WHERE item_id = 'A08C';
UPDATE menu_items SET price = 16000 WHERE item_id = 'A08D';
UPDATE menu_items SET price = 17000 WHERE item_id = 'A08E';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A08F';
UPDATE menu_items SET price = 22000 WHERE item_id = 'A09A';
UPDATE menu_items SET price = 23000 WHERE item_id = 'A09B';
UPDATE menu_items SET price = 24000 WHERE item_id = 'A09C';
UPDATE menu_items SET price = 25000 WHERE item_id = 'A09D';
UPDATE menu_items SET price = 26000 WHERE item_id = 'A09E';
UPDATE menu_items SET price = 27000 WHERE item_id = 'A09F';
UPDATE menu_items SET price = 28000 WHERE item_id = 'A09G';
UPDATE menu_items SET price = 29000 WHERE item_id = 'A09H';
UPDATE menu_items SET price = 30000 WHERE item_id = 'A09I';
UPDATE menu_items SET price = 18000 WHERE item_id = 'A10E';
UPDATE menu_items SET price = 10000 WHERE item_id = 'A11A';
UPDATE menu_items SET price = 12000 WHERE item_id = 'A11C';
UPDATE menu_items SET price = 22000 WHERE item_id = 'A13A';
UPDATE menu_items SET price = 8000 WHERE item_id = 'AA01';
UPDATE menu_items SET price = 7000 WHERE item_id = 'AA02';
UPDATE menu_items SET price = 28000 WHERE item_id = 'C01A';
UPDATE menu_items SET price = 29000 WHERE item_id = 'C01B';
UPDATE menu_items SET price = 30000 WHERE item_id = 'C01C';
UPDATE menu_items SET price = 15000 WHERE item_id = 'C01D';
UPDATE menu_items SET price = 16000 WHERE item_id = 'C01E';
UPDATE menu_items SET price = 17000 WHERE item_id = 'C01F';
UPDATE menu_items SET price = 18000 WHERE item_id = 'C01G';
UPDATE menu_items SET price = 19000 WHERE item_id = 'C01H';
UPDATE menu_items SET price = 20000 WHERE item_id = 'C01I';
UPDATE menu_items SET price = 21000 WHERE item_id = 'C01J';
UPDATE menu_items SET price = 22000 WHERE item_id = 'C01K';
UPDATE menu_items SET price = 23000 WHERE item_id = 'C01L';
UPDATE menu_items SET price = 24000 WHERE item_id = 'C01M';
UPDATE menu_items SET price = 26000 WHERE item_id = 'C01O';
UPDATE menu_items SET price = 26000 WHERE item_id = 'C02A';
UPDATE menu_items SET price = 27000 WHERE item_id = 'C02B';
UPDATE menu_items SET price = 28000 WHERE item_id = 'C02C';
UPDATE menu_items SET price = 29000 WHERE item_id = 'C02D';
UPDATE menu_items SET price = 31000 WHERE item_id = 'C03A';
UPDATE menu_items SET price = 32000 WHERE item_id = 'C03B';
UPDATE menu_items SET price = 33000 WHERE item_id = 'C03C';
UPDATE menu_items SET price = 34000 WHERE item_id = 'C03D';
UPDATE menu_items SET price = 35000 WHERE item_id = 'C03E';
UPDATE menu_items SET price = 44000 WHERE item_id = 'C04A';
UPDATE menu_items SET price = 45000 WHERE item_id = 'C04B';
UPDATE menu_items SET price = 25000 WHERE item_id = 'C04C';
UPDATE menu_items SET price = 26000 WHERE item_id = 'C04D';
UPDATE menu_items SET price = 27000 WHERE item_id = 'C04E';
UPDATE menu_items SET price = 28000 WHERE item_id = 'C04F';
UPDATE menu_items SET price = 29000 WHERE item_id = 'C04G';
UPDATE menu_items SET price = 32000 WHERE item_id = 'C05A';
UPDATE menu_items SET price = 20000 WHERE item_id = 'C05B';
UPDATE menu_items SET price = 21000 WHERE item_id = 'C05C';
UPDATE menu_items SET price = 22000 WHERE item_id = 'C05D';
UPDATE menu_items SET price = 23000 WHERE item_id = 'C05E';
UPDATE menu_items SET price = 38000 WHERE item_id = 'C06A';
UPDATE menu_items SET price = 39000 WHERE item_id = 'C06B';
UPDATE menu_items SET price = 40000 WHERE item_id = 'C06C';
UPDATE menu_items SET price = 41000 WHERE item_id = 'C06D';
UPDATE menu_items SET price = 22000 WHERE item_id = 'C07A';
UPDATE menu_items SET price = 23000 WHERE item_id = 'C07B';
UPDATE menu_items SET price = 24000 WHERE item_id = 'C07C';
UPDATE menu_items SET price = 52000 WHERE item_id = 'C08A';
UPDATE menu_items SET price = 53000 WHERE item_id = 'C08B';
UPDATE menu_items SET price = 55000 WHERE item_id = 'C08D';
UPDATE menu_items SET price = 33000 WHERE item_id = 'C09A';
UPDATE menu_items SET price = 34000 WHERE item_id = 'C09B';
UPDATE menu_items SET price = 35000 WHERE item_id = 'C09C';
UPDATE menu_items SET price = 33000 WHERE item_id = 'C10A';
UPDATE menu_items SET price = 34000 WHERE item_id = 'C10B';
UPDATE menu_items SET price = 35000 WHERE item_id = 'C10C';
UPDATE menu_items SET price = 36000 WHERE item_id = 'C10D';
UPDATE menu_items SET price = 13000 WHERE item_id = 'C11C';
UPDATE menu_items SET price = 9000 WHERE item_id = 'CA01';
UPDATE menu_items SET price = 10000 WHERE item_id = 'CA02';
UPDATE menu_items SET price = 20000 WHERE item_id = 'D01C';
UPDATE menu_items SET price = 18000 WHERE item_id = 'D01F';
UPDATE menu_items SET price = 20000 WHERE item_id = 'D01H';
UPDATE menu_items SET price = 21000 WHERE item_id = 'D01I';
UPDATE menu_items SET price = 22000 WHERE item_id = 'D01J';
UPDATE menu_items SET price = 21000 WHERE item_id = 'D01N';
UPDATE menu_items SET price = 8000 WHERE item_id = 'PAKET MAKAN SIANG';
UPDATE menu_items SET price = 30000 WHERE item_id = 'PAKET MAKAN SIANG 50K';

-- 2) Isi harga tiap baris order_details dari harga menunya
UPDATE order_details od
JOIN menu_items mi ON mi.id = od.menu_item_id
SET od.price = mi.price;

-- 3) Hitung ulang total tiap pesanan = SUM(harga x qty)
UPDATE orders o
SET o.total = (
  SELECT COALESCE(SUM(od.price * od.qty), 0)
  FROM order_details od
  WHERE od.order_id = o.id
);

COMMIT;

-- 4) (Opsional) Cek hasil untuk sanz:
-- SELECT o.id, mi.nama_menu, mi.price, od.qty, o.total
-- FROM orders o JOIN order_details od ON od.order_id=o.id
-- JOIN menu_items mi ON mi.id=od.menu_item_id
-- WHERE o.user_id = 873 ORDER BY o.id;
