class Product:
    def __init__(self, product_id: str, name: str, quantity: int, price: float, category: str = "Uncategorized"):
        # 1. Validation ป้องกันค่าติดลบในระดับ Constructor (ตามสเปก SCRUM-8)
        if quantity < 0:
            raise ValueError(f"Quantity ต้องไม่ติดลบ (ได้รับค่า: {quantity})")
        if price < 0.0:
            raise ValueError(f"Price ต้องไม่ติดลบ (ได้รับค่า: {price})")
        if not str(product_id).strip():
            raise ValueError("product_id ต้องไม่เป็นค่าว่าง")
        if not str(name).strip():
            raise ValueError("name ต้องไม่เป็นค่าว่าง")

        # 2. ฟิลด์ข้อมูลตรงตาม To-Be Class Diagram และ Database Schema
        self.product_id = str(product_id).strip()
        self.name = str(name).strip()
        self.quantity = int(quantity)
        self.price = float(price)
        self.category = str(category).strip() if category else "Uncategorized"

    def to_dict(self) -> dict:
        """แปลง Object เป็น Dictionary สำหรับส่งต่อให้ Repository หรือ Serializer"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "category": self.category
        }

    def __repr__(self) -> str:
        return f"Product(id='{self.product_id}', name='{self.name}', qty={self.quantity}, price={self.price}, cat='{self.category}')"


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-8
# ============================================================
if __name__ == "__main__":
    print("--- เริ่มการทดสอบ Definition of Done (SCRUM-8) ---")

    # 1. ทดสอบสร้าง Object ปกติ (Happy Path)
    p = Product("101", "Mama Noodles", 50, 6.0, "Food")
    assert p.product_id == "101"
    assert p.name == "Mama Noodles"
    assert p.quantity == 50
    assert p.price == 6.0
    assert p.category == "Food"
    print("✓ ผ่านเกณฑ์ 1: สร้าง Product Object สำเร็จและอ่านค่าฟิลด์ได้ถูกต้อง")

    # 2. ทดสอบแปลงเป็น Dictionary ส่งต่อให้ Repository
    d = p.to_dict()
    assert d["product_id"] == "101" and d["quantity"] == 50
    print("✓ ผ่านเกณฑ์ 2: ฟังก์ชัน to_dict() แปลงข้อมูลพร้อมส่งต่อให้ ProductRepository ได้ทันที")

    # 3. ทดสอบ Validation ป้องกัน quantity ติดลบ
    try:
        Product("102", "Bad Qty", -5, 10.0, "Drink")
        assert False, "FAILED: ต้องไม่อนุญาตให้ quantity ติดลบ"
    except ValueError as e:
        print(f"✓ ผ่านเกณฑ์ 3: ดักจับ quantity ติดลบถูกต้อง -> {e}")

    # 4. ทดสอบ Validation ป้องกัน price ติดลบ
    try:
        Product("103", "Bad Price", 10, -20.0, "Drink")
        assert False, "FAILED: ต้องไม่อนุญาตให้ price ติดลบ"
    except ValueError as e:
        print(f"✓ ผ่านเกณฑ์ 4: ดักจับ price ติดลบถูกต้อง -> {e}")

    print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-8 ครบถ้วน 100%")