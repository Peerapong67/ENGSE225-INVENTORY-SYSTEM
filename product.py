class Product:
    """
    ตรงกับ class Product ใน UML diagram
    ฟิลด์: product_id, name, quantity, price, category

    มี validation พื้นฐานใน constructor เอง (ชั้นป้องกันเสริม ไม่ใช่แทนที่ Validator
    หรือ CHECK constraint ระดับฐานข้อมูล) — throw error ถ้า quantity/price ติดลบ
    """

    def __init__(self, product_id: str, name: str, quantity: int, price: float,
                 category: str = "Uncategorized"):
        """สร้าง Product object พร้อม validate ค่าเบื้องต้น (ชั้นป้องกันเสริม
        ไม่ใช่แทนที่ Validator หรือ CHECK constraint ระดับฐานข้อมูล)

        Args:
            product_id: รหัสสินค้า ห้ามเป็นค่าว่าง
            name: ชื่อสินค้า ห้ามเป็นค่าว่าง
            quantity: จำนวนสต็อก ต้องไม่ติดลบ
            price: ราคาต่อหน่วย ต้องไม่ติดลบ
            category: หมวดหมู่สินค้า ถ้าไม่ระบุจะใช้ "Uncategorized"

        Raises:
            ValueError: เมื่อ product_id/name ว่าง หรือ quantity/price ติดลบ
        """
        if not product_id:
            raise ValueError("product_id ห้ามว่าง")
        if not name:
            raise ValueError("name ห้ามว่าง")
        if quantity < 0:
            raise ValueError("quantity ต้องไม่ติดลบ")
        if price < 0:
            raise ValueError("price ต้องไม่ติดลบ")

        self.product_id = product_id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.category = category

    def to_dict(self) -> dict:
        """แปลง Product เป็น dict ธรรมดา (ใช้ตอนส่งข้อมูลออกไปนอกคลาส เช่น เทียบค่า/serialize)

        Returns:
            dict ที่มี key ครบ 5 ตัว: product_id, name, quantity, price, category
        """
        return {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "category": self.category,
        }

    @classmethod
    def from_row(cls, row) -> "Product":
        """สร้าง Product จากผลลัพธ์ query ฐานข้อมูล (ใช้โดย ProductRepository)

        Args:
            row: sqlite3.Row (หรือ dict-like object) ที่มี key product_id, name,
                quantity, price, category ตรงกับตาราง products ใน schema.sql

        Returns:
            Product instance ที่ผ่านการ validate ตาม constructor
        """
        return cls(
            product_id=row["product_id"],
            name=row["name"],
            quantity=row["quantity"],
            price=row["price"],
            category=row["category"],
        )

    def __eq__(self, other):
        """เทียบค่าความเท่ากันแบบ value equality (เทียบทุกฟิลด์ผ่าน to_dict())

        Args:
            other: object อีกตัวที่จะเทียบด้วย

        Returns:
            True ถ้าเป็น Product และทุกฟิลด์ตรงกัน, False ถ้าไม่ตรง,
            NotImplemented ถ้า other ไม่ใช่ Product
        """
        if not isinstance(other, Product):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        """คืนค่า string แทน object สำหรับ debug/print (ไม่ใช่สำหรับแสดงผลผู้ใช้)"""
        return (f"Product(product_id={self.product_id!r}, name={self.name!r}, "
                f"quantity={self.quantity}, price={self.price}, category={self.category!r})")
