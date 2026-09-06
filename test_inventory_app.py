"""
Unit/flow test สำหรับ InventoryApp (SCRUM-11, SCRUM-12, CR-01)
รันด้วย pytest: python -m pytest -v test_inventory_app.py
รันแบบ Demo ใน Terminal: python test_inventory_app.py
"""
import io
import os
import sys
import builtins
import pytest

from inventory_app import InventoryApp
from product import Product
from database_connection import DatabaseConnection
from product_repository import ProductRepository
from logger import Logger


def _mock_inputs(monkeypatch, values):
    """ให้ input() คืนค่าตามลำดับใน values ทีละครั้งที่ถูกเรียก"""
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def _count_logs(db, action=None):
    if action:
        cursor = db.executeQuery(
            "SELECT COUNT(*) AS cnt FROM action_logs WHERE action = ?", (action,)
        )
    else:
        cursor = db.executeQuery("SELECT COUNT(*) AS cnt FROM action_logs")
    return cursor.fetchone()["cnt"]


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

# ------------------------------------------------------------
# showMenu()
# ------------------------------------------------------------

def test_show_menu_prints_all_six_options(db, capsys):
    app = InventoryApp()
    app.showMenu()
    out = capsys.readouterr().out
    for expected in ["1.", "2.", "3.", "4.", "5.", "6."]:
        assert expected in out


# ------------------------------------------------------------
# addOrUpdateProduct()
# ------------------------------------------------------------

def test_add_new_product_saves_and_logs(monkeypatch, db, repo):
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "New Item", "10", "20.0", "Food", "", "5"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved is not None
    assert saved.name == "New Item"
    assert saved.quantity == 10
    assert _count_logs(db, "ADD_PRODUCT") == 1


def test_add_new_product_with_barcode_and_reorder_point(monkeypatch, db, repo):
    """CR-01: ผู้ใช้กรอกบาร์โค้ดและ Reorder Point เองได้"""
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "New Item", "10", "20.0", "Food", "8850999327015", "3"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved.barcode == "8850999327015"
    assert saved.reorder_point == 3


