-- ============================================================
-- Seed data สำหรับตาราง products (แยกไฟล์จาก schema.sql โดยเจตนา
-- เพื่อไม่ให้ปนกันระหว่าง "โครงสร้าง" กับ "ข้อมูลตั้งต้น")
-- รันหลัง schema.sql เท่านั้น: sqlite3 inventory.db < schema.sql
--                              sqlite3 inventory.db < seed_data.sql
-- ============================================================

INSERT INTO products (product_id, name, category, quantity, price) VALUES
    ('101', 'Mama Noodles',  'Food',  50,  6.0),
    ('102', 'Lactasoy Milk', 'Drink', 20,  12.0),
    ('103', 'Singha Water',  'Drink', 100, 10.0)
ON CONFLICT(product_id) DO UPDATE SET
    name     = excluded.name,
    category = excluded.category,
    quantity = excluded.quantity,
    price    = excluded.price;
