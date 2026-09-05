from typing import List, Optional, Dict, Any
from database_connection import DatabaseConnection
from product import Product

class ProductRepository:
    def __init__(self):
        # เก็บ reference ไปยัง Singleton instance ตามสเปก
        self.db = DatabaseConnection.getInstance()

    def upsertProduct(self, p: Product) -> bool:
        """Insert หรือ Update ตาม product_id โดยใช้ ON CONFLICT DO UPDATE"""
        sql = """
            INSERT INTO products (product_id, name, category, quantity, price)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                quantity = excluded.quantity,
                price = excluded.price;
        """
        self.db.executeQuery(sql, (p.product_id, p.name, p.category, p.quantity, p.price))
        self.db.commit()
        return True

    def findById(self, product_id: str) -> Optional[Product]:
        """ค้นหาสินค้าตาม product_id คืนค่าเป็น Product Object หรือ None"""
        sql = "SELECT product_id, name, category, quantity, price FROM products WHERE product_id = ?"
        cursor = self.db.executeQuery(sql, (str(product_id).strip(),))
        row = cursor.fetchone()
        if row:
            return Product(
                product_id=row["product_id"],
                name=row["name"],
                quantity=row["quantity"],
                price=row["price"],
                category=row["category"]
            )
        return None

    def findAll(self) -> List[Product]:
        """ดึงรายการสินค้าทั้งหมดในระบบ เรียงตามชื่อ"""
        sql = "SELECT product_id, name, category, quantity, price FROM products ORDER BY name ASC"
        cursor = self.db.executeQuery(sql)
        rows = cursor.fetchall()
        return [
            Product(
                product_id=r["product_id"],
                name=r["name"],
                quantity=r["quantity"],
                price=r["price"],
                category=r["category"]
            )
            for r in rows
        ]

    def search(self, keyword: str) -> List[Product]:
        """ค้นหาสินค้าจาก name หรือ category ด้วย LIKE"""
        sql = """
            SELECT product_id, name, category, quantity, price 
            FROM products 
            WHERE name LIKE ? OR category LIKE ?
            ORDER BY name ASC
        """
        param = f"%{keyword.strip()}%"
        cursor = self.db.executeQuery(sql, (param, param))
        rows = cursor.fetchall()
        return [
            Product(
                product_id=r["product_id"],
                name=r["name"],
                quantity=r["quantity"],
                price=r["price"],
                category=r["category"]
            )
            for r in rows
        ]

    def updateStock(self, product_id: str, change_qty: int, reason: str = "Adjustment") -> bool:
        """
        อัปเดตสต็อกและบันทึกประวัติลงตาราง stock_movements
        change_qty: ค่าบวกคือรับเข้า, ค่าลบคือตัดออก
        """
        p = self.findById(product_id)
        if not p:
            raise ValueError(f"ไม่พบสินค้า ID: {product_id}")

        new_qty = p.quantity + change_qty
        if new_qty < 0:
            raise ValueError(f"สต็อกไม่เพียงพอ (คงเหลือ: {p.quantity}, ต้องการตัด: {abs(change_qty)})")

        try:
            # 1. อัปเดตยอดคงเหลือใน products
            sql_update = "UPDATE products SET quantity = ? WHERE product_id = ?"
            self.db.executeQuery(sql_update, (new_qty, product_id))

            # 2. บันทึกประวัติลง stock_movements (ตรงตาม schema: change_qty, reason)
            sql_movement = """
                INSERT INTO stock_movements (product_id, change_qty, reason)
                VALUES (?, ?, ?)
            """
            self.db.executeQuery(sql_movement, (product_id, change_qty, reason))

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def getSummary(self) -> Dict[str, Any]:
        """คืนค่า aggregate ตาม query ใน schema.sql"""
        sql = """
            SELECT 
                COUNT(*) AS total_products,
                COALESCE(SUM(quantity), 0) AS total_units,
                COALESCE(SUM(quantity * price), 0) AS total_value,
                COALESCE(SUM(CASE WHEN quantity <= 5 THEN 1 ELSE 0 END), 0) AS low_stock_items
            FROM products;
        """
        cursor = self.db.executeQuery(sql)
        row = cursor.fetchone()
        return {
            "total_products": row["total_products"] if row else 0,
            "total_units": row["total_units"] if row else 0,
            "total_value": float(row["total_value"]) if row else 0.0,
            "low_stock_items": row["low_stock_items"] if row else 0
        }


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-7 (กับฐานข้อมูลจริง)
# ============================================================
if __name__ == "__main__":
    print("--- เริ่มการทดสอบ Definition of Done (SCRUM-7) ---")

    repo = ProductRepository()

    # 1. ทดสอบ upsertProduct (Insert)
    test_prod = Product("REPO-1", "Repo Coffee", 10, 45.0, "Beverage")
    repo.upsertProduct(test_prod)
    found = repo.findById("REPO-1")
    assert found is not None and found.name == "Repo Coffee", "FAILED: Insert ผ่าน upsert ไม่สำเร็จ"
    print("✓ ผ่านเกณฑ์ 1: upsertProduct ทำการ Insert ข้อมูลใหม่ได้จริง")

    # 2. ทดสอบ upsertProduct (Update ข้อมูลเดิม)
    updated_prod = Product("REPO-1", "Repo Coffee Extra", 15, 50.0, "Beverage")
    repo.upsertProduct(updated_prod)
    found_updated = repo.findById("REPO-1")
    assert found_updated.name == "Repo Coffee Extra" and found_updated.quantity == 15, "FAILED: Update ไม่สำเร็จ"
    print("✓ ผ่านเกณฑ์ 2: upsertProduct อัปเดตข้อมูลทับของเดิม (ON CONFLICT) ได้จริง")

    # 3. ทดสอบ updateStock (ตัดสต็อก -3 ชิ้น)
    repo.updateStock("REPO-1", -3, "Sold to customer")
    curr = repo.findById("REPO-1")
    assert curr.quantity == 12, "FAILED: สต็อกไม่ลดลงตามที่ตัด"

    cursor = repo.db.executeQuery(
        "SELECT change_qty, reason FROM stock_movements WHERE product_id = ? ORDER BY movement_id DESC LIMIT 1",
        ("REPO-1",)
    )
    movement = cursor.fetchone()
    assert movement is not None and movement["change_qty"] == -3, "FAILED: ไม่พบประวัติใน stock_movements"
    print(f"✓ ผ่านเกณฑ์ 3: updateStock ตัดสต็อกเหลือ {curr.quantity} และบันทึกลง stock_movements (change_qty={movement['change_qty']}) สำเร็จ")

    # 4. ทดสอบ search และ findAll
    results = repo.search("Coffee")
    assert any(x.product_id == "REPO-1" for x in results), "FAILED: search ไม่พบสินค้า"
    all_prods = repo.findAll()
    assert len(all_prods) >= 1, "FAILED: findAll คืนค่าว่าง"
    print(f"✓ ผ่านเกณฑ์ 4: search() และ findAll() ค้นหาและคืนค่าข้อมูลได้ถูกต้อง (พบทั้งหมด {len(all_prods)} รายการ)")

    # 5. ทดสอบ getSummary
    summary = repo.getSummary()
    assert "total_products" in summary and "total_value" in summary and "low_stock_items" in summary
    print(f"✓ ผ่านเกณฑ์ 5: getSummary() คืนค่าสรุปผลถูกต้อง -> {summary}")

    # เคลียร์ข้อมูลทดสอบ
    repo.db.executeQuery("DELETE FROM stock_movements WHERE product_id = ?", ("REPO-1",))
    repo.db.executeQuery("DELETE FROM products WHERE product_id = ?", ("REPO-1",))
    repo.db.commit()
    print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")

    print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-7 ครบถ้วน 100%")