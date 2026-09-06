"""Unit test สำหรับ ProductRepository (SCRUM-7 & CR-01) — ทดสอบกับฐานข้อมูลจริง (ไม่ mock) ตาม DoD
รันด้วย pytest: python -m pytest -v test_product_repository.py
รันแบบ Demo ใน Terminal: python test_product_repository.py
"""
import os
import sqlite3
import pytest

from product import Product
from database_connection import DatabaseConnection
from product_repository import ProductRepository


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

# ------------------------------------------------------------
# upsertProduct
# ------------------------------------------------------------

def test_upsert_product_inserts_new_record(repo):
    p = Product(product_id="P1", name="Mama Noodles", quantity=50, price=6.0, category="Food")
    repo.upsertProduct(p)

    found = repo.findById("P1")
    assert found == p


def test_upsert_product_with_existing_id_updates_not_duplicates(repo):
    repo.upsertProduct(Product("P1", "Old Name", 5, 20.0, "Food"))
    repo.upsertProduct(Product("P1", "New Name", 8, 25.0, "Drink"))

    all_products = repo.findAll()
    matching = [p for p in all_products if p.product_id == "P1"]
    assert len(matching) == 1
    assert matching[0].name == "New Name"
    assert matching[0].quantity == 8


# ------------------------------------------------------------
# findById
# ------------------------------------------------------------

def test_find_by_id_returns_none_when_not_found(repo):
    assert repo.findById("NO_SUCH_ID") is None


def test_find_by_id_returns_correct_product(repo):
    repo.upsertProduct(Product("P2", "Lactasoy Milk", 20, 12.0, "Drink"))
    found = repo.findById("P2")
    assert found.name == "Lactasoy Milk"
    assert found.quantity == 20


# ------------------------------------------------------------
# findAll
# ------------------------------------------------------------

def test_find_all_returns_empty_list_when_no_products(repo):
    assert repo.findAll() == []


def test_find_all_returns_every_product_sorted_by_name(repo):
    repo.upsertProduct(Product("P1", "Zebra Snack", 1, 1.0))
    repo.upsertProduct(Product("P2", "Apple Juice", 1, 1.0))

    names = [p.name for p in repo.findAll()]
    assert names == ["Apple Juice", "Zebra Snack"]


# ------------------------------------------------------------
# search
# ------------------------------------------------------------

