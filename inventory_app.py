import sys
import math
from typing import List
from product import Product
from product_repository import ProductRepository, LOW_STOCK_THRESHOLD
from validator import Validator
from logger import Logger

class InventoryApp:
    def __init__(self):
        """สร้าง InventoryApp พร้อมเชื่อม ProductRepository และ Logger (singleton)
        เข้าด้วยกัน — ProductRepository จะไปดึง DatabaseConnection singleton ที่มี
        อยู่แล้วในระบบเอง (ต้องมี DatabaseConnection ถูก getInstance() มาก่อนแล้ว
        อย่างน้อยหนึ่งครั้ง เช่น ผ่าน fixture ตอนเทสต์ หรือตอนโปรแกรมเริ่มทำงานจริง)
        """
        self.repo = ProductRepository()
        self.logger = Logger.getInstance()
        self.page_size = 10  # กำหนดขนาดหน้าเริ่มต้นเป็น 10 รายการต่อหน้า

    def showMenu(self):
        """แสดงเมนูหลักของโปรแกรม"""
        print("\n==================== INVENTORY SYSTEM ====================")
        print("1. แสดงสินค้าทั้งหมด (Show all)")
        print("2. เพิ่ม/แก้ไขสินค้า (Add or Update)")
        print("3. ตัดสต็อก (Cut stock)")
        print("4. รายงานสรุป (Report)")
        print("5. ค้นหาสินค้า (Search)")
        print("6. ออกจากโปรแกรม (Exit)")

    def run(self):
        """ลูปหลักของโปรแกรม: แสดงเมนู รับคำสั่ง แล้ว dispatch ไปยังเมธอดที่เกี่ยวข้อง
        วนซ้ำจนกว่าผู้ใช้จะเลือกออก (choice "6")
        """
        while True:
            self.showMenu()
            choice = input("เลือกเมนู: ").strip()

            if choice == "1":
                self.showAllProducts()
            elif choice == "2":
                self.addOrUpdateProduct()
            elif choice == "3":
                self.cutStock()
            elif choice == "4":
                self.showReport()
            elif choice == "5":
                self.searchProduct()
            elif choice == "6":
                print("ขอบคุณที่ใช้บริการ")
                break
            else:
                print(">> ตัวเลือกไม่ถูกต้อง กรุณาเลือก 1-6")

    def addOrUpdateProduct(self):
        """เพิ่มสินค้าใหม่ หรือแก้ไขสินค้าที่มีอยู่แล้ว (upsert ผ่าน ProductRepository)

        ถ้า product_id ที่กรอกมีอยู่แล้ว จะให้ผู้ใช้ยืนยันก่อนบันทึกทับผ่าน
        Validator.confirm() ก่อนเสมอ ป้องกันการเขียนทับข้อมูลโดยไม่ตั้งใจ
        (ตาม risk register ที่เตือนไว้)
        """
        print("\n--- [2] เพิ่ม/แก้ไขสินค้า (Add or Update Product) ---")
        product_id = input("รหัสสินค้า (Product ID): ").strip()
        if not product_id:
            print("ข้อผิดพลาด: รหัสสินค้าต้องไม่เป็นค่าว่าง")
            return

        existing = self.repo.findById(product_id)

        name = input("ชื่อสินค้า: ").strip()
        quantity = Validator.inputNonNegativeInt("จำนวนคงเหลือ: ")
        price = Validator.inputNonNegativeFloat("ราคาต่อหน่วย: ")
        category = input("หมวดหมู่: ").strip() or "Uncategorized"

        try:
            new_product = Product(product_id, name, quantity, price, category)
        except ValueError as e:
            print(f"ข้อผิดพลาด: {e}")
            return

        if existing is not None:
            confirmed = Validator.confirm(existing.to_dict(), new_product.to_dict())
            if not confirmed:
                print("ยกเลิกการบันทึก")
                return

        self.repo.upsertProduct(new_product)
        action = "UPDATE_PRODUCT" if existing is not None else "ADD_PRODUCT"
        self.logger.log(action, f"product_id={product_id}")
        print("บันทึกสำเร็จ")

    def cutStock(self):
        """ตัดสต็อกสินค้าออกตามจำนวนที่ผู้ใช้ระบุ พร้อมเตือนถ้าสต็อกเหลือน้อย

        เช็คว่าสต็อกพอก่อนตัดจริง (ไม่ปล่อยให้ ProductRepository.updateStock()
        raise ValueError เป็นด่านแรก) เพื่อให้ error message เป็นมิตรกับผู้ใช้
        """
        print("\n--- [3] ตัดสต็อกสินค้า (Cut Stock) ---")
        product_id = input("รหัสสินค้าที่จะตัดสต็อก: ").strip()
        product = self.repo.findById(product_id)
        if product is None:
            print("ไม่พบสินค้ารหัสนี้")
            return

        amount = Validator.inputNonNegativeInt("จำนวนที่ต้องการตัดออก: ")
        if amount > product.quantity:
            print("ข้อผิดพลาด: สต็อกไม่พอสำหรับตัดจำนวนนี้")
            return

        try:
            self.repo.updateStock(product_id, -amount, reason="cutStock")
        except ValueError as e:
            print(f"ข้อผิดพลาด: {e}")
            return

        self.logger.log("CUT_STOCK", f"product_id={product_id} qty=-{amount}")
        print("ตัดสต็อกสำเร็จ")

        updated = self.repo.findById(product_id)
        if updated.quantity < LOW_STOCK_THRESHOLD:
            print(f"!!! คำเตือน: สินค้า '{updated.name}' เหลือสต็อกต่ำ ({updated.quantity} ชิ้น) !!!")

    def showReport(self):
        """แสดงรายงานสรุปคลังสินค้าทั้งหมด (จำนวนชนิด, หน่วยรวม, มูลค่ารวม, สินค้าใกล้หมด)"""
        print("\n--- [4] รายงานสรุปคลังสินค้า (Report) ---")
        summary = self.repo.getSummary()
        print(f"จำนวนชนิดสินค้าทั้งหมด: {summary['total_products']}")
        print(f"จำนวนหน่วยสินค้ารวม: {summary['total_units']}")
        print(f"มูลค่าสินค้ารวม: {summary['total_value']:.2f} บาท")
        print(f"จำนวนสินค้าใกล้หมด (<= {LOW_STOCK_THRESHOLD}): {summary['low_stock_items']}")

    def displayPaginatedProducts(self, products: List[Product], title: str = "รายการสินค้า"):
        """ฟังก์ชันช่วยแสดงผลรายการสินค้าแบบแบ่งหน้า (Pagination) ไม่ให้ล้นหน้าจอ"""
        if not products:
            print(f"\nไม่พบข้อมูลสำหรับ: {title}")
            return

        total_items = len(products)
        total_pages = math.ceil(total_items / self.page_size)
        current_page = 1

        while True:
            start_idx = (current_page - 1) * self.page_size
            end_idx = min(start_idx + self.page_size, total_items)
            page_items = products[start_idx:end_idx]

            print(f"\n==================== {title} (หน้า {current_page}/{total_pages}) ====================")
            print(f"{'ลำดับ':<6} {'ID':<12} {'ชื่อสินค้า':<25} {'หมวดหมู่':<15} {'คงเหลือ':<10} {'ราคา':<10}")
            print("-" * 80)
            for idx, p in enumerate(page_items, start=start_idx + 1):
                print(f"{idx:<6} {p.product_id:<12} {p.name:<25} {p.category:<15} {p.quantity:<10} {p.price:<10.2f}")
            print("-" * 80)
            print(f"แสดงรายการที่ {start_idx + 1} - {end_idx} จากทั้งหมด {total_items} รายการ")

            if total_pages <= 1:
                input("\nกด Enter เพื่อกลับสู่เมนู...")
                break

            print("\n[n] หน้าถัดไป | [p] หน้าก่อนหน้า | [q] ออกจากหน้านี้")
            nav = input("เลือกการทำงาน: ").strip().lower()

            if nav == 'n':
                if current_page < total_pages:
                    current_page += 1
                else:
                    print(">> อยู่ที่หน้าสุดท้ายแล้ว")
            elif nav == 'p':
                if current_page > 1:
                    current_page -= 1
                else:
                    print(">> อยู่ที่หน้าแรกแล้ว")
            elif nav == 'q':
                break
            else:
                print(">> คำสั่งไม่ถูกต้อง กรุณาเลือก n, p หรือ q")

    def searchProduct(self):
        """ค้นหาสินค้าตามชื่อหรือหมวดหมู่ พร้อมแสดงผลแบบ Pagination"""
        print("\n--- [3] ค้นหาสินค้า (Search Product) ---")
        keyword = input("คำค้นหา (ชื่อสินค้า หรือ หมวดหมู่): ").strip()
        if not keyword:
            print("ข้อผิดพลาด: คำค้นหาต้องไม่เป็นค่าว่าง")
            return

        results = self.repo.search(keyword)
        self.logger.log("SEARCH_PRODUCT", f"ค้นหาด้วยคำว่า '{keyword}' พบ {len(results)} รายการ")
        self.displayPaginatedProducts(results, title=f"ผลการค้นหา '{keyword}'")

    def showAllProducts(self):
        """แสดงรายการสินค้าทั้งหมด พร้อมระบบ Pagination"""
        products = self.repo.findAll()
        self.displayPaginatedProducts(products, title="รายการสินค้าทั้งหมดในระบบ")


