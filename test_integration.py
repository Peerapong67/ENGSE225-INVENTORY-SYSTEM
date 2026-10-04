"""Full Integration Test สำหรับ Inventory System

ต่างจาก unit test รายคลาส: ทุกเคสในไฟล์นี้ขับโปรแกรมผ่านเมนูหลัก InventoryApp.run()
หรือ entry point จริง แล้วให้ทุกชั้นทำงานร่วมกันจริงทั้งหมด ไม่ mock คลาสใดเลย
    InventoryApp -> Validator -> Product -> ProductRepository -> DatabaseConnection
    -> SQLite (ไฟล์ .db จริง + schema.sql) / Logger -> action_logs
    / CsvReportExporter -> AtomicFileWriter -> ไฟล์ .csv จริง
สิ่งเดียวที่จำลองคือการพิมพ์ของผู้ใช้ (input) เท่านั้น

รันด้วย pytest: python -m pytest -v test_integration.py
"""
import csv
import os
import runpy
import sqlite3
import sys

import pytest

from database_connection import DatabaseConnection
from inventory_app import InventoryApp
from logger import Logger
from product import Product
from product_repository import ProductRepository

HERE = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# Helpers / Fixtures
# ============================================================

def _script_inputs(monkeypatch, values):
    """จำลองผู้ใช้พิมพ์ตามลำดับใน values ถ้าโปรแกรมขอ input เกินสคริปต์ให้เทสต์ fail
    ทันที (ไม่วนค้าง และจับได้ว่าโปรแกรมถามคำถามเกินที่คาดไว้)"""
    it = iter(values)

    def fake_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(f"สคริปต์ input หมดแล้ว แต่โปรแกรมยังถาม: {prompt!r}")

    monkeypatch.setattr("builtins.input", fake_input)
    return it


def _run_menu(monkeypatch, capsys, values):
    """เปิดโปรแกรมผ่านเมนูหลัก run() ป้อน input ตามสคริปต์ คืนค่า output ทั้งหมดบนจอ
    และตรวจว่าโปรแกรมใช้ input ครบทุกตัวพอดี"""
    it = _script_inputs(monkeypatch, values)
    InventoryApp().run()
    assert next(it, None) is None, "โปรแกรมออกก่อนใช้ input ในสคริปต์ครบ"
    return capsys.readouterr().out


def _add(product_id, name, qty, price, category="", barcode="", reorder="5"):
    """ลำดับ input ของเมนู 2 (เพิ่มสินค้าใหม่)"""
    return ["2", product_id, name, str(qty), str(price), category, barcode, str(reorder)]


def _actions(db):
    rows = db.executeQuery("SELECT action FROM action_logs ORDER BY log_id").fetchall()
    return [r["action"] for r in rows]


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


@pytest.fixture
def db_path(isolated_cwd):
    return str(isolated_cwd / "integration.db")


@pytest.fixture
def live_db(db_path):
    """DatabaseConnection จริงที่ชี้ไปยังไฟล์ .db บนดิสก์ (สร้างตารางจาก schema.sql จริง)"""
    return DatabaseConnection.getInstance(db_path)


# ============================================================
# IT-01: เส้นทางการใช้งานหลักครบทุกเมนู (Happy Path End-to-End)
# ============================================================

