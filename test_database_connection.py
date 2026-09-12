"""
Unit Test สำหรับ DatabaseConnection (SCRUM-13, ครอบคลุมส่วน SCRUM-6)
รันด้วย pytest: python -m pytest -v test_database_connection.py
รันแบบ Demo ใน Terminal: python test_database_connection.py
"""
import os
import sqlite3
import pytest

from database_connection import DatabaseConnection


def _insert_sample_product(conn, product_id="P1", name="Test Item",
                            category="TestCat", quantity=10, price=50.0):
    conn.executeQuery(
        """INSERT INTO products (product_id, name, category, quantity, price)
           VALUES (?, ?, ?, ?, ?)""",
        (product_id, name, category, quantity, price),
    )
    conn.commit()


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

# ------------------------------------------------------------
# 1) Singleton pattern
# ------------------------------------------------------------

def test_get_instance_returns_same_object(db, isolated_cwd):
    db2 = DatabaseConnection.getInstance("test_inventory.db")
    assert db is db2
    assert db.connection is db2.connection


def test_direct_constructor_raises_when_instance_exists(db):
    with pytest.raises(Exception):
        DatabaseConnection("test_inventory.db")


def test_get_instance_creates_db_file(db, isolated_cwd):
    assert (isolated_cwd / "test_inventory.db").exists()


# ------------------------------------------------------------
# 2) _init_tables
# ------------------------------------------------------------

def test_init_tables_creates_products_table(db):
    cursor = db.executeQuery(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
    )
    assert cursor.fetchone() is not None


def test_init_tables_creates_stock_movements_table(db):
    cursor = db.executeQuery(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='stock_movements'"
    )
    assert cursor.fetchone() is not None


def test_init_tables_creates_action_logs_table(db):
    cursor = db.executeQuery(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='action_logs'"
    )
    assert cursor.fetchone() is not None


# ------------------------------------------------------------
# 3) executeQuery — เขียนข้อมูล (INSERT)
# ------------------------------------------------------------

