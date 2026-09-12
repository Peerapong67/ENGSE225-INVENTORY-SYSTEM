from typing import List, Optional

from database_connection import DatabaseConnection
from product import Product

LOW_STOCK_THRESHOLD = 5  # ตาม query ตัวอย่างใน schema.sql (getSummary)


class ProductRepository:
    """
    ตรงกับ class ProductRepository ใน UML diagram
    -DatabaseConnection db : เก็บ reference ไปยัง singleton จาก SCRUM-6
    """

    def __init__(self, db: Optional[DatabaseConnection] = None):
        """สร้าง ProductRepository

        Args:
            db: DatabaseConnection ที่จะใช้ ถ้าไม่ระบุจะเรียก
                DatabaseConnection.getInstance() (singleton หลักของระบบ) แทน
        """
        self.db = db or DatabaseConnection.getInstance()

    def upsertProduct(self, p: Product) -> None:
        """บันทึกสินค้า: insert ใหม่ถ้ายังไม่มี product_id นี้ หรือ update ทับถ้ามีอยู่แล้ว
        (ON CONFLICT DO UPDATE ตาม schema — ป้องกันไม่ให้เกิดแถวซ้ำ id เดิม)

        Args:
            p: Product object ที่จะบันทึก
        """
        self.db.executeQuery(
            """
            INSERT INTO products
                (product_id, name, category, quantity, price, barcode, reorder_point)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                quantity = excluded.quantity,
                price = excluded.price,
                barcode = excluded.barcode,
                reorder_point = excluded.reorder_point
            """,
            (p.product_id, p.name, p.category, p.quantity, p.price,
             p.barcode, p.reorder_point),
        )
        self.db.commit()

    def findById(self, product_id: str) -> Optional[Product]:
        """ค้นหาสินค้าด้วย product_id

        Args:
            product_id: รหัสสินค้าที่ต้องการค้นหา

        Returns:
            Product ถ้าพบ, None ถ้าไม่พบ
        """
        cursor = self.db.executeQuery(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        )
        row = cursor.fetchone()
        return Product.from_row(row) if row else None

    def findAll(self) -> List[Product]:
        """ดึงสินค้าทั้งหมด เรียงตามชื่อ (a-z)

        Returns:
            list ของ Product ทั้งหมดในระบบ (list ว่างถ้าไม่มีสินค้าเลย)
        """
        cursor = self.db.executeQuery("SELECT * FROM products ORDER BY name")
        return [Product.from_row(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Product]:
        """ค้นหาสินค้าด้วยคำค้น จากชื่อหรือหมวดหมู่ (แบบ partial match, ไม่สนตัวพิมพ์เล็ก/ใหญ่)

        Args:
            keyword: คำค้นที่จะใช้ค้นในฟิลด์ name และ category

        Returns:
            list ของ Product ที่ชื่อหรือหมวดหมู่มีคำค้นนี้อยู่ เรียงตามชื่อ
        """
        pattern = f"%{keyword}%"
        cursor = self.db.executeQuery(
            "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
            (pattern, pattern),
        )
        return [Product.from_row(row) for row in cursor.fetchall()]

    def updateStock(self, product_id: str, qty: int, reason: str = "") -> None:
        """เปลี่ยนแปลงจำนวนสต็อกสินค้า พร้อมบันทึกประวัติลง stock_movements

        อัปเดตทั้งตาราง products (ยอดคงเหลือปัจจุบัน) และ insert แถวใหม่ลง
        stock_movements (ประวัติการเปลี่ยนแปลง) ในทรานแซกชันเดียวกัน

        Args:
            product_id: รหัสสินค้าที่จะเปลี่ยนสต็อก
            qty: จำนวนที่เปลี่ยนแปลง ค่าบวก = เพิ่มสต็อก, ค่าลบ = ตัดสต็อกออก
            reason: เหตุผล/หมายเหตุของการเปลี่ยนสต็อกครั้งนี้ (ค่าเริ่มต้นว่าง)

        Raises:
            ValueError: ถ้าไม่พบสินค้า product_id นี้ หรือถ้าสต็อกหลังคำนวณจะติดลบ
        """
        existing = self.findById(product_id)
        if existing is None:
            raise ValueError(f"ไม่พบสินค้า product_id={product_id}")

        new_quantity = existing.quantity + qty
        if new_quantity < 0:
            raise ValueError("สต็อกคงเหลือจะติดลบ ไม่สามารถตัดสต็อกได้")

        self.db.executeQuery(
            "UPDATE products SET quantity = ? WHERE product_id = ?",
            (new_quantity, product_id),
        )
        self.db.executeQuery(
            "INSERT INTO stock_movements (product_id, change_qty, reason) VALUES (?, ?, ?)",
            (product_id, qty, reason),
        )
        self.db.commit()

    def getSummary(self) -> dict:
        """สรุปภาพรวมคลังสินค้าทั้งหมด (ใช้แสดงในเมนู "Check Check"/รายงาน)

        Returns:
            dict ที่มี key: total_products (จำนวนชนิดสินค้า), total_units
            (จำนวนหน่วยรวม), total_value (มูลค่ารวม), low_stock_items
            (จำนวนสินค้าที่เหลือ <= LOW_STOCK_THRESHOLD)
        """
        cursor = self.db.executeQuery(
            """
            SELECT
                COUNT(*)             AS total_products,
                COALESCE(SUM(quantity), 0)          AS total_units,
                COALESCE(SUM(quantity * price), 0)  AS total_value,
                SUM(CASE WHEN quantity <= ? THEN 1 ELSE 0 END) AS low_stock_items
            FROM products
            """,
            (LOW_STOCK_THRESHOLD,),
        )
        row = cursor.fetchone()
        return {
            "total_products": row["total_products"],
            "total_units": row["total_units"],
            "total_value": row["total_value"],
            "low_stock_items": row["low_stock_items"] or 0,
        }

    def getLowStockAlerts(self) -> List[Product]:
        """CR-01: ดึงรายการสินค้าที่ถึงจุดต้องสั่งซื้อเพิ่มแล้ว (Reorder Point Alert)

        ใช้เงื่อนไข quantity <= reorder_point ต่อสินค้าแต่ละชิ้น (ต่างจาก
        LOW_STOCK_THRESHOLD ตายตัวที่ getSummary() ใช้ — ที่นี่แต่ละสินค้ามี
        จุดแจ้งเตือนของตัวเองตามที่กำหนดไว้)

        Returns:
            list ของ Product ที่ quantity <= reorder_point เรียงตามชื่อ
            (list ว่างถ้าไม่มีสินค้าใกล้หมดเลย)
        """
        cursor = self.db.executeQuery(
            "SELECT * FROM products WHERE quantity <= reorder_point ORDER BY name"
        )
        return [Product.from_row(row) for row in cursor.fetchall()]
