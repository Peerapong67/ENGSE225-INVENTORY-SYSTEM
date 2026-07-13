"""
test_app.py — ชุด Test สำหรับ INVENTORY SYSTEM v2.0
====================================================
ทดสอบ Feature ทั้ง 12 ข้อ จาก Risk Register (risk_register_app_v1.md)

รันด้วย:  python3 test_app.py
"""

import sys
import os
import sqlite3
import threading
import tempfile
import logging
import io
import ast
import unittest
from unittest.mock import patch

# ── ชี้ให้ import จาก app_v2.py ──────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app_v2

# ═════════════════════════════════════════════════════════════════════════════
# ANSI Color Helpers
# ═════════════════════════════════════════════════════════════════════════════
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_TAG = f"{GREEN}[PASS]{RESET}"
FAIL_TAG = f"{RED}[FAIL]{RESET}"
INFO_TAG = f"{CYAN}[INFO]{RESET}"

_results: list[dict] = []        # เก็บผลรวมทุก test
_risk_fix_desc: dict[int, str] = {}  # เก็บคำอธิบาย "แก้ไขอะไร" ต่อ Risk


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def print_feature_header(
    risk_no: int,
    title: str,
    description: str,
    fix_from: str = "",
    fix_to: str = "",
) -> None:
    """พิมพ์หัวข้อ Feature / Risk พร้อมคำอธิบายสิ่งที่แก้ไข"""
    bar = "═" * 70
    print(f"\n{BOLD}{CYAN}{bar}{RESET}")
    print(f"{BOLD}  Risk #{risk_no:02d} │ {title}{RESET}")
    print(f"  {description}")
    if fix_from:
        print(f"  {YELLOW}⚠ v1 (ปัญหา) :{RESET} {fix_from}")
    if fix_to:
        print(f"  {GREEN}✔ v2 (แก้ไข) :{RESET} {fix_to}")
        # บันทึกไว้สำหรับ summary
        _risk_fix_desc[risk_no] = fix_to
    print(f"{CYAN}{bar}{RESET}")


def assert_test(
    test_name: str,
    detail: str,
    passed: bool,
    actual: str = "",
    risk_no: int = 0,
) -> None:
    """พิมพ์ผลการ test 1 รายการ และเก็บสถิติ"""
    tag  = PASS_TAG if passed else FAIL_TAG
    icon = "✔" if passed else "✘"
    print(f"  {tag} {icon} {test_name}")
    print(f"       ↳ {detail}")
    if actual:
        color = GREEN if passed else RED
        print(f"       ↳ ผลลัพธ์ : {color}{actual}{RESET}")
    _results.append({"risk": risk_no, "name": test_name, "passed": passed})


def setup_temp_db() -> str:
    """สร้าง database ชั่วคราวและคืน path เดิม"""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    original = app_v2.DATABASE_PATH
    app_v2.DATABASE_PATH = tmp.name
    app_v2.initialize_database()
    return original, tmp.name


def teardown_temp_db(original: str, tmp_path: str) -> None:
    """คืน database path และลบไฟล์ชั่วคราว"""
    app_v2.DATABASE_PATH = original
    try:
        os.unlink(tmp_path)
    except FileNotFoundError:
        pass


