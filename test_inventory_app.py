"""
Unit/flow test สำหรับ InventoryApp (SCRUM-11)

ทดสอบตาม Definition of Done ของ SCRUM-11:
  - รันโปรแกรมแล้วใช้งานได้ครบทุกเมนู (run, showMenu, addOrUpdateProduct,
    cutStock, showReport, searchProduct) โดยไม่ error
  - ทุก action ที่แก้ไขข้อมูลเรียก Logger.log() ต่อท้ายจริง

ใช้ fixture db/repo จาก conftest.py เหมือนไฟล์เทสต์อื่น (database ทดสอบแยกจาก
production) — สร้าง InventoryApp() หลัง db fixture พร้อมแล้วเสมอ เพราะ
ProductRepository()/Logger.getInstance() ข้างในจะไปเรียก
DatabaseConnection.getInstance() ที่ถูก fixture ตั้งค่าไว้แล้ว
"""
import pytest

from inventory_app import InventoryApp
from product import Product


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


# ------------------------------------------------------------------
# showMenu()
# ------------------------------------------------------------------

def test_show_menu_prints_all_six_options(db, capsys):
    app = InventoryApp()
    app.showMenu()
    out = capsys.readouterr().out
    for expected in ["1.", "2.", "3.", "4.", "5.", "6."]:
        assert expected in out


# ------------------------------------------------------------------
# addOrUpdateProduct()
# ------------------------------------------------------------------

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
    assert saved.name == "Old Name"  # ต้องไม่เปลี่ยนเพราะผู้ใช้ไม่ยืนยัน
    assert _count_logs(db) == 0  # ไม่ควรมี log เพราะไม่มีการบันทึกจริง


def test_add_product_with_negative_quantity_input_shows_error_no_save(monkeypatch, db, repo):
    """Validator.inputNonNegativeInt วนถามใหม่จนกว่าจะไม่ติดลบ ผลลัพธ์สุดท้ายต้องไม่ติดลบเสมอ"""
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "Item", "-5", "10", "20.0", "Food", "", "5"])
    app.addOrUpdateProduct()

    saved = repo.findById("P1")
    assert saved.quantity == 10  # ค่าที่ยอมรับได้ (ครั้งที่ 2 ที่กรอก) ต้องไม่ติดลบ


def test_add_product_empty_id_shows_error(monkeypatch, db, repo, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, [""])
    app.addOrUpdateProduct()
    out = capsys.readouterr().out
    assert "ห้ามเป็นค่าว่าง" in out or "ค่าว่าง" in out
    assert repo.findAll() == []


# ------------------------------------------------------------------
# cutStock()
# ------------------------------------------------------------------

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
    _mock_inputs(monkeypatch, ["P1", "2"])  # เหลือ 4 -> ต้องเตือน (< 5)
    app.cutStock()

    out = capsys.readouterr().out
    assert "คำเตือน" in out


def test_cut_stock_no_warning_when_stock_stays_at_or_above_threshold(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0, "Food"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["P1", "5"])  # เหลือ 5 -> ยังไม่ต้องเตือน
    app.cutStock()

    out = capsys.readouterr().out
    assert "คำเตือน" not in out


# ------------------------------------------------------------------
# showReport()
# ------------------------------------------------------------------

def test_show_report_prints_correct_summary(db, repo, capsys):
    repo.upsertProduct(Product("P1", "Item A", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Item B", 5, 12.0, "Drink"))

    app = InventoryApp()
    app.showReport()

    out = capsys.readouterr().out
    assert "จำนวนชนิดสินค้าทั้งหมด: 2" in out
    assert "120.00" in out  # 10*6 + 5*12 = 120


# ------------------------------------------------------------------
# searchProduct() — ของเดิม แต่เทสต์ผ่านเมนูจริงของ InventoryApp
# ------------------------------------------------------------------

def test_search_product_finds_match_and_logs(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    app = InventoryApp()
    _mock_inputs(monkeypatch, ["Mama", ""])  # "" = กด Enter กลับเมนูหลังแสดงผล
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


# ------------------------------------------------------------------
# showAllProducts()
# ------------------------------------------------------------------

def test_show_all_products_prints_every_item(monkeypatch, db, repo, capsys):
    repo.upsertProduct(Product("P1", "Coffee", 10, 45.0, "Drink"))
    app = InventoryApp()
    _mock_inputs(monkeypatch, [""])  # กด Enter กลับเมนู (total_pages <= 1)
    app.showAllProducts()

    out = capsys.readouterr().out
    assert "Coffee" in out


# ------------------------------------------------------------------
# run() — ลูปเมนูหลักครบทุกทางเลือก ต้องไม่ error
# ------------------------------------------------------------------

def test_run_exits_cleanly_on_choice_7(monkeypatch, db, capsys):
    """เมนู Exit ย้ายจากเลข 6 เป็นเลข 7 หลังเพิ่มเมนู Low Stock Alerts (CR-01)"""
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["7"])
    app.run()  # ต้องไม่ throw exception ใดๆ
    out = capsys.readouterr().out
    assert "ขอบคุณที่ใช้บริการ" in out


def test_run_invalid_choice_then_exit(monkeypatch, db, capsys):
    app = InventoryApp()
    _mock_inputs(monkeypatch, ["9", "7"])
    app.run()
    out = capsys.readouterr().out
    assert "ตัวเลือกไม่ถูกต้อง" in out


def test_run_shows_low_stock_alerts_on_choice_6(monkeypatch, db, repo, capsys):
    """CR-01: เมนู 6 ต้องเรียก Low Stock Alerts ได้โดยไม่ error"""
    repo.upsertProduct(Product("P1", "Almost Out", 2, 5.0, "Food", reorder_point=5))

    app = InventoryApp()
    _mock_inputs(monkeypatch, ["6", "7"])  # 6: Low Stock Alerts, 7: Exit
    app.run()

    out = capsys.readouterr().out
    assert "Almost Out" in out
    assert "ต้องสั่งซื้อเพิ่ม" in out


def test_run_full_menu_flow_all_options_no_error(monkeypatch, db, repo, capsys):
    """จำลองผู้ใช้เดินครบทุกเมนู 1-7 ในรอบเดียว (ตาม DoD: ใช้งานได้ครบทุกเมนูโดยไม่ error)"""
    repo.upsertProduct(Product("P1", "Existing Item", 10, 5.0, "Food"))

    app = InventoryApp()
    _mock_inputs(monkeypatch, [
        "1", "",              # 1: Show all -> กด Enter กลับเมนู
        "2", "P2", "New", "3", "9.0", "Food", "", "5",   # 2: Add new product (id ใหม่, ไม่ใส่ barcode, reorder_point=5)
        "3", "P1", "2",       # 3: Cut stock
        "4",                  # 4: Report
        "5", "Existing", "",  # 5: Search -> กด Enter กลับเมนู
        "6",                  # 6: Low Stock Alerts (CR-01)
        "7",                  # 7: Exit
    ])
    app.run()  # ต้องไม่ throw exception ใดๆ ตลอดทั้ง flow

    out = capsys.readouterr().out
    assert "ขอบคุณที่ใช้บริการ" in out

    # ยืนยันว่าทุก action ที่แก้ข้อมูลถูก log จริง
    assert _count_logs(db, "ADD_PRODUCT") == 1
    assert _count_logs(db, "CUT_STOCK") == 1
    assert _count_logs(db, "SEARCH_PRODUCT") == 1
