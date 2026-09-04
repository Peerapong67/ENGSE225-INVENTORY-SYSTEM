from database_connection import DatabaseConnection

class Logger:
    # 1. Singleton Instance ตัวแปร static
    _instance = None

    def __init__(self):
        """Constructor ป้องกันการ new object ซ้ำซ้อนโดยตรง"""
        if Logger._instance is not None:
            raise Exception("คลาสนี้เป็น Singleton! ห้ามสร้างใหม่ ให้เรียกผ่าน Logger.getInstance()")
        self.db = DatabaseConnection.getInstance()

    @classmethod
    def getInstance(cls):
        """ดึง instance เดียวของ Logger ทั้งระบบ"""
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def log(self, action: str, detail: str = ""):
        """บันทึก action และ detail ลงตาราง action_logs ในฐานข้อมูล"""
        sql = "INSERT INTO action_logs (action, detail) VALUES (?, ?)"
        self.db.executeQuery(sql, (str(action).strip(), str(detail).strip()))
        self.db.commit()


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-10
# ============================================================
if __name__ == "__main__":
    print("--- เริ่มการทดสอบ Definition of Done (SCRUM-10) ---")

    # 1. ทดสอบ Singleton Pattern
    log1 = Logger.getInstance()
    log2 = Logger.getInstance()
    assert log1 is log2, "FAILED: Logger ไม่ใช่ Singleton"
    print("✓ ผ่านเกณฑ์ 1: Logger เป็น Singleton (เรียกจากจุดไหนก็ได้ Instance เดิม)")

    # 2. ทดสอบการบันทึก Action สำคัญ: เพิ่มสินค้า
    log1.log("ADD_PRODUCT", "เพิ่มสินค้า ID: 104 (Green Tea) จำนวน 30 ชิ้น")

    # 3. ทดสอบการบันทึก Action สำคัญ: แก้ไขสต็อก
    log2.log("UPDATE_STOCK", "แก้ไขสต็อกสินค้า ID: 104 เป็น 40 ชิ้น")

    # 4. ทดสอบการบันทึก Action สำคัญ: ตัดสต็อก
    log1.log("CUT_STOCK", "ตัดสต็อกสินค้า ID: 104 ออก 5 ชิ้น (คงเหลือ 35)")

    # 5. ตรวจสอบว่าข้อมูลลงตาราง action_logs จริงในฐานข้อมูล
    cursor = log1.db.executeQuery(
        "SELECT action, detail FROM action_logs WHERE detail LIKE '%104%' ORDER BY log_id DESC LIMIT 3"
    )
    rows = cursor.fetchall()
    assert len(rows) == 3, f"FAILED: ข้อมูล log ไม่ครบคอร์ส (พบ {len(rows)} แถว)"
    
    print("✓ ผ่านเกณฑ์ 2: บันทึกข้อมูล action_logs ครบถ้วนทั้ง 3 actions สำคัญ (เพิ่ม/แก้/ตัดสต็อก)")
    for r in reversed(rows):
        print(f"   - [{r['action']}]: {r['detail']}")

    # เคลียร์ Log ข้อมูลทดสอบออกเพื่อความสะอาด
    log1.db.executeQuery("DELETE FROM action_logs WHERE detail LIKE '%104%'")
    log1.db.commit()
    print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")

    print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-10 ครบถ้วน 100%")