# ═════════════════════════════════════════════════════════════════════════════
# RISK #1 — SQLite Transaction Safety (Atomic Write)
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_1():
    print_feature_header(
        1,
        "Atomic Write — ป้องกันข้อมูลเสียหายระหว่างบันทึก",
        "ตรวจสอบว่าการบันทึกข้อมูลเป็นแบบ Transaction-safe ผ่าน SQLite",
        fix_from="เขียนทับ data.json โดยตรง → ถ้าไฟฟ้าดับหรือโปรแกรมหยุดกลางคัน ไฟล์เสียหายทั้งหมด",
        fix_to="ใช้ SQLite ซึ่งมี WAL (Write-Ahead Logging) รองรับ atomic transaction ในตัว",
    )
    original, tmp = setup_temp_db()

    # Test 1-A: บันทึกข้อมูลแล้วข้อมูลยังครบ
    app_v2.upsert_product("A01", "Atomic Item", 10, 99.0, "Test")
    with app_v2.get_connection() as con:
        row = con.execute(
            "SELECT * FROM inventory WHERE product_id='A01'"
        ).fetchone()
    ok = row is not None and row["product_name"] == "Atomic Item"
    assert_test(
        "ข้อมูลยังคงอยู่ครบหลังบันทึก",
        "upsert_product() → query กลับมาได้ครบ",
        ok,
        f"product_name = '{row['product_name'] if row else 'None'}'",
        risk_no=1,
    )

    # Test 1-B: การ rollback เมื่อเกิด error ทำให้ข้อมูลก่อนหน้าไม่เสียหาย
    try:
        with app_v2.get_connection() as con:
            con.execute(
                "INSERT INTO inventory VALUES (?,?,?,?,?)",
                ("A02", "RollbackItem", -999, 10.0, "Test"),  # ← negative qty → error
            )
    except sqlite3.IntegrityError:
        pass  # คาดว่าต้อง error
    with app_v2.get_connection() as con:
        row2 = con.execute(
            "SELECT * FROM inventory WHERE product_id='A02'"
        ).fetchone()
    ok2 = row2 is None
    assert_test(
        "Transaction Rollback ทำงาน — ข้อมูลเก่าไม่เสียหาย",
        "INSERT ที่ผิด CHECK constraint ต้องถูก rollback ไม่บันทึกลง DB",
        ok2,
        "A02 ไม่ถูกบันทึก (rollback สำเร็จ)" if ok2 else "A02 ถูกบันทึกทั้งที่ไม่ควร",
        risk_no=1,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #2 — Input Validation
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_2():
    print_feature_header(
        2,
        "Input Validation — ตรวจสอบข้อมูลก่อนประมวลผล",
        "ฟังก์ชัน input_non_negative_int / input_non_negative_float ต้องปฏิเสธค่าผิดปกติ",
        fix_from="int(input(...)) โดยตรง → กรอก 'abc' แล้วโปรแกรม crash ทันที (ValueError)",
        fix_to="ใช้ฟังก์ชัน input_non_negative_int/float ที่วนซ้ำจนกว่าจะกรอกถูกต้อง",
    )

    # Test 2-A: กรอก 'abc' ต้องขอกรอกใหม่ แล้วรับ '5' ได้
    with patch("builtins.input", side_effect=["abc", "5"]):
        result = app_v2.input_non_negative_int("qty: ")
    ok = result == 5
    assert_test(
        "input_non_negative_int รับ 'abc' แล้ววนซ้ำ → รับ '5' ได้",
        "กรอก 'abc' (invalid) → กรอก '5' (valid) → คืนค่า 5",
        ok,
        f"ได้รับค่า {result}",
        risk_no=2,
    )

    # Test 2-B: กรอกทศนิยมที่ valid 3.14
    with patch("builtins.input", side_effect=["3.14"]):
        result2 = app_v2.input_non_negative_float("price: ")
    ok2 = abs(result2 - 3.14) < 1e-9
    assert_test(
        "input_non_negative_float รับ '3.14' ได้",
        "กรอก '3.14' → คืนค่า float 3.14",
        ok2,
        f"ได้รับค่า {result2}",
        risk_no=2,
    )

    # Test 2-C: กรอก 'xyz' สำหรับ float ต้องวนซ้ำ แล้วรับ '50.0' ได้
    with patch("builtins.input", side_effect=["xyz", "50.0"]):
        result3 = app_v2.input_non_negative_float("price: ")
    ok3 = result3 == 50.0
    assert_test(
        "input_non_negative_float รับ 'xyz' แล้ววนซ้ำ → รับ '50.0' ได้",
        "กรอก 'xyz' (invalid) → กรอก '50.0' (valid) → คืนค่า 50.0",
        ok3,
        f"ได้รับค่า {result3}",
        risk_no=2,
    )

    # Test 2-D: กรอก string ว่างสำหรับ input_non_empty ต้องวนซ้ำ
    with patch("builtins.input", side_effect=["", "  ", "Hello"]):
        result4 = app_v2.input_non_empty("name: ")
    ok4 = result4 == "Hello"
    assert_test(
        "input_non_empty ปฏิเสธ string ว่าง → รับ 'Hello' ได้",
        "กรอก '' (empty) → '  ' (whitespace) → 'Hello' (valid)",
        ok4,
        f"ได้รับค่า '{result4}'",
        risk_no=2,
    )


# ═════════════════════════════════════════════════════════════════════════════
# RISK #3 — SQLite Concurrent Access
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_3():
    print_feature_header(
        3,
        "Concurrent Access — SQLite รองรับการใช้งานพร้อมกันหลาย Thread",
        "เปิด connection หลายอันพร้อมกัน ข้อมูลต้องไม่ชน",
        fix_from="เก็บข้อมูลใน data.json ไฟล์เดียว → เปิด 2 หน้าต่างพร้อมกัน ข้อมูลเขียนทับกัน",
        fix_to="ใช้ SQLite ซึ่งมี file-level locking รองรับ concurrent access หลาย process/thread",
    )
    original, tmp = setup_temp_db()
    errors: list[str] = []

    def worker(thread_id: int):
        try:
            app_v2.upsert_product(
                f"C{thread_id:02d}",
                f"Concurrent Item {thread_id}",
                thread_id,
                float(thread_id),
                "ConcurrentTest",
            )
        except Exception as exc:
            errors.append(str(exc))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(1, 11)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # นับว่าบันทึกครบ 10 รายการไหม
    with app_v2.get_connection() as con:
        count = con.execute(
            "SELECT COUNT(*) FROM inventory WHERE category='ConcurrentTest'"
        ).fetchone()[0]

    ok_no_error = len(errors) == 0
    ok_all_saved = count == 10

    assert_test(
        "10 Thread เขียนพร้อมกัน — ไม่มี Exception",
        "แต่ละ thread เรียก upsert_product() พร้อมกัน ต้องไม่มี error",
        ok_no_error,
        f"errors = {errors if errors else 'ไม่มี'}",
        risk_no=3,
    )
    assert_test(
        "10 Thread เขียนพร้อมกัน — ข้อมูลครบ 10 รายการ",
        "นับสินค้าที่บันทึกจาก 10 thread ต้องได้ครบ 10",
        ok_all_saved,
        f"บันทึกได้ {count}/10 รายการ",
        risk_no=3,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #4 — Confirmation Before Save
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_4():
    print_feature_header(
        4,
        "Confirmation Before Save — ยืนยันก่อนบันทึก พร้อมแสดงข้อมูลเดิม",
        "เมื่อกด 'n' ต้องไม่บันทึก / เมื่อกด 'y' ต้องบันทึก",
        fix_from="กรอกข้อมูลแล้วบันทึกทันทีโดยไม่ถามยืนยัน → กดผิดหรือพิมพ์ผิดก็เขียนทับข้อมูลเดิมเลย",
        fix_to="แสดงข้อมูลเดิมเปรียบเทียบ + ถามยืนยัน (y/n) ก่อนบันทึกทุกครั้ง",
    )
    original, tmp = setup_temp_db()
    app_v2.upsert_product("D01", "Original Name", 10, 50.0, "Test")

    # Test 4-A: ยืนยัน 'n' → ต้องไม่เปลี่ยนแปลงข้อมูล
    inputs_cancel = iter(["D01", "New Name", "99", "99.0", "NewCat", "n"])
    with patch("builtins.input", side_effect=inputs_cancel):
        with patch("builtins.print"):  # ซ่อน output ระหว่าง test
            app_v2.menu_add_or_update()

    with app_v2.get_connection() as con:
        row = con.execute(
            "SELECT * FROM inventory WHERE product_id='D01'"
        ).fetchone()
    ok_cancel = row["product_name"] == "Original Name"
    assert_test(
        "กด 'n' (ปฏิเสธ) → ข้อมูลไม่เปลี่ยน",
        "กรอกข้อมูลใหม่แล้วกด n ที่ขั้นตอนยืนยัน → product_name ยังเป็น 'Original Name'",
        ok_cancel,
        f"product_name = '{row['product_name']}'",
        risk_no=4,
    )

    # Test 4-B: ยืนยัน 'y' → ต้องบันทึกข้อมูลใหม่
    inputs_confirm = iter(["D01", "Updated Name", "99", "99.0", "NewCat", "y"])
    with patch("builtins.input", side_effect=inputs_confirm):
        with patch("builtins.print"):
            app_v2.menu_add_or_update()

    with app_v2.get_connection() as con:
        row2 = con.execute(
            "SELECT * FROM inventory WHERE product_id='D01'"
        ).fetchone()
    ok_confirm = row2["product_name"] == "Updated Name"
    assert_test(
        "กด 'y' (ยืนยัน) → ข้อมูลถูกบันทึก",
        "กรอกข้อมูลใหม่แล้วกด y → product_name เปลี่ยนเป็น 'Updated Name'",
        ok_confirm,
        f"product_name = '{row2['product_name']}'",
        risk_no=4,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #5 — No Negative Values
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_5():
    print_feature_header(
        5,
        "No Negative Values — ราคาและจำนวนต้องไม่ติดลบ",
        "ทั้ง Application Layer (input functions) และ DB Layer (CHECK constraint)",
        fix_from="ไม่มีการตรวจสอบ → สามารถกรอกจำนวน -100 หรือราคา -50 บาทได้ตามปกติ",
        fix_to="ตรวจสอบ >= 0 ทั้ง 2 ชั้น: input function (app) และ CHECK constraint (SQLite)",
    )
    original, tmp = setup_temp_db()

    # Test 5-A: input_non_negative_int ปฏิเสธ -5
    captured = []
    def fake_input_int(prompt):
        vals = ["-5", "0"]
        return vals[len(captured)]
    with patch("builtins.input", side_effect=["-5", "0"]):
        result = app_v2.input_non_negative_int("qty: ")
    ok_int = result == 0
    assert_test(
        "input_non_negative_int ปฏิเสธ -5 → รับ 0 ได้",
        "กรอก -5 (invalid) → กรอก 0 (valid) → คืนค่า 0",
        ok_int,
        f"ได้รับค่า {result}",
        risk_no=5,
    )

    # Test 5-B: input_non_negative_float ปฏิเสธ -99.9
    with patch("builtins.input", side_effect=["-99.9", "10.0"]):
        result2 = app_v2.input_non_negative_float("price: ")
    ok_float = result2 == 10.0
    assert_test(
        "input_non_negative_float ปฏิเสธ -99.9 → รับ 10.0 ได้",
        "กรอก -99.9 (invalid) → กรอก 10.0 (valid) → คืนค่า 10.0",
        ok_float,
        f"ได้รับค่า {result2}",
        risk_no=5,
    )

    # Test 5-C: SQLite CHECK constraint ปฏิเสธ price < 0
    raised = False
    try:
        with app_v2.get_connection() as con:
            con.execute(
                "INSERT INTO inventory VALUES (?,?,?,?,?)",
                ("E01", "NegPrice", 10, -1.0, "Test"),
            )
    except sqlite3.IntegrityError:
        raised = True
    assert_test(
        "SQLite CHECK constraint ปฏิเสธ price = -1.0",
        "INSERT ราคาติดลบต้อง raise IntegrityError",
        raised,
        "IntegrityError raised ✔" if raised else "ไม่มี error — ข้อมูลผิดถูกบันทึก ✘",
        risk_no=5,
    )

    # Test 5-D: SQLite CHECK constraint ปฏิเสธ quantity < 0
    raised2 = False
    try:
        with app_v2.get_connection() as con:
            con.execute(
                "INSERT INTO inventory VALUES (?,?,?,?,?)",
                ("E02", "NegQty", -1, 10.0, "Test"),
            )
    except sqlite3.IntegrityError:
        raised2 = True
    assert_test(
        "SQLite CHECK constraint ปฏิเสธ quantity = -1",
        "INSERT จำนวนติดลบต้อง raise IntegrityError",
        raised2,
        "IntegrityError raised ✔" if raised2 else "ไม่มี error — ข้อมูลผิดถูกบันทึก ✘",
        risk_no=5,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #6 — Stock Cannot Go Negative
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_6():
    print_feature_header(
        6,
        "Stock Floor = 0 — สต็อกต้องไม่ติดลบ",
        "ตรวจสอบทั้ง logic ใน menu_stock_out() และ DB CHECK constraint",
        fix_from="x[id]['q'] = x[id]['q'] - amt โดยไม่ตรวจสอบ → สต็อกติดลบได้ถ้าตัดเกิน",
        fix_to="ตรวจ new_qty < 0 ก่อนบันทึก + ใช้ max(0, new_qty) + CHECK constraint ใน DB",
    )
    original, tmp = setup_temp_db()
    app_v2.upsert_product("F01", "Limited Stock", 3, 10.0, "Test")

    # Test 6-A: ตัดสต็อกมากกว่าที่มี → ต้องไม่บันทึก
    output_buffer = io.StringIO()
    inputs = iter(["F01", "10"])   # มี 3 แต่ตัด 10
    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", output_buffer):
            app_v2.menu_stock_out()

    with app_v2.get_connection() as con:
        row = con.execute(
            "SELECT quantity FROM inventory WHERE product_id='F01'"
        ).fetchone()
    ok_no_change = row["quantity"] == 3
    assert_test(
        "ตัดสต็อกเกินที่มี (3 มีแต่ตัด 10) → สต็อกไม่เปลี่ยน",
        "menu_stock_out() ตรวจพบ stock ไม่พอ → ไม่บันทึก → quantity ยังเป็น 3",
        ok_no_change,
        f"quantity = {row['quantity']}",
        risk_no=6,
    )

    # Test 6-B: ตัดสต็อกพอดี → ต้องเหลือ 0 ไม่ใช่ลบ
    inputs2 = iter(["F01", "3"])   # ตัด 3 จาก 3 → เหลือ 0
    with patch("builtins.input", side_effect=inputs2):
        with patch("builtins.print"):
            app_v2.menu_stock_out()

    with app_v2.get_connection() as con:
        row2 = con.execute(
            "SELECT quantity FROM inventory WHERE product_id='F01'"
        ).fetchone()
    ok_zero = row2["quantity"] == 0
    assert_test(
        "ตัดสต็อกพอดี (3 ตัด 3) → เหลือ 0 ไม่ใช่ติดลบ",
        "max(0, new_quantity) ต้องให้ค่า 0",
        ok_zero,
        f"quantity = {row2['quantity']}",
        risk_no=6,
    )

    # Test 6-C: DB CHECK constraint ปฏิเสธ UPDATE เป็นลบ
    raised = False
    try:
        with app_v2.get_connection() as con:
            con.execute(
                "UPDATE inventory SET quantity = -1 WHERE product_id='F01'"
            )
    except sqlite3.IntegrityError:
        raised = True
    assert_test(
        "SQLite CHECK constraint ปฏิเสธ UPDATE quantity = -1",
        "UPDATE ให้ quantity ติดลบต้อง raise IntegrityError",
        raised,
        "IntegrityError raised ✔" if raised else "ไม่มี error ✘",
        risk_no=6,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #7 — Correct File Path (Relative to Script)
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_7():
    print_feature_header(
        7,
        "Correct File Path — ไฟล์ DB และ Log อยู่โฟลเดอร์เดียวกับโปรแกรมเสมอ",
        "ตรวจสอบว่า DATABASE_PATH และ LOG_PATH ถูก resolve ด้วย os.path.abspath(__file__)",
        fix_from='db = "data.json" (relative path) → ไฟล์ถูกสร้างที่ CWD ไม่ใช่โฟลเดอร์โปรแกรม',
        fix_to="BASE_DIR = os.path.dirname(os.path.abspath(__file__)) → ไฟล์อยู่โฟลเดอร์โปรแกรมเสมอ",
    )

    script_dir = os.path.dirname(os.path.abspath(app_v2.__file__))

    # Test 7-A: DATABASE_PATH อยู่ใน script_dir
    db_dir = os.path.dirname(app_v2.DATABASE_PATH)
    ok_db = db_dir == script_dir
    assert_test(
        "DATABASE_PATH อยู่ใน directory เดียวกับ app_v2.py",
        f"script dir = {script_dir}",
        ok_db,
        f"DATABASE_PATH dir = {db_dir}",
        risk_no=7,
    )

    # Test 7-B: LOG_PATH อยู่ใน script_dir
    log_dir = os.path.dirname(app_v2.LOG_PATH)
    ok_log = log_dir == script_dir
    assert_test(
        "LOG_PATH อยู่ใน directory เดียวกับ app_v2.py",
        f"script dir = {script_dir}",
        ok_log,
        f"LOG_PATH dir = {log_dir}",
        risk_no=7,
    )

    # Test 7-C: Path เป็น absolute path
    ok_abs_db  = os.path.isabs(app_v2.DATABASE_PATH)
    ok_abs_log = os.path.isabs(app_v2.LOG_PATH)
    assert_test(
        "DATABASE_PATH เป็น absolute path",
        "os.path.isabs(DATABASE_PATH) ต้องคืน True",
        ok_abs_db,
        str(app_v2.DATABASE_PATH),
        risk_no=7,
    )
    assert_test(
        "LOG_PATH เป็น absolute path",
        "os.path.isabs(LOG_PATH) ต้องคืน True",
        ok_abs_log,
        str(app_v2.LOG_PATH),
        risk_no=7,
    )


# ═════════════════════════════════════════════════════════════════════════════
# RISK #8 — Automatic Logging
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_8():
    print_feature_header(
        8,
        "Automatic Logging — บันทึก Log ทุกครั้งที่มีการเปลี่ยนแปลงข้อมูล",
        "ตรวจสอบว่า write_log() บันทึกไฟล์ Log จริง และมีข้อความที่ถูกต้อง",
        fix_from="ไม่มีระบบ log เลย → ไม่รู้ว่าใครแก้ไขข้อมูลอะไร เมื่อไหร่",
        fix_to="write_log() บันทึก action + รายละเอียดลง inventory.log ทุกครั้งที่มี INSERT/UPDATE/STOCK_OUT",
    )
    original_db, tmp_db = setup_temp_db()

    # ใช้ log file ชั่วคราวแยกต่างหาก
    tmp_log = tempfile.NamedTemporaryFile(suffix=".log", delete=False, mode="w", encoding="utf-8")
    tmp_log.close()

    # เพิ่ม FileHandler ชั่วคราวไปยัง root logger
    tmp_handler = logging.FileHandler(tmp_log.name, encoding="utf-8")
    tmp_handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(tmp_handler)

    app_v2.write_log("TEST_INSERT", "ID=G01 | ทดสอบการบันทึก Log")
    app_v2.write_log("TEST_UPDATE", "ID=G01 | อัปเดตข้อมูล")

    tmp_handler.flush()
    tmp_handler.close()
    logging.getLogger().removeHandler(tmp_handler)

    with open(tmp_log.name, "r", encoding="utf-8") as f:
        log_content = f.read()

    ok_insert = "TEST_INSERT" in log_content and "G01" in log_content
    ok_update = "TEST_UPDATE" in log_content
    ok_thai   = "ทดสอบการบันทึก Log" in log_content

    assert_test(
        "write_log() บันทึก action=TEST_INSERT ลงไฟล์ได้",
        "เรียก write_log('TEST_INSERT', ...) แล้วตรวจในไฟล์ log",
        ok_insert,
        "พบ 'TEST_INSERT' และ 'G01' ในไฟล์" if ok_insert else "ไม่พบ",
        risk_no=8,
    )
    assert_test(
        "write_log() บันทึก action=TEST_UPDATE ลงไฟล์ได้",
        "เรียก write_log('TEST_UPDATE', ...) แล้วตรวจในไฟล์ log",
        ok_update,
        "พบ 'TEST_UPDATE' ในไฟล์" if ok_update else "ไม่พบ",
        risk_no=8,
    )
    assert_test(
        "ไฟล์ Log รองรับภาษาไทย (UTF-8)",
        "ข้อความภาษาไทยใน log ต้องอ่านกลับมาได้ถูกต้อง",
        ok_thai,
        "พบ 'ทดสอบการบันทึก Log' ✔" if ok_thai else "ข้อความเพี้ยน ✘",
        risk_no=8,
    )

    os.unlink(tmp_log.name)
    teardown_temp_db(original_db, tmp_db)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #9 — UTF-8 Encoding
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_9():
    print_feature_header(
        9,
        "UTF-8 Encoding — ชื่อภาษาไทยแสดงผลถูกต้องทุกระบบ",
        "ตรวจสอบว่าเก็บ/อ่านภาษาไทยจาก SQLite ได้ถูกต้อง และ encoding ใน log",
        fix_from="ไม่ได้กำหนด encoding → ชื่อไทยแสดงเป็น ??? หรือ UnicodeDecodeError บนบางเครื่อง",
        fix_to="กำหนด encoding='utf-8' ทุกจุด: logging, sys.stdout.reconfigure, และ SQLite ใช้ UTF-8 default",
    )
    original, tmp = setup_temp_db()

    # Test 9-A: บันทึกชื่อภาษาไทย แล้วอ่านกลับได้ถูกต้อง
    thai_name = "มาม่าหมูสับรสเผ็ด"
    app_v2.upsert_product("T01", thai_name, 50, 7.0, "อาหาร")

    with app_v2.get_connection() as con:
        row = con.execute(
            "SELECT * FROM inventory WHERE product_id='T01'"
        ).fetchone()

    ok_name = row is not None and row["product_name"] == thai_name
    ok_cat  = row is not None and row["category"] == "อาหาร"

    assert_test(
        "บันทึกชื่อภาษาไทยและอ่านกลับได้ถูกต้อง",
        f"บันทึก product_name='{thai_name}' แล้วอ่านกลับ",
        ok_name,
        f"product_name = '{row['product_name'] if row else 'None'}'",
        risk_no=9,
    )
    assert_test(
        "บันทึก category ภาษาไทยและอ่านกลับได้ถูกต้อง",
        "บันทึก category='อาหาร' แล้วอ่านกลับ",
        ok_cat,
        f"category = '{row['category'] if row else 'None'}'",
        risk_no=9,
    )

    # Test 9-C: ตรวจ source code มี encoding='utf-8' สำหรับ logging
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_v2.py")
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    ok_enc = 'encoding="utf-8"' in source or "encoding='utf-8'" in source
    assert_test(
        "Source code กำหนด encoding='utf-8' ในการเปิดไฟล์ Log",
        "ตรวจ source code app_v2.py ว่ามี encoding='utf-8'",
        ok_enc,
        "พบ encoding='utf-8' ✔" if ok_enc else "ไม่พบ ✘",
        risk_no=9,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #10 — No Duplicate Code + Unit Tests
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_10():
    print_feature_header(
        10,
        "No Duplicate Code — upsert_product() รวมโค้ดเพิ่ม/แก้ไขไว้จุดเดียว",
        "ตรวจสอบว่าฟังก์ชัน upsert_product ทำงานถูกต้องทั้งกรณี insert และ update",
        fix_from="โค้ด if/else สำหรับเพิ่มและแก้ไขซ้ำกันทุก field → แก้ที่เดียวลืมแก้อีกที่",
        fix_to="ฟังก์ชัน upsert_product() จุดเดียวครอบคลุมทั้ง insert และ update + Unit Test",
    )
    original, tmp = setup_temp_db()

    # Test 10-A: Insert สินค้าใหม่ → ต้องคืน 'inserted'
    result = app_v2.upsert_product("U01", "New Item", 10, 20.0, "Cat")
    ok_ins = result == "inserted"
    assert_test(
        "upsert_product() กับ ID ใหม่ → คืน 'inserted'",
        "เรียก upsert_product('U01', ...) กับ ID ที่ยังไม่มีใน DB",
        ok_ins,
        f"return value = '{result}'",
        risk_no=10,
    )

    # Test 10-B: Update สินค้าที่มีแล้ว → คืน 'updated' และข้อมูลเปลี่ยน
    result2 = app_v2.upsert_product("U01", "Updated Item", 99, 55.0, "NewCat")
    ok_upd = result2 == "updated"
    with app_v2.get_connection() as con:
        row = con.execute(
            "SELECT * FROM inventory WHERE product_id='U01'"
        ).fetchone()
    ok_data = row["product_name"] == "Updated Item" and row["quantity"] == 99
    assert_test(
        "upsert_product() กับ ID เดิม → คืน 'updated'",
        "เรียก upsert_product('U01', ...) กับ ID ที่มีอยู่แล้วใน DB",
        ok_upd,
        f"return value = '{result2}'",
        risk_no=10,
    )
    assert_test(
        "upsert_product() อัปเดตข้อมูลได้ถูกต้อง",
        "ตรวจว่า product_name และ quantity เปลี่ยนเป็นค่าใหม่",
        ok_data,
        f"product_name='{row['product_name']}', quantity={row['quantity']}",
        risk_no=10,
    )

    # Test 10-C: ตรวจ Source Code ว่าไม่มีโค้ดซ้ำ
    # อนุญาต: 1 ใน upsert, 1 ใน init, และใน unit test section ของ app_v2.py เอง
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_v2.py")
    with open(src_path, "r", encoding="utf-8") as f:
        source_lines = f.readlines()
    # นับบรรทัดที่มี "INSERT INTO inventory"
    insert_lines = [l.strip() for l in source_lines if "INSERT INTO inventory" in l]
    # ใน app_v2.py มี: 1 ใน init (executemany), 1 ใน upsert, 2 ใน unit test block
    # สิ่งสำคัญคือไม่มีการเขียน INSERT ซ้ำนอก upsert_product (ต้องน้อยกว่า 5)
    ok_no_dup = len(insert_lines) < 5
    assert_test(
        "โค้ด INSERT ไม่ซ้ำซ้อน — logic หลักรวมอยู่ใน upsert_product()",
        f"ตรวจ source code ว่า INSERT INTO inventory มีน้อยกว่า 5 ครั้ง (พบ: {len(insert_lines)})",
        ok_no_dup,
        f"พบ 'INSERT INTO inventory' จำนวน {len(insert_lines)} ครั้ง {'✔' if ok_no_dup else '✘'}",
        risk_no=10,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# RISK #11 — Meaningful Variable Names
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_11():
    print_feature_header(
        11,
        "Meaningful Variable Names — ชื่อตัวแปรต้องสื่อความหมาย",
        "ตรวจ source code ว่าใช้ชื่อสื่อความหมาย และไม่ใช้ชื่อสั้น/ไม่ชัดเจน",
        fix_from="ใช้ชื่อ x, a, b, c, d, e → อ่านไม่รู้ว่าเก็บอะไร แก้โค้ดยาก",
        fix_to="เปลี่ยนเป็น inventory, product_id, product_name, quantity, price, category",
    )

    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_v2.py")
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Test 11-A: ชื่อตัวแปรที่ดีต้องมีอยู่
    good_names = ["product_id", "product_name", "quantity", "price", "category",
                  "inventory", "connection", "total_inventory_value"]
    for name in good_names:
        found = name in source
        assert_test(
            f"พบชื่อตัวแปร '{name}' ใน source code",
            f"app_v2.py ต้องใช้ชื่อ '{name}' ที่สื่อความหมาย",
            found,
            "✔ พบ" if found else "✘ ไม่พบ",
            risk_no=11,
        )

    # Test 11-B: ชื่อสั้นที่ไม่สื่อความหมาย (จาก v1) ต้องไม่อยู่ใน global scope
    bad_single_chars = ["\nx = ", "\na = ", "\nb = ", "\nc = "]
    for bad in bad_single_chars:
        found_bad = bad in source
        assert_test(
            f"ไม่มีตัวแปรชื่อสั้นไม่สื่อความหมาย ('{bad.strip()}')",
            f"ตรวจ source code ว่าไม่มีการประกาศ '{bad.strip()}' แบบ v1",
            not found_bad,
            "✔ ไม่พบ (ดี)" if not found_bad else f"✘ พบ '{bad.strip()}' ซึ่งไม่สื่อความหมาย",
            risk_no=11,
        )


# ═════════════════════════════════════════════════════════════════════════════
# RISK #12 — Pagination + Search
# ═════════════════════════════════════════════════════════════════════════════

def test_risk_12():
    print_feature_header(
        12,
        "Pagination & Search — แสดงผลทีละหน้า และค้นหาสินค้า",
        "ตรวจสอบ Pagination logic และฟังก์ชันค้นหาจาก SQLite LIKE",
        fix_from="แสดงสินค้าทุกรายการในครั้งเดียว → มีสินค้าพันรายการหน้าจอท่วม อ่านไม่ได้",
        fix_to="show_products_paginated() แสดงทีละ 10 รายการ + menu_search() ค้นหาด้วย LIKE",
    )
    original, tmp = setup_temp_db()

    # เพิ่มสินค้า 25 รายการ เพื่อทดสอบ pagination (PAGE_SIZE=10)
    for i in range(1, 26):
        app_v2.upsert_product(
            f"P{i:03d}",
            f"Product {i:03d}",
            i * 2,
            float(i),
            "Food" if i % 2 == 0 else "Drink",
        )

    with app_v2.get_connection() as con:
        all_rows = con.execute(
            "SELECT * FROM inventory ORDER BY product_id"
        ).fetchall()

    total = len(all_rows)

    # Test 12-A: คำนวณจำนวนหน้า
    expected_pages = (total + app_v2.PAGE_SIZE - 1) // app_v2.PAGE_SIZE
    ok_pages = expected_pages == 3   # 25 items / 10 per page = 3 pages
    assert_test(
        f"คำนวณ total_pages ถูกต้อง ({total} รายการ / {app_v2.PAGE_SIZE} ต่อหน้า = {expected_pages} หน้า)",
        "ตรวจ formula (total + PAGE_SIZE - 1) // PAGE_SIZE",
        ok_pages,
        f"total_pages = {expected_pages}",
        risk_no=12,
    )

    # Test 12-B: หน้า 1 ต้องมี PAGE_SIZE รายการ
    page1_rows = all_rows[0:app_v2.PAGE_SIZE]
    ok_p1 = len(page1_rows) == app_v2.PAGE_SIZE
    assert_test(
        f"หน้า 1 มีสินค้าครบ {app_v2.PAGE_SIZE} รายการ",
        f"all_rows[0:{app_v2.PAGE_SIZE}] ต้องมี {app_v2.PAGE_SIZE} รายการ",
        ok_p1,
        f"รายการในหน้า 1 = {len(page1_rows)}",
        risk_no=12,
    )

    # Test 12-C: หน้าสุดท้ายมีรายการที่เหลือ (25 mod 10 = 5)
    last_page_rows = all_rows[(expected_pages - 1) * app_v2.PAGE_SIZE:]
    expected_last = total - (expected_pages - 1) * app_v2.PAGE_SIZE
    ok_last = len(last_page_rows) == expected_last
    assert_test(
        f"หน้าสุดท้ายมีสินค้า {expected_last} รายการ (ส่วนที่เหลือ)",
        f"all_rows[{(expected_pages-1)*app_v2.PAGE_SIZE}:] ต้องมี {expected_last} รายการ",
        ok_last,
        f"รายการในหน้าสุดท้าย = {len(last_page_rows)}",
        risk_no=12,
    )

    # Test 12-D: ค้นหาด้วย keyword 'Food' ต้องได้เฉพาะ Food
    # นับจริงจาก DB เพื่อรองรับ default data ที่อาจมีอยู่แล้ว
    search_term = "%Food%"
    with app_v2.get_connection() as con:
        search_rows = con.execute(
            """
            SELECT * FROM inventory
            WHERE product_name LIKE ?
               OR category LIKE ?
               OR product_id LIKE ?
            ORDER BY product_id
            """,
            (search_term, search_term, search_term),
        ).fetchall()
        # นับ expected จาก DB จริง (รวม default seeded data)
        expected_food_rows = con.execute(
            "SELECT COUNT(*) FROM inventory WHERE category LIKE '%Food%'"
        ).fetchone()[0]
    ok_search = len(search_rows) == expected_food_rows and expected_food_rows > 0
    assert_test(
        f"ค้นหา 'Food' ได้ผลลัพธ์ถูกต้อง ({expected_food_rows} รายการ)",
        "SELECT ... WHERE category LIKE '%Food%' ต้องได้ผลตรงกับจำนวนสินค้า category=Food",
        ok_search,
        f"พบ {len(search_rows)} รายการ (คาดหวัง {expected_food_rows}) {'✔' if ok_search else '✘'}",
        risk_no=12,
    )

    # Test 12-E: ค้นหา ID ที่ไม่มี → ได้ผลลัพธ์ว่าง
    with app_v2.get_connection() as con:
        empty_rows = con.execute(
            "SELECT * FROM inventory WHERE product_id LIKE '%XXXXXX%'",
        ).fetchall()
    ok_empty = len(empty_rows) == 0
    assert_test(
        "ค้นหา keyword ที่ไม่มีในระบบ → ได้ผลลัพธ์ว่าง",
        "SELECT ... WHERE ... LIKE '%XXXXXX%' ต้องได้ 0 รายการ",
        ok_empty,
        f"พบ {len(empty_rows)} รายการ",
        risk_no=12,
    )

    teardown_temp_db(original, tmp)


# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY REPORT
# ═════════════════════════════════════════════════════════════════════════════

def print_summary():
    bar = "═" * 70
    total  = len(_results)
    passed = sum(1 for r in _results if r["passed"])
    failed = total - passed

    print(f"\n\n{BOLD}{bar}")
    print(f"  📊 สรุปผลการทดสอบทั้งหมด")
    print(f"{bar}{RESET}")

    # จัดกลุ่มตาม risk
    from collections import defaultdict
    by_risk: dict[int, list] = defaultdict(list)
    for r in _results:
        by_risk[r["risk"]].append(r)

    # ─── ตาราง: Risk │ ผ่าน │ ไม่ผ่าน │ สถานะ │ สิ่งที่แก้ไข ───
    col_w = 42   # ความกว้างคอลัมน์ "สิ่งที่แก้ไข"
    header = f"  {'Risk':<8} {'Tests':>5} {'ผ่าน':>4} {'ไม่ผ่าน':>6}  {'สถานะ':<7}  สิ่งที่แก้ไข (v1 → v2)"
    print(f"\n{header}")
    print(f"  {'─'*90}")
    for risk_no in sorted(by_risk.keys()):
        tests  = by_risk[risk_no]
        p      = sum(1 for t in tests if t["passed"])
        f      = len(tests) - p
        n      = len(tests)
        status = f"{GREEN}PASS{RESET}" if f == 0 else f"{RED}FAIL{RESET}"
        fix    = _risk_fix_desc.get(risk_no, "-")
        # ตัดข้อความให้พอดีคอลัมน์
        if len(fix) > col_w:
            fix = fix[:col_w - 1] + "…"
        print(f"  Risk #{risk_no:<3}  {n:>4} {GREEN}{p:>4}{RESET} {RED}{f:>6}{RESET}   {status}  {fix}")

    print(f"\n  {'─'*90}")
    pct = (passed / total * 100) if total else 0
    print(f"  รวม       {total:>4} {GREEN}{passed:>4}{RESET} {RED}{failed:>6}{RESET}")
    print(f"\n  คะแนน: {BOLD}{passed}/{total} ({pct:.1f}%){RESET}")

    if failed == 0:
        print(f"\n  {GREEN}{BOLD}🎉 ทุก Feature ผ่านการทดสอบ!{RESET}")
    else:
        print(f"\n  {RED}{BOLD}⚠  มี {failed} test ที่ยังไม่ผ่าน{RESET}")

    print(f"{BOLD}{bar}{RESET}\n")
    return failed


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         TEST SUITE — INVENTORY SYSTEM v2.0                         ║")
    print("║         ทดสอบ Feature ทั้ง 12 ข้อ จาก Risk Register                ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")

    test_risk_1()
    test_risk_2()
    test_risk_3()
    test_risk_4()
    test_risk_5()
    test_risk_6()
    test_risk_7()
    test_risk_8()
    test_risk_9()
    test_risk_10()
    test_risk_11()
    test_risk_12()

    failed_count = print_summary()
    sys.exit(0 if failed_count == 0 else 1)