def test_it01_full_user_journey_through_main_menu(monkeypatch, capsys, live_db, isolated_cwd):
    out = _run_menu(monkeypatch, capsys, [
        *_add("P001", "ชาเขียว", 20, 25.0, "Drink", "8850001", 5),
        *_add("P002", "บะหมี่กึ่งสำเร็จรูป", 6, 7.5, "Food", "8850002", 5),
        *_add("P003", "น้ำปลา", 3, 30.0, "", "", 4),   # หมวดหมู่ว่าง -> Uncategorized
        "1", "",                                     # แสดงทั้งหมด (หน้าเดียว) แล้วกด Enter
        "3", "P002", "2",                            # ตัดสต็อก 6 -> 4 (<= จุดสั่งซื้อ 5)
        "4",                                         # รายงานสรุป
        "5", "Drink", "",                            # ค้นหาด้วยหมวดหมู่
        "6",                                         # แจ้งเตือนสินค้าใกล้หมด
        "7", "",                                     # Export CSV ชื่อไฟล์ default
        "9",                                         # เลือกเมนูผิด
        "8",                                         # ออกจากโปรแกรม
    ])

    # หน้าจอแสดงผลถูกต้องทุกขั้น
    assert out.count("บันทึกสำเร็จ") == 3
    assert "หน้า 1/1" in out
    assert "ตัดสต็อกสำเร็จ" in out
    assert "!!! คำเตือน: สินค้า 'บะหมี่กึ่งสำเร็จรูป' เหลือสต็อกต่ำ (4 ชิ้น, จุดสั่งซื้อ 5) !!!" in out
    assert "จำนวนชนิดสินค้าทั้งหมด: 3" in out
    assert "จำนวนหน่วยสินค้ารวม: 27" in out
    assert "มูลค่าสินค้ารวม: 620.00 บาท" in out
    assert "จำนวนสินค้าใกล้หมด (<= 5): 2" in out
    assert "ผลการค้นหา 'Drink'" in out
    assert "รวม 2 รายการที่ต้องสั่งซื้อเพิ่ม" in out
    assert "Export สำเร็จ: 2 รายการ ถูกบันทึกไปยังไฟล์ 'low_stock_report.csv'" in out
    assert ">> ตัวเลือกไม่ถูกต้อง กรุณาเลือก 1-8" in out
    assert out.rstrip().endswith("ขอบคุณที่ใช้บริการ")

    # ข้อมูลในฐานข้อมูลจริงถูกต้อง
    repo = ProductRepository(live_db)
    # findAll() เรียงตามชื่อ (ช < น < บ ตามลำดับ Unicode ของ SQLite)
    assert [p.product_id for p in repo.findAll()] == ["P001", "P003", "P002"]
    assert repo.findById("P002").quantity == 4
    assert repo.findById("P003").category == "Uncategorized"
    movements = live_db.executeQuery(
        "SELECT product_id, change_qty, reason FROM stock_movements").fetchall()
    assert [tuple(m) for m in movements] == [("P002", -2, "cutStock")]

    # Audit trail ครบตามลำดับการใช้งาน
    assert _actions(live_db) == [
        "ADD_PRODUCT", "ADD_PRODUCT", "ADD_PRODUCT", "CUT_STOCK", "SEARCH_PRODUCT",
        "LOW_STOCK_ALERT_VIEWED", "EXPORT_LOW_STOCK_CSV",
    ]

    # ไฟล์ CSV ถูกสร้างจริง มีเฉพาะสินค้าใกล้หมด ภาษาไทยไม่เพี้ยน
    assert _read_csv(isolated_cwd / "low_stock_report.csv") == [
        ["ProductID", "ProductName", "Barcode", "Quantity", "ReorderPoint", "Price"],
        ["P003", "น้ำปลา", "", "3", "4", "30.0"],
        ["P002", "บะหมี่กึ่งสำเร็จรูป", "8850002", "4", "5", "7.5"],
    ]


# ============================================================
# IT-02: แก้ไขสินค้าเดิม (Upsert) ทั้งกรณียืนยันและยกเลิก
# ============================================================

def test_it02_update_existing_product_confirm_and_decline(monkeypatch, capsys, live_db):
    out = _run_menu(monkeypatch, capsys, [
        *_add("P001", "Green Tea", 20, 25.0, "Drink", "8850001", 5),
        *_add("P001", "Green Tea Premium", 30, 35.0, "Drink", "8850001", 8), "y",
        *_add("P001", "Should Not Save", 1, 1.0, "Drink", "", 5), "n",
        "8",
    ])

    assert "ข้อมูลเดิม:" in out and "ข้อมูลใหม่:" in out
    assert "ยกเลิกการบันทึก" in out

    rows = live_db.executeQuery("SELECT * FROM products").fetchall()
    assert len(rows) == 1  # upsert ไม่สร้างแถวซ้ำ
    saved = Product.from_row(rows[0])
    assert (saved.name, saved.quantity, saved.price, saved.reorder_point) == \
        ("Green Tea Premium", 30, 35.0, 8)
    assert _actions(live_db) == ["ADD_PRODUCT", "UPDATE_PRODUCT"]


