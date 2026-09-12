"""
CsvReportExporter
==================
CR-02 (Emergency Change Request): Export รายการสินค้าสต็อกต่ำเป็นไฟล์ CSV

ตามหลัก Clean Architecture ที่สไลด์ Week 10 กำหนด:
- Single Responsibility: คลาสนี้ทำหน้าที่เดียวคือแปลง Product -> ไฟล์ CSV
- แยกขาดจาก UI (ConsoleUI) และ InventoryRepository เดิม ไม่ import csv
  ปนเข้าไปในชั้นอื่นโดยตรง (กัน Tight Coupling ตาม Bad Practice ที่สไลด์เตือนไว้)
- ออกแบบเป็น Static Method: ไร้ State ทดสอบแยกได้ง่าย ไม่ต้องสร้าง instance
- ใช้ Context Manager (with open) จัดการปิดไฟล์อัตโนมัติ
- กำหนด Encoding utf-8 รองรับภาษาไทยสมบูรณ์
"""

import csv
from typing import List

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

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
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

        return len(low_stock_products)
