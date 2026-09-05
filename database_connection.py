import sqlite3
import os

class DatabaseConnection:
    # 1. ตัวแปร static เก็บตัวตนเดียวของคลาส (Singleton Instance)
    _instance = None

    def __init__(self, db_name="inventory.db"):
        """Constructor: ป้องกันไม่ให้เรียกสร้างตรงๆ จากภายนอก (ใช้ getInstance() แทน)

        Args:
            db_name: ชื่อไฟล์/path ของ SQLite database ที่จะเชื่อมต่อ

        Raises:
            Exception: เมื่อมี instance อยู่แล้ว (ต้องเรียกผ่าน getInstance() เท่านั้น)
        """
        if DatabaseConnection._instance is not None:
            raise Exception("คลาสนี้เป็น Singleton! ห้ามสร้างใหม่ ให้เรียกใช้ผ่าน getInstance() เท่านั้น")
        
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        # ตั้งค่าให้คืนผลลัพธ์เป็น row ที่เข้าถึงชื่อคอลัมน์ได้ง่าย
        self.connection.row_factory = sqlite3.Row
        self._init_tables()

    @classmethod
    def getInstance(cls, db_name="inventory.db"):
        """เมธอด static สำหรับดึง Connection เดียวทั้งระบบ (สร้างครั้งแรกถ้ายังไม่มี)

        Args:
            db_name: ชื่อไฟล์/path ของ SQLite database (ใช้เฉพาะตอนสร้างครั้งแรก
                เท่านั้น ถ้ามี instance อยู่แล้ว พารามิเตอร์นี้จะถูกละเว้น)

        Returns:
            DatabaseConnection instance เดิมเสมอไม่ว่าจะเรียกจากจุดไหนก็ตาม
        """
        if cls._instance is None:
            cls._instance = DatabaseConnection(db_name)
        return cls._instance

    def _init_tables(self):
        """อ่านไฟล์ schema.sql มารันสร้างตารางอัตโนมัติหากยังไม่มี

        ใช้ path แบบ absolute อิงตำแหน่งไฟล์นี้เอง (__file__) แทน relative path
        ตรงๆ เพราะโปรแกรมอาจถูกรันจาก working directory ใดก็ได้ ไม่ใช่แค่ root
        ของ repo เสมอไป schema.sql อยู่โฟลเดอร์เดียวกับไฟล์นี้ (repo เป็นโครงสร้าง
        แบบแบนราบ ไม่มี src/ แยก)
        """
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")

        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
            self.connection.commit()

    def executeQuery(self, sql: str, params: tuple = ()):
        """รัน SQL query (SELECT/INSERT/UPDATE/DELETE) ผ่าน connection เดียวของระบบ

        Args:
            sql: คำสั่ง SQL ที่จะรัน ใช้ "?" แทนค่าพารามิเตอร์ (parameterized query
                ป้องกัน SQL injection)
            params: ค่าที่จะแทนที่ "?" ใน sql ตามลำดับ

        Returns:
            sqlite3.Cursor ที่ใช้เรียก .fetchone()/.fetchall() ต่อได้ทันที
        """
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        return cursor

    def beginTransaction(self):
        """เริ่ม transaction — ปัจจุบันเป็น no-op เพราะ sqlite3 module จัดการ
        transaction ให้อัตโนมัติอยู่แล้วเมื่อเรียก executeQuery() (isolation_level
        เริ่มต้นเปิด implicit transaction ให้ตอนมีคำสั่ง INSERT/UPDATE/DELETE)
        """
        pass

    def commit(self):
        """ยืนยันการเปลี่ยนแปลงข้อมูล (INSERT/UPDATE/DELETE) ที่ยังไม่ commit ลงฐานข้อมูลจริง"""
        self.connection.commit()

    def rollback(self):
        """ยกเลิกการเปลี่ยนแปลงข้อมูลที่ยังไม่ commit ทั้งหมด กลับไปเป็นสถานะก่อนหน้า"""
        self.connection.rollback()


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-6
# ============================================================
if __name__ == "__main__":
    print("--- เริ่มการทดสอบ Definition of Done (SCRUM-6) ---")

    # 1. ทดสอบ: ไม่เปิด connection ซ้ำซ้อน (Singleton Verification)
    db_instance_1 = DatabaseConnection.getInstance("inventory.db")
    db_instance_2 = DatabaseConnection.getInstance("inventory.db")

    assert db_instance_1 is db_instance_2, "FAILED: Singleton ไม่ตรงกัน เกิด connection ซ้ำซ้อน"
    assert db_instance_1.connection is db_instance_2.connection, "FAILED: SQLite connection ภายในเป็นคนละตัวกัน"
    print("✓ ผ่านเกณฑ์ 1: เรียกจากหลายจุดได้ Instance เดิม และใช้ SQLite Connection เดียวกันจริง")

    # 2. ทดสอบ: "เขียน" ข้อมูล (Insert)
    test_id = "999"
    db_instance_1.executeQuery("DELETE FROM products WHERE product_id = ?", (test_id,))
    db_instance_1.commit()

    db_instance_1.executeQuery("""
        INSERT INTO products (product_id, name, quantity, price, category)
        VALUES (?, ?, ?, ?, ?)
    """, (test_id, "Test Item", 10, 50.0, "TestCategory"))
    db_instance_1.commit()
    print("✓ ผ่านเกณฑ์ 2 (เขียน): บันทึกข้อมูลสินค้าใหม่ผ่าน Connection ได้สำเร็จ")

    # 3. ทดสอบ: "อ่าน" ข้อมูล (Select)
    cursor = db_instance_2.executeQuery("SELECT name, quantity, price FROM products WHERE product_id = ?", (test_id,))
    row = cursor.fetchone()
    assert row is not None, "FAILED: อ่านข้อมูลไม่พบ"
    assert row["name"] == "Test Item", "FAILED: ข้อมูลที่อ่านได้ไม่ถูกต้อง"
    print(f"✓ ผ่านเกณฑ์ 3 (อ่าน): อ่านข้อมูลสินค้า ID {test_id} ผ่าน Connection สำเร็จ (ชื่อ: {row['name']}, คงเหลือ: {row['quantity']})")

    # 4. ทดสอบ: "แก้" ข้อมูล (Update)
    db_instance_1.executeQuery("UPDATE products SET quantity = ? WHERE product_id = ?", (25, test_id))
    db_instance_1.commit()

    cursor_after_update = db_instance_2.executeQuery("SELECT quantity FROM products WHERE product_id = ?", (test_id,))
    row_updated = cursor_after_update.fetchone()
    assert row_updated["quantity"] == 25, "FAILED: การแก้ไขข้อมูลไม่สำเร็จ"
    print(f"✓ ผ่านเกณฑ์ 4 (แก้ไข): อัปเดตจำนวนสต็อกเป็น {row_updated['quantity']} สำเร็จ")

    # ล้างข้อมูลทดสอบออกเพื่อความสะอาด
    db_instance_1.executeQuery("DELETE FROM products WHERE product_id = ?", (test_id,))
    db_instance_1.commit()
    print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")

    print("\nสรุป: ผ่านเกณฑ์ Definition of Done ครบถ้วน 100% พร้อมส่งมอบ")