"""
Unit Tests สำหรับ CsvReportExporter (CR-02)
รันด้วย: pytest test_csv_report_exporter.py -v
"""

import csv

from csv_report_exporter import CsvReportExporter
from product import Product


def test_export_low_stock_to_csv_creates_valid_file(tmp_path):
    """Test 1 (ตามสไลด์ Week 10): สินค้าสต็อกต่ำ 1 รายการ ต้องถูกเขียนลง CSV ถูกต้อง"""
    # 1. Arrange: เตรียมข้อมูลสินค้าสต็อกต่ำจำลอง
    products = [
        Product(product_id="P01", name="Sugar", quantity=2, price=20.0,
                barcode="111", reorder_point=5),
    ]
    output_path = tmp_path / "test_low_stock.csv"

    # 2. Act: เรียกใช้ฟังก์ชันส่งออก CSV
    rows_written = CsvReportExporter.export_low_stock_products(products, str(output_path))

    # 3. Assert: ยืนยันว่าไฟล์ถูกสร้างจริงและข้อมูลถูกต้อง
    assert rows_written == 1
    assert output_path.exists()

    with open(output_path, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    assert reader[0] == ["ProductID", "ProductName", "Barcode", "Quantity", "ReorderPoint", "Price"]
    assert reader[1] == ["P01", "Sugar", "111", "2", "5", "20.0"]


def test_export_low_stock_excludes_products_above_reorder_point(tmp_path):
    """Test 2 (ตามสไลด์ Week 10): สินค้าที่ยังไม่ต่ำกว่า reorder_point ต้องไม่ถูก export"""
    products = [
        Product(product_id="P01", name="Sugar", quantity=2, price=20.0, reorder_point=5),
        Product(product_id="P02", name="Plenty Item", quantity=100, price=15.0, reorder_point=5),
    ]
    output_path = tmp_path / "test_low_stock_filtered.csv"

    rows_written = CsvReportExporter.export_low_stock_products(products, str(output_path))

    assert rows_written == 1  # เฉพาะ P01 เท่านั้นที่ is_low_stock() เป็น True

    with open(output_path, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    product_ids_in_file = [row[0] for row in reader[1:]]
    assert "P01" in product_ids_in_file
    assert "P02" not in product_ids_in_file
