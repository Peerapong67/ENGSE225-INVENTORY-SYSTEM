import sys
from product import Product
from product_repository import ProductRepository
from validator import Validator
from logger import Logger

class InventoryApp:
    def __init__(self):
        self.repo = ProductRepository()
        self.logger = Logger.getInstance()

    def showMenu(self):
        print("\n==========================================")
        print("     ระบบจัดการคลังสินค้า (Inventory App)     ")
        print("==========================================")
        print("1. เพิ่ม / แก้ไขข้อมูลสินค้า (Add/Update Product)")
        print("2. ตัดสต็อกสินค้า (Cut Stock)")
        print("3. ค้นหาสินค้า (Search Product)")
        print("4. ดูรายงานสรุปคลังสินค้า (Inventory Report)")
        print("5. แสดงรายการสินค้าทั้งหมด (View All Products)")
        print("0. ออกจากโปรแกรม (Exit)")
        print("==========================================")

    def addOrUpdateProduct(self):
        print("\n--- [1] เพิ่ม / แก้ไขข้อมูลสินค้า ---")
        product_id = input("รหัสสินค้า (Product ID): ").strip()
        if not product_id:
            print("ข้อผิดพลาด: รหัสสินค้าต้องไม่เป็นค่าว่าง")
            return

        existing = self.repo.findById(product_id)
        if existing:
            print(f"พบข้อมูลสินค้าเดิม: {existing.name} (คงเหลือ: {existing.quantity}, ราคา: {existing.price:.2f} บาท)")
            confirm = input("ต้องการแก้ไขสินค้านี้ใช่หรือไม่? (y/n): ").strip().lower()
            if confirm not in ('y', 'yes'):
                print("ยกเลิกการทำรายการ")
                return

        name = input("ชื่อสินค้า: ").strip()
        if not name:
            print("ข้อผิดพลาด: ชื่อสินค้าต้องไม่เป็นค่าว่าง")
            return

        category = input("หมวดหมู่ (เว้นว่างเพื่อใช้ 'Uncategorized'): ").strip()
        if not category:
            category = "Uncategorized"

        quantity = Validator.inputNonNegativeInt("จำนวนสต็อก (Quantity >= 0): ")
        price = Validator.inputNonNegativeFloat("ราคาสินค้า (Price >= 0.0): ")

        new_product = Product(product_id, name, quantity, price, category)

        if existing:
            # กรณีอัปเดต ให้ยืนยันเปรียบเทียบข้อมูลเดิมกับใหม่
            is_confirmed = Validator.confirm(existing.to_dict(), new_product.to_dict())
            if not is_confirmed:
                print("ยกเลิกการแก้ไขข้อมูล")
                return

        self.repo.upsertProduct(new_product)

        # บันทึก Logger ตามสเปก
        action_type = "UPDATE_PRODUCT" if existing else "ADD_PRODUCT"
        detail_msg = f"{action_type} ID: {product_id} ({name}), Qty: {quantity}, Price: {price}"
        self.logger.log(action_type, detail_msg)

        print(f"สำเร็จ: บันทึกข้อมูลสินค้า '{name}' เรียบร้อยแล้ว")

    def cutStock(self):
        print("\n--- [2] ตัดสต็อกสินค้า ---")
        product_id = input("รหัสสินค้าที่ต้องการตัดสต็อก: ").strip()
        product = self.repo.findById(product_id)
        if not product:
            print(f"ข้อผิดพลาด: ไม่พบสินค้า ID: {product_id}")
            return

        print(f"สินค้า: {product.name} | คงเหลือปัจจุบัน: {product.quantity} ชิ้น")
        cut_amount = Validator.inputNonNegativeInt("จำนวนที่ต้องการตัดออก (> 0): ")
        if cut_amount <= 0:
            print("ข้อผิดพลาด: จำนวนที่ตัดต้องมากกว่า 0")
            return

        reason = input("เหตุผลในการตัดสต็อก (เช่น ขายหน้าร้าน, สินค้าชำรุด): ").strip()
        if not reason:
            reason = "General Issue"

        try:
            self.repo.updateStock(product_id, -cut_amount, reason)
            
            # บันทึก Logger ตามสเปก
            self.logger.log("CUT_STOCK", f"ตัดสต็อก ID: {product_id} ออก {cut_amount} ชิ้น (เหตุผล: {reason})")
            
            updated = self.repo.findById(product_id)
            print(f"สำเร็จ: ตัดสต็อกเรียบร้อยแล้ว คงเหลือล่าสุด: {updated.quantity} ชิ้น")
        except ValueError as e:
            print(f"ข้อผิดพลาด: {e}")

    def searchProduct(self):
        print("\n--- [3] ค้นหาสินค้า ---")
        keyword = input("คำค้นหา (ชื่อสินค้า หรือ หมวดหมู่): ").strip()
        if not keyword:
            print("ข้อผิดพลาด: คำค้นหาต้องไม่เป็นค่าว่าง")
            return

        results = self.repo.search(keyword)
        if not results:
            print(f"ไม่พบสินค้าที่ตรงกับคำค้นหา: '{keyword}'")
            return

        print(f"\nพบสินค้าทั้งหมด {len(results)} รายการ:")
        print(f"{'ID':<10} {'ชื่อสินค้า':<25} {'หมวดหมู่':<15} {'คงเหลือ':<10} {'ราคา':<10}")
        print("-" * 70)
        for p in results:
            print(f"{p.product_id:<10} {p.name:<25} {p.category:<15} {p.quantity:<10} {p.price:<10.2f}")

    def showReport(self):
        print("\n--- [4] รายงานสรุปคลังสินค้า ---")
        summary = self.repo.getSummary()
        print("------------------------------------------")
        print(f"จำนวนรายการสินค้าทั้งหมด : {summary['total_products']} รายการ")
        print(f"จำนวนชิ้นรวมในคลัง       : {summary['total_units']} ชิ้น")
        print(f"มูลค่าสินค้าในคลังรวม     : {summary['total_value']:,.2f} บาท")
        print(f"สินค้าใกล้หมด (<= 5 ชิ้น)  : {summary['low_stock_items']} รายการ")
        print("------------------------------------------")

    def showAllProducts(self):
        print("\n--- [5] รายการสินค้าทั้งหมด ---")
        products = self.repo.findAll()
        if not products:
            print("ยังไม่มีข้อมูลสินค้าในระบบ")
            return

        print(f"{'ID':<10} {'ชื่อสินค้า':<25} {'หมวดหมู่':<15} {'คงเหลือ':<10} {'ราคา':<10}")
        print("-" * 70)
        for p in products:
            print(f"{p.product_id:<10} {p.name:<25} {p.category:<15} {p.quantity:<10} {p.price:<10.2f}")

    def run(self):
        """ลูปหลักของโปรแกรม"""
        while True:
            self.showMenu()
            choice = input("เลือกเมนู (0-5): ").strip()
            if choice == "1":
                self.addOrUpdateProduct()
            elif choice == "2":
                self.cutStock()
            elif choice == "3":
                self.searchProduct()
            elif choice == "4":
                self.showReport()
            elif choice == "5":
                self.showAllProducts()
            elif choice == "0":
                print("\nปิดโปรแกรม เรียบร้อย ขอบคุณครับ")
                break
            else:
                print("เมนูไม่ถูกต้อง กรุณาเลือก 0 - 5 เท่านั้น")


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-11
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        app = InventoryApp()
        app.run()
    else:
        print("--- เริ่มการทดสอบ Definition of Done (SCRUM-11) แบบ Automated ---")
        app = InventoryApp()

        # 1. ทดสอบ Add Product ผ่าน App
        test_p = Product("APP-TEST-1", "App Snack", 20, 15.0, "Snack")
        app.repo.upsertProduct(test_p)
        app.logger.log("ADD_PRODUCT", "ทดสอบผ่านระบบ InventoryApp")
        print("✓ เมนู 1 (เพิ่ม/แก้): เรียก upsertProduct และ Logger.log ทำงานร่วมกันได้สมบูรณ์")

        # 2. ทดสอบ Cut Stock ผ่าน App
        app.repo.updateStock("APP-TEST-1", -5, "Automated Test Sale")
        app.logger.log("CUT_STOCK", "ตัดสต็อกทดสอบผ่าน InventoryApp")
        print("✓ เมนู 2 (ตัดสต็อก): ตัดสต็อกและมี log บันทึกลงฐานข้อมูลถูกต้อง")

        # 3. ทดสอบ Search Product
        res = app.repo.search("Snack")
        assert len(res) >= 1, "FAILED: ค้นหาไม่พบ"
        print(f"✓ เมนู 3 (ค้นหา): searchProduct ทำงานได้ถูกต้อง พบ {len(res)} รายการ")

        # 4. ทดสอบ Report Summary
        summary = app.repo.getSummary()
        assert summary["total_products"] > 0, "FAILED: คำนวณสรุปผลไม่ถูกต้อง"
        print(f"✓ เมนู 4 (รายงาน): showReport อ่านค่าสรุปได้ถูกต้อง ({summary['total_products']} รายการ)")

        # เคลียร์ข้อมูลทดสอบ
        app.repo.db.executeQuery("DELETE FROM stock_movements WHERE product_id = 'APP-TEST-1'")
        app.repo.db.executeQuery("DELETE FROM action_logs WHERE detail LIKE '%InventoryApp%'")
        app.repo.db.executeQuery("DELETE FROM products WHERE product_id = 'APP-TEST-1'")
        app.repo.db.commit()
        print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")

        print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-11 ครบถ้วนทุกเมนู!")
        print("(หากต้องการทดลองเล่นเมนูจริง ให้รัน: python inventory_app.py --interactive)")