# ============================================================
# IT-03: การจัดการข้อผิดพลาดตลอดทั้งระบบ — ข้อมูลไม่เสียหาย
# ============================================================

def test_it03_invalid_operations_never_corrupt_data(monkeypatch, capsys, live_db):
    out = _run_menu(monkeypatch, capsys, [
        *_add("P001", "Green Tea", 20, 25.0, "Drink", "8850001", 5),
        "6",                                          # ยังไม่มีสินค้าใกล้หมด
        "2", "",                                      # รหัสสินค้าว่าง
        # ชื่อว่าง + กรอกตัวเลขผิดหลายครั้ง (Validator ต้องถามซ้ำจนได้ค่าที่ถูกต้อง)
        "2", "P010", "", "abc", "-1", "5", "x", "-2", "10", "Snack", "", "5",
        *_add("P011", "Copy Cat", 5, 10.0, "Drink", "8850001", 5),  # บาร์โค้ดซ้ำ
        "3", "NOPE",                                  # ตัดสต็อกสินค้าที่ไม่มี
        "3", "P001", "999",                           # ตัดเกินสต็อก
        "5", "",                                      # ค้นหาด้วยคำว่าง
        "5", "zzz",                                   # ค้นหาไม่พบ
        "8",
    ])

    assert "ไม่มีสินค้าที่ถึงจุดสั่งซื้อขั้นต่ำในขณะนี้" in out
    assert "ข้อผิดพลาด: รหัสสินค้าต้องไม่เป็นค่าว่าง" in out
    assert "กรุณากรอกจำนวนเต็มเท่านั้น" in out
    assert "กรุณากรอกตัวเลขเท่านั้น" in out
    assert out.count("ค่าต้องไม่ติดลบ กรุณากรอกใหม่") == 2
    assert "ข้อผิดพลาด: name ห้ามว่าง" in out
    assert "Barcode '8850001' ถูกใช้แล้วโดยสินค้า 'P001'" in out
    assert "ไม่พบสินค้ารหัสนี้" in out
    assert "ข้อผิดพลาด: สต็อกไม่พอสำหรับตัดจำนวนนี้" in out
    assert "ข้อผิดพลาด: คำค้นหาต้องไม่เป็นค่าว่าง" in out
    assert "ไม่พบข้อมูลสำหรับ: ผลการค้นหา 'zzz'" in out

    # ทุก error ต้องไม่ทิ้งข้อมูลขยะไว้ในฐานข้อมูล
    repo = ProductRepository(live_db)
    assert [p.product_id for p in repo.findAll()] == ["P001"]
    assert repo.findById("P001").quantity == 20
    assert live_db.executeQuery("SELECT COUNT(*) AS c FROM stock_movements").fetchone()["c"] == 0
    assert _actions(live_db) == ["ADD_PRODUCT", "SEARCH_PRODUCT"]


# ============================================================
# IT-04: Pagination ข้ามหลายหน้าผ่านเมนูจริง
# ============================================================

def test_it04_pagination_navigation_across_pages(monkeypatch, capsys, live_db):
    repo = ProductRepository(live_db)
    for i in range(1, 24):  # 23 รายการ = 3 หน้า (10 + 10 + 3)
        repo.upsertProduct(Product(f"B{i:02d}", f"Bulk {i:02d}", 10, 1.0, "Bulk"))

    out = _run_menu(monkeypatch, capsys, [
        "1", "p", "n", "n", "n", "p", "x", "q",
        "8",
    ])

    assert "หน้า 1/3" in out and "หน้า 2/3" in out and "หน้า 3/3" in out
    assert "แสดงรายการที่ 21 - 23 จากทั้งหมด 23 รายการ" in out
    assert ">> อยู่ที่หน้าแรกแล้ว" in out
    assert ">> อยู่ที่หน้าสุดท้ายแล้ว" in out
    assert ">> คำสั่งไม่ถูกต้อง กรุณาเลือก n, p หรือ q" in out


