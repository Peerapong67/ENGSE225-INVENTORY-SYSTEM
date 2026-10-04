"""
Unit Tests สำหรับ CsvReportExporter (CR-02)
รันด้วย: pytest test_csv_report_exporter.py -v
"""

import csv
import os
import tempfile

import pytest

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

    with open(output_path, newline="", encoding="utf-8-sig") as f:
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

    with open(output_path, newline="", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))

    product_ids_in_file = [row[0] for row in reader[1:]]
    assert "P01" in product_ids_in_file
    assert "P02" not in product_ids_in_file


def test_export_writes_utf8_bom_so_excel_reads_thai(tmp_path):
    """BUG-106: Excel บน Windows ต้องเห็น UTF-8 BOM จึงจะอ่านชื่อภาษาไทยถูก
    (ไม่มี BOM จะอ่านด้วย code page ของเครื่อง เช่น cp874 แล้วตัวอักษรเพี้ยน)"""
    products = [Product("P01", "น้ำดื่มสิงห์ 600ml", 2, 7.0, reorder_point=5)]
    output_path = tmp_path / "thai.csv"

    CsvReportExporter.export_low_stock_products(products, str(output_path))

    raw = output_path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(raw.decode("utf-8-sig").splitlines()))
    assert rows[0][0] == "ProductID"
    assert rows[1][1] == "น้ำดื่มสิงห์ 600ml"


def test_export_failure_keeps_existing_report_intact(tmp_path):
    """Atomic write: ถ้าเขียน CSV พังกลางทาง ไฟล์รายงานเดิมต้องไม่ถูกเขียนทับครึ่งๆ กลางๆ"""
    output_path = tmp_path / "report.csv"
    output_path.write_text("old report", encoding="utf-8")

    class BrokenProduct:
        """สินค้าจำลองที่พังตอนอ่าน price (เขียนแถวแรกไปแล้วค่อยพังที่แถวนี้)"""
        product_id, name, barcode, quantity, reorder_point = "P02", "Broken", "", 1, 5

        def is_low_stock(self):
            return True

        @property
        def price(self):
            raise RuntimeError("จำลองข้อผิดพลาดระหว่างเขียนแถว")

    products = [Product("P01", "Sugar", 2, 20.0, reorder_point=5), BrokenProduct()]

    with pytest.raises(RuntimeError):
        CsvReportExporter.export_low_stock_products(products, str(output_path))

    assert output_path.read_text(encoding="utf-8") == "old report"
    assert [p.name for p in tmp_path.iterdir()] == ["report.csv"]  # ไม่มี .tmp ค้าง


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_csv_report_exporter.py
# ============================================================

def _export_and_read(products):
    """ช่วย export แล้วอ่านผลลัพธ์กลับมาเป็น (จำนวนแถวที่เขียน, rows ในไฟล์)"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "report.csv")
        count = CsvReportExporter.export_low_stock_products(products, output_path)
        with open(output_path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        return count, rows


def _run_terminal_demo():
    print("=" * 85)
    print(" 📤  CSVREPORTEXPORTER (CR-02) DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    cases = [
        {
            "id": "TC-CSV-01",
            "method": "Single Low Stock Export & Header Integrity",
            "data": "id='P01', name='Sugar', qty=2, reorder_point=5, barcode='111'",
            "action": lambda: _export_and_read(
                [Product("P01", "Sugar", 2, 20.0, barcode="111", reorder_point=5)]
            ),
            "verify": lambda res: res[0] == 1 and res[1][0] == [
                "ProductID", "ProductName", "Barcode", "Quantity", "ReorderPoint", "Price"
            ],
            "expected": "เขียน Header ครบ 6 คอลัมน์ และแถวข้อมูลสินค้าสต็อกต่ำ 1 รายการถูกต้อง"
        },
        {
            "id": "TC-CSV-02",
            "method": "Filtering Logic (is_low_stock delegation)",
            "data": "P01: qty=2/reorder=5 (ต่ำ), P02: qty=100/reorder=5 (ปกติ)",
            "action": lambda: _export_and_read([
                Product("P01", "Sugar", 2, 20.0, reorder_point=5),
                Product("P02", "Plenty Item", 100, 15.0, reorder_point=5),
            ]),
            "verify": lambda res: res[0] == 1 and len(res[1]) == 2,
            "expected": "กรองเฉพาะสินค้าที่ is_low_stock()==True เท่านั้น ตัดสินค้าปกติออกจากไฟล์"
        },
        {
            "id": "TC-CSV-03",
            "method": "Zero Result Edge Case",
            "data": "สินค้าทั้งหมดมี qty มากกว่า reorder_point",
            "action": lambda: _export_and_read([
                Product("P03", "All Good", 999, 1.0, reorder_point=5),
            ]),
            "verify": lambda res: res[0] == 0 and len(res[1]) == 1,
            "expected": "คืนค่า 0 แถว แต่ยังสร้างไฟล์พร้อม Header ไว้เสมอ (ไม่ error เมื่อไม่มีสินค้าต่ำ)"
        },
        {
            "id": "TC-CSV-04",
            "method": "Stateless Static Method Design (Single Responsibility)",
            "data": "ตรวจสอบว่า export_low_stock_products เป็น @staticmethod",
            "action": lambda: isinstance(
                CsvReportExporter.__dict__["export_low_stock_products"], staticmethod
            ),
            "verify": lambda res: res is True,
            "expected": "เรียกใช้ได้โดยไม่ต้องสร้าง instance ยืนยันว่าไม่มี State แยกอิสระจาก UI/Repository"
        },
    ]

    passed_count = 0
    for idx, c in enumerate(cases, 1):
        try:
            res = c["action"]()
            is_ok = c["verify"](res)
        except Exception as e:
            res = f"Exception: {e}"
            is_ok = False

        status_tag = "[ PASSED ] ✓" if is_ok else "[ FAILED ] ✗"
        if is_ok:
            passed_count += 1

        print(f"\n{idx}. Case ID: {c['id']}  {status_tag}")
        print(f"   • วิธีการทดสอบ  : {c['method']}")
        print(f"   • ชุดข้อมูลทดสอบ: {c['data']}")
        print(f"   • ผลลัพธ์ที่ได้  : {c['expected']}")

    print("\n" + "-" * 85)
    print(f"สรุปภาพรวม: ผ่านการทดสอบ {passed_count}/{len(cases)} เคส (Pass Rate: {(passed_count/len(cases))*100:.1f}%)")
    print("=" * 85)


if __name__ == "__main__":
    _run_terminal_demo()
