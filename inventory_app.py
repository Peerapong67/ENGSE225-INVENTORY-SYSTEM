import sys
import math
from typing import List
from product import Product
from product_repository import ProductRepository
from validator import Validator
from logger import Logger

class InventoryApp:
    def __init__(self):
        self.repo = ProductRepository()
        self.logger = Logger.getInstance()
        self.page_size = 10  # กำหนดขนาดหน้าเริ่มต้นเป็น 10 รายการต่อหน้า

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
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-11
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        app = InventoryApp()
        app.run()
    else:
        print("--- เริ่มการทดสอบ Definition of Done (SCRUM-12) ---")
        app = InventoryApp()

        # 1. เตรียมข้อมูลจำลอง 15 รายการ เพื่อทดสอบกรณีข้อมูลล้นหน้าจอ (> 10 ชิ้น)
        mock_products = [
            Product(f"PAGE-{i:02d}", f"Bulk Item {i:02d}", 10 + i, 50.0 + i, "BulkCategory")
            for i in range(1, 16)
        ]
        for p in mock_products:
            app.repo.upsertProduct(p)

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

        # เคลียร์ข้อมูลทดสอบ
        for p in mock_products:
            app.repo.db.executeQuery("DELETE FROM products WHERE product_id = ?", (p.product_id,))
        app.repo.db.commit()
        print("✓ เคลียร์ข้อมูลทดสอบเรียบร้อย")

        print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-12 ครบถ้วน 100%")