def test_it05_empty_inventory_screens(monkeypatch, capsys, live_db):
    out = _run_menu(monkeypatch, capsys, ["1", "4", "6", "8"])

    assert "ไม่พบข้อมูลสำหรับ: รายการสินค้าทั้งหมดในระบบ" in out
    assert "จำนวนชนิดสินค้าทั้งหมด: 0" in out
    assert "มูลค่าสินค้ารวม: 0.00 บาท" in out
    assert "จำนวนสินค้าใกล้หมด (<= 5): 0" in out
    assert "ไม่มีสินค้าที่ถึงจุดสั่งซื้อขั้นต่ำในขณะนี้" in out


# ============================================================
# IT-06: ข้อมูลคงอยู่หลังปิด/เปิดโปรแกรมใหม่ (Persistence)
# ============================================================

def test_it06_data_persists_after_restart(monkeypatch, capsys, db_path):
    DatabaseConnection.getInstance(db_path)
    _run_menu(monkeypatch, capsys, [
        *_add("P001", "Coffee", 10, 40.0, "Drink", "8850009", 3),
        "3", "P001", "4",
        "8",
    ])

    # ปิดโปรแกรม: ปิด connection และล้าง singleton ทั้งหมด เหมือนเริ่ม process ใหม่
    DatabaseConnection._instance.connection.close()
    DatabaseConnection._instance = None
    Logger._instance = None

    reopened = DatabaseConnection.getInstance(db_path)  # schema.sql รันซ้ำต้องไม่ลบข้อมูลเดิม
    out = _run_menu(monkeypatch, capsys, ["4", "8"])

    product = ProductRepository(reopened).findById("P001")
    assert (product.quantity, product.barcode, product.reorder_point) == (6, "8850009", 3)
    assert "จำนวนหน่วยสินค้ารวม: 6" in out
    assert "มูลค่าสินค้ารวม: 240.00 บาท" in out
    assert _actions(reopened) == ["ADD_PRODUCT", "CUT_STOCK"]


def test_it07_database_constraints_back_up_application_checks(live_db):
    """Defense in depth: แม้ข้ามชั้นแอปไปเขียน SQL ตรงๆ schema ก็ยังกันข้อมูลผิดไว้"""
    repo = ProductRepository(live_db)
    repo.upsertProduct(Product("P001", "Green Tea", 5, 25.0, barcode="8850001"))

    with pytest.raises(sqlite3.IntegrityError):  # partial UNIQUE index ของ barcode
        live_db.executeQuery(
            "INSERT INTO products (product_id, name, barcode) VALUES ('P002', 'Dup', '8850001')")
    live_db.rollback()

    with pytest.raises(sqlite3.IntegrityError):  # CHECK (quantity >= 0)
        live_db.executeQuery("UPDATE products SET quantity = -1 WHERE product_id = 'P001'")
    live_db.rollback()

    with pytest.raises(sqlite3.IntegrityError):  # FOREIGN KEY ของ stock_movements
        live_db.executeQuery(
            "INSERT INTO stock_movements (product_id, change_qty) VALUES ('GHOST', 1)")
    live_db.rollback()

    # สินค้าที่ไม่มีบาร์โค้ด ('') มีซ้ำกันได้หลายชิ้น
    repo.upsertProduct(Product("P003", "No Barcode A", 1, 1.0))
    repo.upsertProduct(Product("P004", "No Barcode B", 1, 1.0))
    assert len(repo.findAll()) == 3
    assert repo.findById("P001").quantity == 5


# ============================================================
# IT-08: Export CSV แบบ Atomic ผ่านเมนูจริง
# ============================================================

