"""
Unit Test สำหรับ DatabaseConnection (SCRUM-13, ครอบคลุมส่วน SCRUM-6)

หมายเหตุ: ณ ตอนที่เขียนไฟล์นี้ ในโปรเจกต์มีเพียง DatabaseConnection ที่ implement จริง
(Product, Validator, Logger, ProductRepository ยังไม่มีไฟล์ .py ให้ทดสอบ)
จึงเขียนเทสต์เฉพาะคลาสนี้ก่อน โครงไฟล์เทสต์คลาสอื่นเตรียมไว้ให้ต่อท้ายเมื่อโค้ดพร้อม

แนวทางที่ใช้:
- แยก test ตามเมธอด/พฤติกรรมของ DatabaseConnection ทีละฟังก์ชัน (ตามที่ขอ)
- ใช้ pytest fixture รีเซ็ต Singleton (_instance) ก่อนและหลังทุกเทสต์ เพราะ
  DatabaseConnection เป็น Singleton ระดับคลาส ถ้าไม่รีเซ็ต เทสต์แต่ละเคสจะแชร์
  instance/connection กัน ทำให้ผลเทสต์ปนกันและ debug ยาก
- ใช้ tmp_path ของ pytest สร้างไฟล์ .db แยกทุกเทสต์ (ไม่แตะ inventory.db จริง)
  และ copy schema.sql ไปไว้ที่ tmp dir พร้อม chdir เข้าไป เพราะ _init_tables()
  อ่านไฟล์ "schema.sql" แบบ relative path ตายตัว
"""
import sqlite3
import pytest

from database_connection import DatabaseConnection

# fixtures: reset_singletons, isolated_cwd, db มาจาก conftest.py (ใช้ร่วมกับไฟล์เทสต์อื่น)


def _insert_sample_product(conn, product_id="P1", name="Test Item",
                            category="TestCat", quantity=10, price=50.0):
    conn.executeQuery(
        """INSERT INTO products (product_id, name, category, quantity, price)
           VALUES (?, ?, ?, ?, ?)""",
        (product_id, name, category, quantity, price),
    )
    conn.commit()


# ------------------------------------------------------------------
# 1) Singleton pattern
# ------------------------------------------------------------------

def test_get_instance_returns_same_object(db, isolated_cwd):
    """getInstance() เรียกซ้ำต้องได้ instance เดิม ไม่สร้างใหม่"""
    db2 = DatabaseConnection.getInstance("test_inventory.db")
    assert db is db2
    assert db.connection is db2.connection


def test_direct_constructor_raises_when_instance_exists(db):
    """ห้ามสร้าง DatabaseConnection() ตรงๆ ซ้ำ ต้องโยน Exception"""
    with pytest.raises(Exception):
        DatabaseConnection("test_inventory.db")


def test_get_instance_creates_db_file(db, isolated_cwd):
    """getInstance() ต้องสร้างไฟล์ .db จริงบน disk"""
    assert (isolated_cwd / "test_inventory.db").exists()


# ------------------------------------------------------------------
# 2) _init_tables (ทางอ้อม ผ่านผลลัพธ์หลัง getInstance)
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# 3) executeQuery — เขียนข้อมูล (INSERT)
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# 4) executeQuery — อ่านข้อมูล (SELECT) ผ่านหลาย reference (Singleton จริงไหม)
# ------------------------------------------------------------------

def test_execute_query_select_via_second_reference(db, isolated_cwd):
    _insert_sample_product(db)
    db2 = DatabaseConnection.getInstance("test_inventory.db")
    cursor = db2.executeQuery(
        "SELECT name FROM products WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row["name"] == "Test Item"


# ------------------------------------------------------------------
# 5) executeQuery — แก้ไขข้อมูล (UPDATE)
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# 6) executeQuery — ลบข้อมูล (DELETE)
# ------------------------------------------------------------------

def test_execute_query_delete(db):
    _insert_sample_product(db)
    db.executeQuery("DELETE FROM products WHERE product_id = ?", ("P1",))
    db.commit()

    cursor = db.executeQuery(
        "SELECT * FROM products WHERE product_id = ?", ("P1",)
    )
    assert cursor.fetchone() is None


# ------------------------------------------------------------------
# 7) commit()
# ------------------------------------------------------------------

def test_commit_persists_data_across_new_connection(db, isolated_cwd):
    """commit() แล้ว ปิด connection เปิดใหม่ (จำลอง process ใหม่) ข้อมูลต้องยังอยู่"""
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


# ------------------------------------------------------------------
# 8) rollback()
# ------------------------------------------------------------------

def test_rollback_reverts_uncommitted_changes(db):
    _insert_sample_product(db)  # commit แล้ว มีอยู่จริง

    db.executeQuery(
        "UPDATE products SET quantity = ? WHERE product_id = ?", (999, "P1")
    )
    # ยังไม่ commit แล้ว rollback ทันที
    db.rollback()

    cursor = db.executeQuery(
        "SELECT quantity FROM products WHERE product_id = ?", ("P1",)
    )
    assert cursor.fetchone()["quantity"] == 10  # ค่าต้องไม่เปลี่ยนเป็น 999


# ------------------------------------------------------------------
# 9) beginTransaction() — ปัจจุบันเป็น no-op ตาม implementation
# ------------------------------------------------------------------

def test_begin_transaction_does_not_raise(db):
    db.beginTransaction()  # แค่ต้องไม่ error


# ------------------------------------------------------------------
# 10) CHECK constraint ระดับฐานข้อมูล (ชั้นป้องกันเสริมจาก Validator)
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# 11) upsert ผ่าน SQL ที่ ProductRepository จะใช้ (ON CONFLICT DO UPDATE)
#     ทดสอบล่วงหน้าระดับ DB แม้ ProductRepository ยังไม่ implement
# ------------------------------------------------------------------

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
    assert len(rows) == 1  # ต้องไม่มีแถวซ้ำ
    assert rows[0]["name"] == "Updated Name"
    assert rows[0]["quantity"] == 8


# ------------------------------------------------------------------
# 12) stock_movements — ประวัติการเปลี่ยนสต็อก
# ------------------------------------------------------------------

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
    """product_id ที่ไม่มีอยู่จริงใน products ต้อง insert ไม่ผ่าน (FK constraint)"""
    with pytest.raises(sqlite3.IntegrityError):
        db.executeQuery(
            "INSERT INTO stock_movements (product_id, change_qty, reason) VALUES (?, ?, ?)",
            ("NON_EXISTENT_ID", -1, "should fail"),
        )


# ------------------------------------------------------------------
# 13) action_logs — รองรับ Logger.log()
# ------------------------------------------------------------------

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