# ============================================================
# Entry point:
#   python inventory_app.py              -> เข้าเมนูจริง (interactive) ทันที — ค่า default
#   python inventory_app.py --selftest   -> รัน self-test สำหรับ DoD ของ SCRUM-11/12
#                                            (ใช้ตอน dev ตรวจ DoD เร็วๆ ไม่ต้อง
#                                            เปิดเมนูเอง — ไม่ใช่ทางเข้าใช้งานหลัก)
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        print("--- เริ่มการทดสอบ Definition of Done (SCRUM-12) ---")
        app = InventoryApp()

        # 1. เตรียมข้อมูลจำลอง 15 รายการ เพื่อทดสอบกรณีข้อมูลล้นหน้าจอ (> 10 ชิ้น)
        mock_products = [
            Product(f"PAGE-{i:02d}", f"Bulk Item {i:02d}", 10 + i, 50.0 + i, "BulkCategory")
            for i in range(1, 16)
        ]
        for p in mock_products:
            app.repo.upsertProduct(p)

        # ใช้ try/finally ครอบตั้งแต่ตรงนี้ เพื่อรับประกันว่าข้อมูลจำลองจะถูกลบออก
        # จาก inventory.db เสมอ ไม่ว่า assert ด้านล่างจะผ่านหรือ fail กลางทางก็ตาม
        # (ก่อนแก้ ถ้า assert ไหน fail กลางทาง โค้ด cleanup ท้ายไฟล์จะไม่ถูกรันเลย
        # ทำให้สินค้าจำลอง PAGE-01..15 ค้างอยู่ใน DB จริงถาวร)
        try:
            # 2. ทดสอบ search(keyword) ด้วย category
            search_res = app.repo.search("BulkCategory")
            assert len(search_res) == 15, f"FAILED: search ผลลัพธ์ไม่ครบ 15 รายการ (ได้ {len(search_res)})"
            print(f"✓ ผ่านเกณฑ์ 1: ค้นหาด้วย category สำเร็จ พบ {len(search_res)} รายการ")

            # 3. ตรวจสอบการคำนวณแบ่งหน้า (Pagination Calculation)
            total_items = len(search_res)
            expected_pages = math.ceil(total_items / app.page_size)
            assert expected_pages == 2, f"FAILED: จำนวนหน้าคำนวณผิด (คาดหวัง 2 ได้ {expected_pages})"

            first_page = search_res[0:app.page_size]
            second_page = search_res[app.page_size:total_items]
            assert len(first_page) == 10, "FAILED: หน้าแรกไม่มี 10 รายการ"
            assert len(second_page) == 5, "FAILED: หน้าที่สองไม่มี 5 รายการ"
            print(f"✓ ผ่านเกณฑ์ 2: แบ่งหน้าแสดงผลถูกต้อง (หน้า 1 มี {len(first_page)} ชิ้น, หน้า 2 มี {len(second_page)} ชิ้น)")

            # 4. ทดสอบ search ด้วยชื่อสินค้าบางส่วน (Partial Match)
            name_res = app.repo.search("Bulk Item 05")
            assert len(name_res) == 1 and name_res[0].product_id == "PAGE-05", "FAILED: ค้นหาด้วยชื่อไม่ตรง"
            print("✓ ผ่านเกณฑ์ 3: ค้นหาด้วยชื่อสินค้าเฉพาะเจาะจงสำเร็จ")

            print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-12 ครบถ้วน 100%")
        finally:
            # เคลียร์ข้อมูลทดสอบ — รันเสมอไม่ว่า assert ด้านบนจะผ่านหรือไม่ก็ตาม
            for p in mock_products:
                app.repo.db.executeQuery("DELETE FROM products WHERE product_id = ?", (p.product_id,))
            app.repo.db.commit()
            print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")
    else:
        # ค่า default: ไม่มี flag ใดๆ -> เข้าเมนู interactive ทันที
        app = InventoryApp()
        app.run()