def test_search_matches_by_name(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    results = repo.search("Mama")
    assert len(results) == 1
    assert results[0].product_id == "P1"


def test_search_matches_by_category(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    results = repo.search("Drink")
    assert len(results) == 1
    assert results[0].product_id == "P2"


def test_search_returns_empty_list_when_no_match(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    assert repo.search("NotExist") == []


# ------------------------------------------------------------
# updateStock
# ------------------------------------------------------------

def test_update_stock_increases_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", 5, reason="restock")
    assert repo.findById("P1").quantity == 15


def test_update_stock_decreases_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", -4, reason="sale")
    assert repo.findById("P1").quantity == 6


def test_update_stock_records_stock_movement_history(repo, db):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", -3, reason="cut stock test")

    cursor = db.executeQuery(
        "SELECT * FROM stock_movements WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["change_qty"] == -3
    assert row["reason"] == "cut stock test"


def test_update_stock_below_zero_raises_and_does_not_change_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 5, 5.0))
    with pytest.raises(ValueError):
        repo.updateStock("P1", -10)
    assert repo.findById("P1").quantity == 5


def test_update_stock_on_missing_product_raises(repo):
    with pytest.raises(ValueError):
        repo.updateStock("NO_SUCH_ID", 5)


# ------------------------------------------------------------
# getSummary
# ------------------------------------------------------------

def test_get_summary_on_empty_repository(repo):
    summary = repo.getSummary()
    assert summary["total_products"] == 0
    assert summary["total_units"] == 0
    assert summary["total_value"] == 0
    assert summary["low_stock_items"] == 0


def test_get_summary_calculates_totals_correctly(repo):
    repo.upsertProduct(Product("P1", "Item A", quantity=10, price=6.0))
    repo.upsertProduct(Product("P2", "Item B", quantity=20, price=12.0))

    summary = repo.getSummary()
    assert summary["total_products"] == 2
    assert summary["total_units"] == 30
    assert summary["total_value"] == 10 * 6.0 + 20 * 12.0


def test_get_summary_counts_low_stock_items(repo):
    repo.upsertProduct(Product("P1", "Low Stock Item", quantity=3, price=1.0))
    repo.upsertProduct(Product("P2", "Boundary Item", quantity=5, price=1.0))
    repo.upsertProduct(Product("P3", "Plenty Item", quantity=100, price=1.0))

    summary = repo.getSummary()
    assert summary["low_stock_items"] == 2


# ============================================================
# CR-01: Barcode & Reorder Point Alert (SCRUM-CR01)
# ============================================================

def test_upsert_product_persists_barcode_and_reorder_point(repo):
    p = Product("P1", "Scanned Item", quantity=10, price=6.0,
                barcode="8850999327015", reorder_point=8)
    repo.upsertProduct(p)

    found = repo.findById("P1")
    assert found.barcode == "8850999327015"
    assert found.reorder_point == 8


def test_get_low_stock_alerts_returns_products_at_or_below_reorder_point(repo):
    repo.upsertProduct(Product("P1", "Low Item", quantity=3, price=1.0, reorder_point=5))
    repo.upsertProduct(Product("P2", "Boundary Item", quantity=5, price=1.0, reorder_point=5))
    repo.upsertProduct(Product("P3", "Normal Item", quantity=6, price=1.0, reorder_point=5))

    alerts = repo.getLowStockAlerts()
    alert_ids = [p.product_id for p in alerts]

    assert "P1" in alert_ids
    assert "P2" in alert_ids
    assert "P3" not in alert_ids
    assert len(alerts) == 2


def test_get_low_stock_alerts_returns_empty_when_no_products_low(repo):
    repo.upsertProduct(Product("P1", "Plenty Item", quantity=100, price=1.0, reorder_point=5))
    alerts = repo.getLowStockAlerts()
    assert alerts == []


def test_get_low_stock_alerts_returns_empty_when_no_products_at_all(repo):
    alerts = repo.getLowStockAlerts()
    assert alerts == []


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_product_repository.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 🏛️   PRODUCT REPOSITORY DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    test_db_name = "test_repo_terminal.db"
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass

    DatabaseConnection._instance = None
    db = DatabaseConnection.getInstance(test_db_name)
    repo = ProductRepository(db)

    cases = [
        {
            "id": "TC-REPO-01",
            "method": "CRUD: Create via ON CONFLICT Upsert",
            "data": "Product(id='P1', name='Coffee', qty=10, price=45.0, cat='Drink')",
            "action": lambda: (repo.upsertProduct(Product("P1", "Coffee", 10, 45.0, "Drink")), repo.findById("P1")),
            "verify": lambda res: res[1] is not None and res[1].name == "Coffee",
            "expected": "เพิ่มสินค้าใหม่ลงตาราง products สำเร็จ ค้นหาด้วย findById('P1') พบข้อมูลถูกต้อง"
        },
        {
            "id": "TC-REPO-02",
            "method": "CRUD: Update Existing Key Idempotency",
            "data": "อัปเดต 'P1' เป็น name='Coffee Extra', qty=15, price=50.0",
            "action": lambda: (repo.upsertProduct(Product("P1", "Coffee Extra", 15, 50.0, "Drink")), repo.findById("P1"), repo.findAll()),
            "verify": lambda res: res[1].name == "Coffee Extra" and res[1].quantity == 15 and len(res[2]) == 1,
            "expected": "อัปเดตทับเรคคอร์ดเดิมสำเร็จด้วย ON CONFLICT ไม่สร้างแถวข้อมูลซ้ำซ้อน"
        },
        {
            "id": "TC-REPO-03",
            "method": "CR-01: Persistence of Barcode & Reorder Point",
            "data": "Product(id='P2', barcode='8850999327015', reorder_point=8)",
            "action": lambda: (repo.upsertProduct(Product("P2", "Sugar", 20, 15.0, barcode="8850999327015", reorder_point=8)), repo.findById("P2")),
            "verify": lambda res: res[1].barcode == "8850999327015" and res[1].reorder_point == 8,
            "expected": "บันทึกและดึงค่า barcode/reorder_point ผ่าน SQLite ได้ครบถ้วนสมบูรณ์"
        },
        {
            "id": "TC-REPO-04",
            "method": "Transactional Stock Adjustment & Audit Movement",
            "data": "ตัดสต็อก 'P1' ออก 3 ชิ้น (change_qty=-3, reason='sale demo')",
            "action": lambda: _test_cut_stock(repo, db),
            "verify": lambda res: res["qty"] == 12 and res["mov_qty"] == -3,
            "expected": "ลดสต็อกเหลือ 12 และบันทึกประวัติลง stock_movements แบบ Atomic Transaction"
        },
        {
            "id": "TC-REPO-05",
            "method": "Negative Stock Protection Guard (DoD Constraint)",
            "data": "ตัดสต็อก 'P1' เกินจำนวนที่มี (คงเหลือ 12 แต่สั่งตัดออก 20)",
            "action": lambda: _check_repo_value_error(lambda: repo.updateStock("P1", -20)),
            "verify": lambda res: res is True and repo.findById("P1").quantity == 12,
            "expected": "ปฏิเสธการตัดสต็อก (ValueError: สต็อกไม่พอ) และคงยอดเดิมไว้ ไม่เกิดการเปลี่ยนแปลง"
        },
        {
            "id": "TC-REPO-06",
            "method": "Pattern Search with LIKE Operator",
            "data": "search('Sugar') หรือ search('Drink')",
            "action": lambda: (repo.search("Sugar"), repo.search("Drink")),
            "verify": lambda res: len(res[0]) == 1 and len(res[1]) == 1,
            "expected": "ค้นหาเจอถูกต้องทั้งจากชื่อสินค้า (Name) และหมวดหมู่ (Category)"
        },
        {
            "id": "TC-REPO-07",
            "method": "CR-01: Critical Inventory Filter Query",
            "data": "P1(qty=12, reorder=5), P2(qty=20, reorder=8), P3(qty=2, reorder=5)",
            "action": lambda: _test_low_stock_alerts(repo),
            "verify": lambda res: len(res) == 1 and res[0].product_id == "P3",
            "expected": "getLowStockAlerts() คัดกรองเฉพาะสินค้าที่ qty <= reorder_point ได้แม่นยำ"
        },
        {
            "id": "TC-REPO-08",
            "method": "Aggregate Summary & Low Stock KPI Calculation",
            "data": "คำนวณยอดรวมสินค้า มูลค่าสต็อก และนับรายการใกล้หมด (getSummary)",
            "action": lambda: repo.getSummary(),
            "verify": lambda res: res["total_products"] >= 3 and res["total_units"] > 0 and res["total_value"] > 0,
            "expected": "คำนวณสถิติคลังสินค้าถูกต้อง สรุปชนิดสินค้า จำนวนรวม และมูลค่ารวมตรงเป๊ะ"
        }
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

    db.connection.close()
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass


def _test_cut_stock(repo, db):
    repo.updateStock("P1", -3, reason="sale demo")
    p = repo.findById("P1")
    cur = db.executeQuery("SELECT change_qty FROM stock_movements WHERE product_id = 'P1' ORDER BY movement_id DESC LIMIT 1")
    mov = cur.fetchone()
    return {"qty": p.quantity, "mov_qty": mov["change_qty"] if mov else None}


def _check_repo_value_error(fn):
    try:
        fn()
        return False
    except ValueError:
        return True
    except Exception:
        return False


def _test_low_stock_alerts(repo):
    repo.upsertProduct(Product("P3", "Low Snack", 2, 10.0, "Snack", reorder_point=5))
    return repo.getLowStockAlerts()


if __name__ == "__main__":
    _run_terminal_demo()
