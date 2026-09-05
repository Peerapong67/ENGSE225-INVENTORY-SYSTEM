from database_connection import DatabaseConnection


class Logger:
    """
    ตรงกับ class Logger ใน UML diagram — Singleton pattern แบบเดียวกับ DatabaseConnection
    log(action, detail) บันทึกลงตาราง action_logs ที่ออกแบบไว้ใน SCRUM-5
    """

    _instance = None

    def __init__(self):
        """Constructor: ป้องกันไม่ให้เรียกสร้างตรงๆ จากภายนอก

        Raises:
            Exception: เมื่อมี instance อยู่แล้ว (ต้องเรียกผ่าน getInstance() เท่านั้น)
        """
        if Logger._instance is not None:
            raise Exception("คลาสนี้เป็น Singleton! ห้ามสร้างใหม่ ให้เรียกใช้ผ่าน getInstance() เท่านั้น")

    @classmethod
    def getInstance(cls) -> "Logger":
        """เมธอด static สำหรับดึง Logger instance เดียวทั้งระบบ (สร้างครั้งแรกถ้ายังไม่มี)

        Returns:
            Logger instance เดิมเสมอไม่ว่าจะเรียกจากจุดไหนก็ตาม
        """
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def log(self, action: str, detail: str = "") -> None:
        """บันทึก action สำคัญ (เพิ่ม/แก้/ตัดสต็อก) ลงตาราง action_logs ทันที (auto-commit)

        Args:
            action: ชื่อ action ที่เกิดขึ้น เช่น "ADD_PRODUCT", "CUT_STOCK"
            detail: รายละเอียดเพิ่มเติมของ action นั้น (ค่าเริ่มต้นเป็นสตริงว่าง)
        """
        db = DatabaseConnection.getInstance()
        db.executeQuery(
            "INSERT INTO action_logs (action, detail) VALUES (?, ?)",
            (action, detail),
        )
        db.commit()