def test_it08_reexport_replaces_report_atomically(monkeypatch, capsys, live_db, isolated_cwd):
    report = isolated_cwd / "weekly.csv"
    _run_menu(monkeypatch, capsys, [
        *_add("P001", "Sugar", 2, 15.0, "Food", "", 5),
        *_add("P002", "Salt", 50, 10.0, "Food", "", 5),
        "7", "weekly.csv",
        "8",
    ])
    assert [row[0] for row in _read_csv(report)[1:]] == ["P001"]

    # เติมสต็อกจนไม่ต่ำแล้ว และให้อีกตัวต่ำแทน จากนั้น export ทับไฟล์เดิม
    repo = ProductRepository(live_db)
    repo.updateStock("P001", 20, reason="restock")
    repo.updateStock("P002", -48, reason="sale")
    out = _run_menu(monkeypatch, capsys, ["7", "weekly.csv", "8"])

    assert "Export สำเร็จ: 1 รายการ" in out
    assert _read_csv(report) == [
        ["ProductID", "ProductName", "Barcode", "Quantity", "ReorderPoint", "Price"],
        ["P002", "Salt", "", "2", "5", "10.0"],
    ]
    # ไม่มีไฟล์ชั่วคราว .tmp ค้างอยู่ในโฟลเดอร์หลัง atomic write
    assert not [name for name in os.listdir(isolated_cwd) if name.endswith(".tmp")]
    assert _actions(live_db).count("EXPORT_LOW_STOCK_CSV") == 2


# ============================================================
# IT-09: Entry point จริงของแต่ละโปรแกรม (python <file>.py)
# ============================================================

def _run_script(monkeypatch, filename, *args):
    monkeypatch.setattr(sys, "argv", [filename, *args])
    return runpy.run_path(os.path.join(HERE, filename), run_name="__main__")


def test_it09_inventory_app_entry_point_opens_menu(monkeypatch, capsys, isolated_cwd):
    DatabaseConnection.getInstance(str(isolated_cwd / "inventory.db"))
    _script_inputs(monkeypatch, ["4", "8"])

    _run_script(monkeypatch, "inventory_app.py")

    out = capsys.readouterr().out
    assert "INVENTORY SYSTEM" in out
    assert "จำนวนชนิดสินค้าทั้งหมด: 0" in out
    assert "ขอบคุณที่ใช้บริการ" in out


def test_it10_inventory_app_selftest_cleans_up(monkeypatch, capsys, isolated_cwd):
    _run_script(monkeypatch, "inventory_app.py", "--selftest")

    out = capsys.readouterr().out
    assert "สรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-12 ครบถ้วน 100%" in out
    assert "✓ เคลียร์ข้อมูลทดสอบเรียบร้อย" in out
    # self-test ต้องไม่ทิ้งสินค้าจำลองไว้ในฐานข้อมูล
    assert ProductRepository().findAll() == []


def test_it11_database_connection_selftest(monkeypatch, capsys, isolated_cwd):
    namespace = _run_script(monkeypatch, "database_connection.py")
    # run_path สร้างคลาส DatabaseConnection ชุดใหม่ใน namespace ของสคริปต์ ต้องปิดเอง
    namespace["DatabaseConnection"]._instance.connection.close()

    out = capsys.readouterr().out
    assert "สรุป: ผ่านเกณฑ์ Definition of Done ครบถ้วน 100% พร้อมส่งมอบ" in out
    assert os.path.exists(isolated_cwd / "inventory.db")


def test_it12_legacy_app_v1_entry_point(monkeypatch, capsys, isolated_cwd):
    _script_inputs(monkeypatch, ["4", "5"])

    _run_script(monkeypatch, "app_v1.py")

    out = capsys.readouterr().out
    assert "Total product types: 3" in out
    assert out.rstrip().endswith("Bye")
    assert not os.path.exists(isolated_cwd / "data.json")  # แค่ดูรายงาน ไม่ต้องเขียนไฟล์