def test_execute_query_insert(db):
    _insert_sample_product(db)
    cursor = db.executeQuery(
        "SELECT * FROM products WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["name"] == "Test Item"
    assert row["quantity"] == 10
    assert row["price"] == 50.0


# ------------------------------------------------------------
# 4) executeQuery — อ่านข้อมูล (SELECT) ผ่านหลาย reference
# ------------------------------------------------------------

def test_execute_query_select_via_second_reference(db, isolated_cwd):
    _insert_sample_product(db)
    db2 = DatabaseConnection.getInstance("test_inventory.db")
    cursor = db2.executeQuery(
        "SELECT name FROM products WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row["name"] == "Test Item"


# ------------------------------------------------------------
# 5) executeQuery — แก้ไขข้อมูล (UPDATE)
# ------------------------------------------------------------

def test_execute_query_update(db):
    _insert_sample_product(db, quantity=10)
    db.executeQuery(
        "UPDATE products SET quantity = ? WHERE product_id = ?", (25, "P1")
    )
    db.commit()

    cursor = db.executeQuery(
        "SELECT quantity FROM products WHERE product_id = ?", ("P1",)
    )
    assert cursor.fetchone()["quantity"] == 25


# ------------------------------------------------------------
# 6) executeQuery — ลบข้อมูล (DELETE)
# ------------------------------------------------------------

def test_execute_query_delete(db):
    _insert_sample_product(db)
    db.executeQuery("DELETE FROM products WHERE product_id = ?", ("P1",))
    db.commit()

    cursor = db.executeQuery(
        "SELECT * FROM products WHERE product_id = ?", ("P1",)
    )
    assert cursor.fetchone() is None


# ------------------------------------------------------------
# 7) commit()
# ------------------------------------------------------------

def test_commit_persists_data_across_new_connection(db, isolated_cwd):
    _insert_sample_product(db)
    db.connection.close()

    raw_conn = sqlite3.connect(str(isolated_cwd / "test_inventory.db"))
    raw_conn.row_factory = sqlite3.Row
    row = raw_conn.execute(
        "SELECT * FROM products WHERE product_id = ?", ("P1",)
    ).fetchone()
    raw_conn.close()

    assert row is not None
    assert row["name"] == "Test Item"


# ------------------------------------------------------------
# 8) rollback()
# ------------------------------------------------------------

def test_rollback_reverts_uncommitted_changes(db):
    _insert_sample_product(db)

    db.executeQuery(
        "UPDATE products SET quantity = ? WHERE product_id = ?", (999, "P1")
    )
    db.rollback()

    cursor = db.executeQuery(
        "SELECT quantity FROM products WHERE product_id = ?", ("P1",)
    )
    assert cursor.fetchone()["quantity"] == 10


# ------------------------------------------------------------
# 9) beginTransaction()
# ------------------------------------------------------------

def test_begin_transaction_does_not_raise(db):
    db.beginTransaction()


# ------------------------------------------------------------
# 10) CHECK constraint ระดับฐานข้อมูล
# ------------------------------------------------------------

def test_insert_negative_quantity_violates_check_constraint(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.executeQuery(
            """INSERT INTO products (product_id, name, category, quantity, price)
               VALUES (?, ?, ?, ?, ?)""",
            ("P2", "Bad Item", "Food", -5, 10.0),
        )


def test_insert_negative_price_violates_check_constraint(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.executeQuery(
            """INSERT INTO products (product_id, name, category, quantity, price)
               VALUES (?, ?, ?, ?, ?)""",
            ("P3", "Bad Item", "Food", 5, -10.0),
        )


# ------------------------------------------------------------
# 11) upsert ผ่าน SQL (ON CONFLICT DO UPDATE)
# ------------------------------------------------------------

def test_upsert_same_id_updates_instead_of_duplicating(db):
    upsert_sql = """
        INSERT INTO products (product_id, name, category, quantity, price)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(product_id) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            quantity = excluded.quantity,
            price = excluded.price
    """
    db.executeQuery(upsert_sql, ("P1", "First Name", "Food", 5, 20.0))
    db.commit()
    db.executeQuery(upsert_sql, ("P1", "Updated Name", "Drink", 8, 25.0))
    db.commit()

    cursor = db.executeQuery("SELECT * FROM products WHERE product_id = ?", ("P1",))
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["name"] == "Updated Name"
    assert rows[0]["quantity"] == 8


# ------------------------------------------------------------
# 12) stock_movements — ประวัติการเปลี่ยนสต็อก & Foreign Key
# ------------------------------------------------------------

def test_stock_movement_insert_linked_to_product(db):
    _insert_sample_product(db, quantity=10)
    db.executeQuery(
        "INSERT INTO stock_movements (product_id, change_qty, reason) VALUES (?, ?, ?)",
        ("P1", -3, "cut stock test"),
    )
    db.commit()

    cursor = db.executeQuery(
        "SELECT * FROM stock_movements WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["change_qty"] == -3


def test_stock_movement_foreign_key_enforced(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.executeQuery(
            "INSERT INTO stock_movements (product_id, change_qty, reason) VALUES (?, ?, ?)",
            ("NON_EXISTENT_ID", -1, "should fail"),
        )


# ------------------------------------------------------------
# 13) action_logs
# ------------------------------------------------------------

def test_action_log_insert(db):
    db.executeQuery(
        "INSERT INTO action_logs (action, detail) VALUES (?, ?)",
        ("TEST_ACTION", "unit test detail"),
    )
    db.commit()

    cursor = db.executeQuery(
        "SELECT * FROM action_logs WHERE action = ?", ("TEST_ACTION",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["detail"] == "unit test detail"


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_database_connection.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 🗄️   DATABASE CONNECTION DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    test_db_name = "test_db_terminal.db"
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass

    DatabaseConnection._instance = None
    db = DatabaseConnection.getInstance(test_db_name)

    cases = [
        {
            "id": "TC-DBC-01",
            "method": "Singleton Connection Reference Integrity",
            "data": "db1 = getInstance(), db2 = getInstance()",
            "action": lambda: (db, DatabaseConnection.getInstance(test_db_name)),
            "verify": lambda res: res[0] is res[1] and res[0].connection is res[1].connection,
            "expected": "ได้ Instance และ SQLite Connection เดียวกันจริง ไม่เปิด Connection ซ้ำซ้อน"
        },
        {
            "id": "TC-DBC-02",
            "method": "Constructor Guarding Exception Assertion",
            "data": "เรียก DatabaseConnection('test.db') ตรงๆ",
            "action": lambda: _check_constructor_guard(test_db_name),
            "verify": lambda res: res is True,
            "expected": "ห้ามสร้าง Object ตรงๆ โยน Exception บังคับใช้ getInstance() เท่านั้น"
        },
        {
            "id": "TC-DBC-03",
            "method": "Automated Schema Bootstrap Verification",
            "data": "ตรวจสอบตาราง products, stock_movements, action_logs",
            "action": lambda: [r["name"] for r in db.executeQuery("SELECT name FROM sqlite_master WHERE type='table'").fetchall()],
            "verify": lambda res: all(t in res for t in ["products", "stock_movements", "action_logs"]),
            "expected": "อ่านและประมวลผล schema.sql สร้างตารางครบถ้วนทั้ง 3 ตารางอัตโนมัติ"
        },
        {
            "id": "TC-DBC-04",
            "method": "CRUD: Create & Parameterized Write (INSERT)",
            "data": "INSERT สินค้า 'P101', Qty=20, Price=15.0",
            "action": lambda: _test_insert(db),
            "verify": lambda res: res is not None and res["quantity"] == 20,
            "expected": "บันทึกข้อมูลสินค้าใหม่ผ่านคำสั่ง executeQuery() สำเร็จ ปลอดภัยจาก SQL Injection"
        },
        {
            "id": "TC-DBC-05",
            "method": "CRUD: Update & State Modification (UPDATE)",
            "data": "UPDATE สินค้า 'P101' ปรับจำนวนเป็น 35",
            "action": lambda: _test_update(db),
            "verify": lambda res: res is not None and res["quantity"] == 35,
            "expected": "แก้ไขข้อมูลสินค้าสำเร็จ ยอดคงเหลืออัปเดตตรงตามที่ระบุ"
        },
        {
            "id": "TC-DBC-06",
            "method": "Transaction Rollback Fault Tolerance",
            "data": "UPDATE 'P101' Qty=999 แล้วสั่ง rollback() ทันทีโดยไม่ commit",
            "action": lambda: _test_rollback(db),
            "verify": lambda res: res["quantity"] == 35,
            "expected": "ยกเลิกคำสั่งสำเร็จ ข้อมูลถอยกลับสู่สถานะก่อนหน้า (Qty=35 ไม่กลายเป็น 999)"
        },
        {
            "id": "TC-DBC-07",
            "method": "Database-level Negative Quantity Check Constraint",
            "data": "INSERT สินค้า Qty=-5 (CHECK constraint)",
            "action": lambda: _check_integrity_error(lambda: db.executeQuery(
                "INSERT INTO products (product_id, name, quantity, price) VALUES ('P99', 'Bad', -5, 10.0)"
            )),
            "verify": lambda res: res is True,
            "expected": "ฐานข้อมูลปฏิเสธคำสั่งทันที (sqlite3.IntegrityError) ห้ามสต็อกติดลบเด็ดขาด"
        },
        {
            "id": "TC-DBC-08",
            "method": "Foreign Key Relational Constraint Enforcement",
            "data": "INSERT stock_movements ให้ product_id ที่ไม่มีใน products",
            "action": lambda: _check_integrity_error(lambda: db.executeQuery(
                "INSERT INTO stock_movements (product_id, change_qty, reason) VALUES ('NO_ID', -1, 'fail')"
            )),
            "verify": lambda res: res is True,
            "expected": "ฐานข้อมูลปฏิเสธคำสั่ง (PRAGMA foreign_keys = ON ป้องกันข้อมูลกำพร้า)"
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


def _check_constructor_guard(db_name):
    try:
        DatabaseConnection(db_name)
        return False
    except Exception:
        return True


def _test_insert(db):
    db.executeQuery(
        "INSERT INTO products (product_id, name, quantity, price, category) VALUES (?, ?, ?, ?, ?)",
        ("P101", "Coffee", 20, 15.0, "Drink")
    )
    db.commit()
    return db.executeQuery("SELECT * FROM products WHERE product_id = 'P101'").fetchone()


def _test_update(db):
    db.executeQuery("UPDATE products SET quantity = ? WHERE product_id = ?", (35, "P101"))
    db.commit()
    return db.executeQuery("SELECT * FROM products WHERE product_id = 'P101'").fetchone()


def _test_rollback(db):
    db.executeQuery("UPDATE products SET quantity = ? WHERE product_id = ?", (999, "P101"))
    db.rollback()
    return db.executeQuery("SELECT * FROM products WHERE product_id = 'P101'").fetchone()


def _check_integrity_error(fn):
    try:
        fn()
        return False
    except sqlite3.IntegrityError:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    _run_terminal_demo()