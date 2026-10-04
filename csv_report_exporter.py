"""
CsvReportExporter
==================
CR-02 (Emergency Change Request): Export รายการสินค้าสต็อกต่ำเป็นไฟล์ CSV

ตามหลัก Clean Architecture ที่สไลด์ Week 10 กำหนด:
- Single Responsibility: คลาสนี้ทำหน้าที่เดียวคือแปลง Product -> ไฟล์ CSV
- แยกขาดจาก UI (ConsoleUI) และ InventoryRepository เดิม ไม่ import csv
  ปนเข้าไปในชั้นอื่นโดยตรง (กัน Tight Coupling ตาม Bad Practice ที่สไลด์เตือนไว้)
- ออกแบบเป็น Static Method: ไร้ State ทดสอบแยกได้ง่าย ไม่ต้องสร้าง instance
- เขียนไฟล์ผ่าน AtomicFileWriter: ถ้าพังกลางทาง ไฟล์รายงานเดิมไม่ถูกเขียนทับครึ่งๆ กลางๆ
- กำหนด Encoding utf-8 พร้อม BOM (utf-8-sig) รองรับภาษาไทยสมบูรณ์ทั้งในโปรแกรมทั่วไปและ Excel (BUG-106)
"""

import csv
from typing import List

from atomic_file_writer import AtomicFileWriter
from product import Product


class CsvReportExporter:
    """แปลงรายการสินค้าที่สต็อกต่ำ (Product) ให้เป็นไฟล์ CSV แบบแยกอิสระจากระบบเดิม"""

    FIELDNAMES = ["ProductID", "ProductName", "Barcode", "Quantity", "ReorderPoint", "Price"]

    @staticmethod
    def export_low_stock_products(products: List[Product], output_path: str) -> int:
        """ส่งออกรายการสินค้าสต็อกต่ำเป็นไฟล์ CSV คืนค่าจำนวนแถวที่เขียน

        รับ list ของ Product ทั้งหมด แล้วกรองเฉพาะที่ is_low_stock() เป็น True
        เอง (ตาม Impact Assessment ของสไลด์: "อ่านข้อมูลจากโมเดล Product และ
        เรียก is_low_stock()") ผู้เรียกจึงไม่ต้องกรองมาก่อนก็ได้

        Args:
            products: list ของ Product ทั้งหมดในคลัง (ยังไม่กรอง)
            output_path: path ปลายทางของไฟล์ .csv ที่จะสร้าง

        Returns:
            int: จำนวนแถว (รายการสินค้า) ที่เขียนลงไฟล์จริง
        """
        low_stock_products = [p for p in products if p.is_low_stock()]

        def write_rows(f):
            writer = csv.writer(f)
            writer.writerow(CsvReportExporter.FIELDNAMES)
            for p in low_stock_products:
                writer.writerow([
                    p.product_id,
                    p.name,
                    p.barcode,
                    p.quantity,
                    p.reorder_point,
                    p.price,
                ])

        # BUG-106: utf-8-sig เขียน BOM นำหน้าไฟล์ ให้ Excel บน Windows รู้ว่าเป็น UTF-8
        # (ไม่มี BOM จะอ่านด้วย code page ของเครื่อง เช่น cp874 แล้วชื่อภาษาไทยเพี้ยน)
        AtomicFileWriter.write(output_path, write_rows, encoding="utf-8-sig", newline='')

        return len(low_stock_products)
