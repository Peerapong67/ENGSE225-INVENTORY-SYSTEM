-- ============================================================
-- Inventory App - SQLite Database Schema
-- ออกแบบจาก UML Class Diagram (InventoryApp / ProductRepository / Product / Logger)
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1) products
--    สอดคล้องกับ class Product ใน diagram โดยตรง
--    (product_id, name, quantity, price, category)
--    เพิ่ม CHECK constraint ป้องกันค่าติดลบเป็นชั้นป้องกันสุดท้าย
--    ระดับฐานข้อมูล เสริมจาก Validator ฝั่งแอปพลิเคชัน
--    เพิ่ม created_at/updated_at เพื่อรองรับการทำรายงาน/ตรวจสอบย้อนหลัง
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id  TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL DEFAULT 'Uncategorized',
    quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    price       REAL NOT NULL DEFAULT 0 CHECK (price >= 0),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ใช้เร่งความเร็วให้ ProductRepository.search(keyword) และ findAll() ที่มี filter/sort
CREATE INDEX IF NOT EXISTS idx_products_name     ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- SQLite ไม่มี ON UPDATE CURRENT_TIMESTAMP แบบ MySQL ต้องใช้ trigger แทน
CREATE TRIGGER IF NOT EXISTS trg_products_updated_at
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    UPDATE products
       SET updated_at = datetime('now')
     WHERE product_id = OLD.product_id;
END;

-- ------------------------------------------------------------
-- 2) stock_movements
--    เก็บประวัติทุกครั้งที่สต็อกเปลี่ยน (จาก updateStock / cutStock)
--    ไม่มีใน diagram โดยตรง แต่จำเป็นสำหรับ getSummary()/รายงานย้อนหลัง
--    change_qty: ค่าบวก = เพิ่มสต็อก, ค่าลบ = ตัดสต็อกออก
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  TEXT NOT NULL,
    change_qty  INTEGER NOT NULL,
    reason      TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stock_movements_product
    ON stock_movements(product_id);

-- ------------------------------------------------------------
-- 3) action_logs
--    รองรับ class Logger (log(action, detail)) ให้เก็บ log ลงฐานข้อมูล
--    แทนการเขียนเฉพาะไฟล์/console
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS action_logs (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    action     TEXT NOT NULL,
    detail     TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_action_logs_action ON action_logs(action);

-- ============================================================
-- ตัวอย่าง query ที่ใช้ประกอบเมธอดใน ProductRepository
-- ============================================================

-- upsertProduct(Product p)
-- INSERT INTO products (product_id, name, category, quantity, price)
-- VALUES (:id, :name, :category, :quantity, :price)
-- ON CONFLICT(product_id) DO UPDATE SET
--     name = excluded.name,
--     category = excluded.category,
--     quantity = excluded.quantity,
--     price = excluded.price;

-- findById(id)
-- SELECT * FROM products WHERE product_id = :id;

-- findAll()
-- SELECT * FROM products ORDER BY name;

-- search(keyword)
-- SELECT * FROM products
-- WHERE name LIKE '%' || :keyword || '%'
--    OR category LIKE '%' || :keyword || '%';

-- updateStock(id, qty)  -- บันทึกทั้งยอดปัจจุบันและประวัติการเปลี่ยนแปลง
-- UPDATE products SET quantity = quantity + :qty WHERE product_id = :id;
-- INSERT INTO stock_movements (product_id, change_qty, reason)
-- VALUES (:id, :qty, :reason);

-- getSummary() -> Report
-- SELECT
--     COUNT(*)                    AS total_products,
--     SUM(quantity)                AS total_units,
--     SUM(quantity * price)        AS total_value,
--     SUM(CASE WHEN quantity <= 5 THEN 1 ELSE 0 END) AS low_stock_items
-- FROM products;