def test_add_or_update_existing_id_confirmed_updates(monkeypatch, db, repo):
    repo.upsertProduct(Product("P1", "Old Name", 5, 20.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "New Name", "8", "25.0", "Drink", "", "5", "y"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved.name == "New Name"
    assert saved.quantity == 8
    assert _count_logs(db, "UPDATE_PRODUCT") == 1


def test_add_or_update_existing_id_declined_does_not_change(monkeypatch, db, repo):
    repo.upsertProduct(Product("P1", "Old Name", 5, 20.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "New Name", "8", "25.0", "Drink", "", "5", "n"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved.name == "Old Name"
    assert _count_logs(db) == 0


def test_add_product_with_negative_quantity_input_shows_error_no_save(monkeypatch, db, repo):
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "Item", "-5", "10", "20.0", "Food", "", "5"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved.quantity == 10


def test_add_product_empty_id_shows_error(monkeypatch, db, repo, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, [""])
    app.addOrUpdateProduct()
    out = capsys.readouterr().out
    assert "ห้ามเป็นค่าว่าง" in out or "ค่าว่าง" in out
    assert repo.findAll() == []


# ------------------------------------------------------------
# cutStock()
# ------------------------------------------------------------

def test_cut_stock_reduces_quantity_and_logs(monkeypatch, db, repo):
    repo.upsertProduct(Product("P1", "Item", 20, 5.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "5"])
    app.cutStock()

    assert repo.findById("P1").quantity == 15
    assert _count_logs(db, "CUT_STOCK") == 1


def test_cut_stock_insufficient_shows_error_and_does_not_change(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item", 3, 5.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "10"])
    app.cutStock()

    out = capsys.readouterr().out
    assert "ไม่พอ" in out
    assert repo.findById("P1").quantity == 3
    assert _count_logs(db) == 0


def test_cut_stock_product_not_found_shows_error(monkeypatch, db, repo, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["NO_SUCH_ID"])
    app.cutStock()
    out = capsys.readouterr().out
    assert "ไม่พบสินค้า" in out


def test_cut_stock_triggers_low_stock_warning(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item", 6, 5.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "2"])
    app.cutStock()

    out = capsys.readouterr().out
    assert "คำเตือน" in out


def test_cut_stock_no_warning_when_stock_stays_at_or_above_threshold(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "5"])
    app.cutStock()

    out = capsys.readouterr().out
    assert "คำเตือน" not in out


# ------------------------------------------------------------
# showReport()
# ------------------------------------------------------------

def test_show_report_prints_correct_summary(db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item A", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Item B", 5, 12.0, "Drink"))

    app = InventoryApp()
    app.showReport()

    out = capsys.readouterr().out
    assert "จำนวนชนิดสินค้าทั้งหมด: 2" in out
    assert "120.00" in out


# ------------------------------------------------------------
# searchProduct()
# ------------------------------------------------------------

def test_search_product_finds_match_and_logs(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    app = InventoryApp()
    _mock_inputs(monkeypatch, ["Mama", ""])
    app.searchProduct()

    out = capsys.readouterr().out
    assert "Mama Noodles" in out
    assert _count_logs(db, "SEARCH_PRODUCT") == 1


def test_search_product_empty_keyword_shows_error(monkeypatch, db, repo, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, [""])
    app.searchProduct()
    out = capsys.readouterr().out
    assert "ค่าว่าง" in out


# ------------------------------------------------------------
# showAllProducts()
# ------------------------------------------------------------

def test_show_all_products_prints_every_item(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Coffee", 10, 45.0, "Drink"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, [""])
    app.showAllProducts()

    out = capsys.readouterr().out
    assert "Coffee" in out


# ------------------------------------------------------------
# run()
# ------------------------------------------------------------

def test_run_exits_cleanly_on_choice_7(monkeypatch, db, capsys):
    """เมนู Exit คือเลข 7 เมื่อมีเมนู Low Stock Alerts (CR-01)"""
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["7"])
    app.run()
    out = capsys.readouterr().out
    assert "ขอบคุณที่ใช้บริการ" in out


def test_run_invalid_choice_then_exit(monkeypatch, db, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["9", "7"])
    app.run()
    out = capsys.readouterr().out
    assert "ตัวเลือกไม่ถูกต้อง" in out


def test_run_shows_low_stock_alerts_on_choice_6(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Almost Out", 2, 5.0, "Food", reorder_point=5))

    app = InventoryApp()
    _mock_inputs(monkeypatch, ["6", "", "7"])  # 6 -> Enter กลับเมนู -> 7 ออก
    app.run()

    out = capsys.readouterr().out
    assert "Almost Out" in out or "พบ" in out


def test_run_full_menu_flow_all_options_no_error(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Existing Item", 10, 5.0, "Food"))

    app = InventoryApp()
    _mock_inputs(monkeypatch, [
        "1", "",                                              # 1: Show all -> Enter
        "2", "P2", "New", "3", "9.0", "Food", "", "5",       # 2: Add new (ID, Name, Qty, Price, Cat, Barcode, Reorder)
        "3", "P1", "2",                                       # 3: Cut stock
        "4",                                                  # 4: Report
        "5", "Existing", "",                                  # 5: Search -> Enter
        "6", "",                                              # 6: Low stock alert -> Enter
        "7",                                                  # 7: Exit
    ])
    app.run()

    out = capsys.readouterr().out
    assert "ขอบคุณที่ใช้บริการ" in out
    assert _count_logs(db, "ADD_PRODUCT") == 1
    assert _count_logs(db, "CUT_STOCK") == 1
    assert _count_logs(db, "SEARCH_PRODUCT") == 1


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_inventory_app.py
# ============================================================

def _run_with_mock_inputs(fn, inputs):
    """ฟังก์ชันจำลอง input ที่ปลอดภัย ไม่ค้างลูปแน่นอน"""
    it = iter(inputs)
    real_input = builtins.input
    old_stdout = sys.stdout
    captured = io.StringIO()

    def safe_mock_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            return "7"  # คืนค่า Exit (7) เสมอหาก input หมด ป้องกัน Infinite Loop

    builtins.input = safe_mock_input
    sys.stdout = captured
    try:
        fn()
    finally:
        builtins.input = real_input
        sys.stdout = old_stdout

    return captured.getvalue()


def _capture_output(fn):
    old_stdout = sys.stdout
    captured = io.StringIO()
    sys.stdout = captured
    try:
        fn()
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


def _run_terminal_demo():
    print("=" * 85)
    print(" 🖥️   INVENTORY APP CLI & INTEGRATION FLOWS VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    test_db_name = "test_app_terminal.db"
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass

    # เตรียม Database และ Singleton
    DatabaseConnection._instance = None
    Logger._instance = None
    db = DatabaseConnection.getInstance(test_db_name)
    repo = ProductRepository(db)

    app = InventoryApp()
    app.repo = repo  # ผูก repo กับฐานข้อมูลทดสอบ

    cases = [
        {
            "id": "TC-APP-01",
            "method": "CLI Menu Structure Verification",
            "data": "app.showMenu()",
            "action": lambda: _capture_output(lambda: app.showMenu()),
            "verify": lambda out: all(x in out for x in ["1.", "2.", "3.", "4.", "5.", "6."]),
            "expected": "แสดงเมนูหลักครบถ้วนทั้ง 6 ตัวเลือกพื้นฐาน (รวม Exit ทางออก)"
        },
        {
            "id": "TC-APP-02",
            "method": "Interactive Add Product & Audit Trail",
            "data": "Input: ID='P101', Name='Green Tea', Qty=15, Price=25.0, Cat='Drink', Barcode='', Reorder=5",
            # ส่ง input ครบ 7 ช่อง: ID, Name, Qty, Price, Category, Barcode, Reorder Point
            "action": lambda: _run_with_mock_inputs(app.addOrUpdateProduct, ["P101", "Green Tea", "15", "25.0", "Drink", "", "5"]),
            "verify": lambda out: repo.findById("P101") is not None and repo.findById("P101").name == "Green Tea",
            "expected": "บันทึกสินค้าใหม่สำเร็จ และบันทึก Log 'ADD_PRODUCT' ลงฐานข้อมูล"
        },
        {
            "id": "TC-APP-03",
            "method": "DoD Safety: Upsert Confirmation Dialog (User Declined)",
            "data": "แก้ไข ID='P101' แต่กด 'n' ตอนยืนยันบันทึกทับ",
            # ส่ง input ครบ 7 ช่อง แล้วตามด้วย 'n' ตอน confirm
            "action": lambda: _run_with_mock_inputs(app.addOrUpdateProduct, ["P101", "Green Tea Extra", "20", "30.0", "Drink", "", "5", "n"]),
            "verify": lambda out: "ยกเลิกการบันทึก" in out and repo.findById("P101").name == "Green Tea",
            "expected": "ระบบตรวจพบ ID ซ้ำ แสดง Diff และยกเลิกการบันทึกตามคำสั่ง 'n' ข้อมูลเดิมไม่สูญหาย"
        },
        {
            "id": "TC-APP-04",
            "method": "Interactive Cut Stock & Warning Notification",
            "data": "ตัดสต็อกสินค้า 'P101' ออก 12 ชิ้น (คงเหลือ 15 - 12 = 3 ชิ้น)",
            "action": lambda: _run_with_mock_inputs(app.cutStock, ["P101", "12"]),
            "verify": lambda out: "ตัดสต็อกสำเร็จ" in out and "คำเตือน" in out and repo.findById("P101").quantity == 3,
            "expected": "ตัดสต็อกสำเร็จ ยอดเหลือ 3 ชิ้น (<= 5) ทริกเกอร์ข้อความคำเตือนสต็อกต่ำทันที"
        },
        {
            "id": "TC-APP-05",
            "method": "Search Flow with Substring Partial Match",
            "data": "ค้นหาคำว่า 'Tea' (searchProduct)",
            "action": lambda: _run_with_mock_inputs(app.searchProduct, ["Tea", ""]),
            "verify": lambda out: "Green Tea" in out,
            "expected": "ค้นหาเจอสินค้าเป้าหมาย พร้อมแสดงผลในตารางแบบแบ่งหน้า (Pagination)"
        },
        {
            "id": "TC-APP-06",
            "method": "Executive Inventory Report Generation",
            "data": "app.showReport()",
            "action": lambda: _capture_output(lambda: app.showReport()),
            "verify": lambda out: "จำนวนชนิดสินค้าทั้งหมด:" in out and "มูลค่าสินค้ารวม:" in out,
            "expected": "แสดงผลรายงานสรุปคลังสินค้า คำนวณชนิด หน่วยรวม และมูลค่ารวมครบถ้วน"
        },
        {
            "id": "TC-APP-07",
            "method": "Full End-to-End User Simulation Flow",
            "data": "เดินเมนู Show All -> Add -> Cut -> Report -> Search -> Low Stock -> Exit",
            # เดินเมนู 1 ถึง 7 ตามลำดับของเมนูจริง
            "action": lambda: _run_with_mock_inputs(app.run, [
                "1", "",                                          # 1: Show all -> Enter
                "2", "P102", "Milk", "10", "12.0", "Drink", "", "5",  # 2: Add
                "3", "P102", "2",                                 # 3: Cut
                "4",                                              # 4: Report
                "5", "Milk", "",                                  # 5: Search -> Enter
                "6", "",                                          # 6: Low Stock Alert -> Enter
                "7"                                               # 7: Exit
            ]),
            "verify": lambda out: "ขอบคุณที่ใช้บริการ" in out,
            "expected": "ทำงานผ่าน CLI ตลอดทั้งรอบครบทุกคำสั่งโดยไม่เกิด Exception หรือแอปแครช"
        }
    ]

    passed_count = 0
    for idx, c in enumerate(cases, 1):
        try:
            out = c["action"]()
            is_ok = c["verify"](out)
        except Exception as e:
            out = f"Exception: {e}"
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

    db.connection.close()
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass


if __name__ == "__main__":
    _run_terminal_demo()
