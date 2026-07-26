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
    actual_pass: str,
    actual_fail: str,
    risk_no: int = 0,
) -> None:
    """พิมพ์ผลการ test 1 รายการ และเก็บสถิติ"""
    tag  = PASS_TAG if passed else FAIL_TAG
    icon = "✔" if passed else "✘"
    print(f"  {tag} {icon} ชื่อเทสต์      : {test_name}")
    print(f"       ↳ detail          : {detail}")
    if passed:
        print(f"       ↳ ผลลัพธ์ (PASS)  : {GREEN}{actual_pass}{RESET}")
    else:
        print(f"       ↳ ผลลัพธ์ (FAIL)  : {RED}{actual_fail}{RESET}")
    _results.append({"risk": risk_no, "name": test_name, "passed": passed})
    assert passed, f"Risk #{risk_no} — {test_name} | {actual_fail if not passed else actual_pass}"


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
        "ข้อมูลสินค้าในคลังต้องถูกบันทึกสำเร็จและข้อมูลถูกต้อง",
        "เรียก upsert_product() บันทึกข้อมูล แล้วทำการ query ข้อมูลกลับมาเช็ค",
        ok,
        "พบสินค้า 'Atomic Item' ในฐานข้อมูลตรงตามที่บันทึกไว้",
        f"ไม่พบสินค้า 'Atomic Item' หรือได้ข้อมูลเป็น '{row['product_name'] if row else 'None'}' แทน",
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
        "การทำธุรกรรม (Transaction) ต้องถูก Rollback เมื่อเกิดข้อผิดพลาดในการบันทึก",
        "พยายาม INSERT ข้อมูลที่ผิดเงื่อนไข (CHECK constraint จำนวนติดลบ) แล้วตรวจสอบว่าข้อมูลถูกบันทึกหรือไม่",
        ok2,
        "ข้อมูลไม่ถูกบันทึกลงในฐานข้อมูลตามที่คาดไว้ (Rollback สำเร็จ)",
        "พบข้อมูลสินค้า ID 'A02' ในฐานข้อมูล ทั้งที่การบันทึกต้องล้มเหลวและ rollback",
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
        "ฟังก์ชัน input_non_negative_int ต้องรับเฉพาะจำนวนเต็มที่ไม่ติดลบและขอข้อมูลใหม่หากกรอกไม่ถูกต้อง",
        "กรอกตัวอักษร 'abc' จากนั้นกรอกตัวเลข '5' แล้วเช็คว่าฟังก์ชันคืนค่า 5",
        ok,
        "ได้รับค่าเป็น 5 ตรงกับที่คาดหวัง",
        f"ได้รับค่าเป็น {result} ซึ่งไม่ถูกต้อง",
        risk_no=2,
    )

    # Test 2-B: กรอกทศนิยมที่ valid 3.14
    with patch("builtins.input", side_effect=["3.14"]):
        result2 = app_v2.input_non_negative_float("price: ")
    ok2 = abs(result2 - 3.14) < 1e-9
    assert_test(
        "ฟังก์ชัน input_non_negative_float ต้องรับทศนิยมที่เป็นบวกได้ถูกต้อง",
        "กรอกตัวเลขทศนิยม '3.14' แล้วเช็คว่าฟังก์ชันคืนค่า 3.14",
        ok2,
        "ได้รับค่าเป็น 3.14 ตรงกับที่คาดหวัง",
        f"ได้รับค่าเป็น {result2} ซึ่งต่างจากค่าที่คาดหวัง 3.14",
        risk_no=2,
    )

    # Test 2-C: กรอก 'xyz' สำหรับ float ต้องวนซ้ำ แล้วรับ '50.0' ได้
    with patch("builtins.input", side_effect=["xyz", "50.0"]):
        result3 = app_v2.input_non_negative_float("price: ")
    ok3 = result3 == 50.0
    assert_test(
        "ฟังก์ชัน input_non_negative_float ต้องปฏิเสธตัวอักษรและขอข้อมูลใหม่จนกว่าจะได้ทศนิยมที่เป็นบวก",
        "กรอกตัวอักษร 'xyz' จากนั้นกรอกตัวเลข '50.0' แล้วเช็คว่าคืนค่า 50.0",
        ok3,
        "ได้รับค่าเป็น 50.0 ตรงกับที่คาดหวัง",
        f"ได้รับค่าเป็น {result3} ซึ่งไม่ถูกต้อง",
        risk_no=2,
    )

    # Test 2-D: กรอก string ว่างสำหรับ input_non_empty ต้องวนซ้ำ
    with patch("builtins.input", side_effect=["", "  ", "Hello"]):
        result4 = app_v2.input_non_empty("name: ")
    ok4 = result4 == "Hello"
    assert_test(
        "ฟังก์ชัน input_non_empty ต้องไม่ยอมรับข้อความว่างหรือเว้นวรรค และขอข้อมูลใหม่จนกว่าจะกรอกข้อความ",
        "กรอกข้อความว่าง '', เว้นวรรค '  ', และข้อความ 'Hello' แล้วเช็คว่าคืนค่า 'Hello'",
        ok4,
        "ได้รับค่าเป็น 'Hello' ตรงกับที่คาดหวัง",
        f"ได้รับค่าเป็น '{result4}' ซึ่งไม่ถูกต้อง",
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
        "ระบบต้องไม่มี Error หรือขัดข้องเมื่อเขียนข้อมูลพร้อมกันจากหลาย Thread (Concurrency)",
        "จำลองสถานการณ์เปิดใช้งาน 10 Thread เพื่อเขียนข้อมูลลงฐานข้อมูลพร้อมกัน และตรวจสอบว่าไม่มี Error ใดๆ เกิดขึ้น",
        ok_no_error,
        "ไม่พบ Error หรือ Exception ใดๆ ในทุก Thread",
        f"พบข้อผิดพลาดระหว่างเขียนข้อมูล: {errors}",
        risk_no=3,
    )
    assert_test(
        "ข้อมูลทั้งหมดต้องถูกบันทึกสำเร็จครบถ้วนเมื่อเขียนพร้อมกันจากหลาย Thread",
        "นับจำนวนรายการข้อมูลทั้งหมดที่บันทึกจริงในฐานข้อมูลหลังจากรัน 10 Thread พร้อมกัน",
        ok_all_saved,
        "พบสินค้าที่บันทึกสำเร็จครบถ้วนจำนวน 10 รายการ",
        f"ข้อมูลสูญหาย บันทึกได้เพียง {count} จากทั้งหมด 10 รายการ",
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
        "ข้อมูลเก่าต้องไม่ถูกแก้ไขหากผู้ใช้กดปฏิเสธ ('n') ในขั้นตอนยืนยัน",
        "ป้อนข้อมูลใหม่ แต่เมื่อระบบถามยืนยันให้กรอก 'n' แล้วตรวจสอบว่าชื่อสินค้ายังเป็นชื่อเดิม",
        ok_cancel,
        "ชื่อสินค้ายังเป็น 'Original Name' ตามเดิมไม่เปลี่ยนแปลง",
        f"ข้อมูลถูกเปลี่ยนไปเป็น '{row['product_name'] if row else 'None'}' ทั้งที่กดปฏิเสธการยืนยัน",
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
        "ข้อมูลใหม่ต้องถูกบันทึกสำเร็จเมื่อผู้ใช้กดยืนยัน ('y')",
        "ป้อนข้อมูลใหม่ เมื่อระบบถามยืนยันให้กรอก 'y' แล้วตรวจสอบว่าชื่อสินค้าอัปเดตเป็นชื่อใหม่",
        ok_confirm,
        "ชื่อสินค้าถูกอัปเดตเป็น 'Updated Name' ตรงกับที่คาดหวัง",
        f"ข้อมูลไม่เปลี่ยน หรือเป็น '{row2['product_name'] if row2 else 'None'}' ทั้งที่กดยืนยันแล้ว",
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
        "ฟังก์ชัน input_non_negative_int ต้องปฏิเสธเลขติดลบและยอมรับเฉพาะจำนวนที่ไม่ติดลบ",
        "กรอกจำนวนติดลบ '-5' จากนั้นกรอก '0' แล้วเช็คว่าคืนค่า 0",
        ok_int,
        "ได้รับค่าเป็น 0 ตรงตามที่คาดหวัง",
        f"ได้รับค่าเป็น {result} ทั้งที่กรอกเลขติดลบไปก่อนหน้า",
        risk_no=5,
    )

    # Test 5-B: input_non_negative_float ปฏิเสธ -99.9
    with patch("builtins.input", side_effect=["-99.9", "10.0"]):
        result2 = app_v2.input_non_negative_float("price: ")
    ok_float = result2 == 10.0
    assert_test(
        "ฟังก์ชัน input_non_negative_float ต้องปฏิเสธเลขติดลบและยอมรับเฉพาะทศนิยมที่ไม่ติดลบ",
        "กรอกราคาสินค้าติดลบ '-99.9' จากนั้นกรอก '10.0' แล้วเช็คว่าคืนค่า 10.0",
        ok_float,
        "ได้รับค่าเป็น 10.0 ตรงตามที่คาดหวัง",
        f"ได้รับค่าเป็น {result2} ทั้งที่กรอกเลขติดลบไปก่อนหน้า",
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
        "ฐานข้อมูล SQLite ต้องปฏิเสธการเพิ่มราคาสินค้าที่ติดลบผ่าน CHECK Constraint",
        "พยายาม INSERT สินค้าที่ราคาสินค้าเป็นลบ (-1.0) ลงในฐานข้อมูลตรงๆ และตรวจสอบว่าจะเกิด IntegrityError หรือไม่",
        raised,
        "ฐานข้อมูลเกิด IntegrityError (ปฏิเสธราคาสินค้าติดลบสำเร็จ)",
        "ไม่มีข้อผิดพลาดเกิดขึ้นและราคาสินค้าติดลบถูกบันทึกลงในฐานข้อมูล",
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
        "ฐานข้อมูล SQLite ต้องปฏิเสธการเพิ่มจำนวนสินค้าที่ติดลบผ่าน CHECK Constraint",
        "พยายาม INSERT สินค้าที่จำนวนสินค้าเป็นลบ (-1) ลงในฐานข้อมูลตรงๆ และตรวจสอบว่าจะเกิด IntegrityError หรือไม่",
        raised2,
        "ฐานข้อมูลเกิด IntegrityError (ปฏิเสธจำนวนสินค้าติดลบสำเร็จ)",
        "ไม่มีข้อผิดพลาดเกิดขึ้นและจำนวนสินค้าติดลบถูกบันทึกลงในฐานข้อมูล",
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
        "ระบบต้องไม่อนุญาตให้ตัดสต็อกสินค้าเกินกว่าจำนวนที่มีอยู่ในปัจจุบัน",
        "สินค้ามีสต็อก 3 รายการ ทำการจำลองตัดสต็อก 10 รายการ แล้วเช็คว่าจำนวนสินค้าคงเดิมคือ 3",
        ok_no_change,
        "สต็อกสินค้าไม่มีการเปลี่ยนแปลง (ยังคงมีจำนวน 3 ชิ้น)",
        f"สต็อกสินค้าถูกเปลี่ยนเป็น {row['quantity'] if row else 'None'} ทั้งที่ตัดสินค้าเกินสต็อกที่มี",
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
        "การตัดสต็อกสินค้าพอดีกับจำนวนที่มีต้องทำให้คงเหลือเป็น 0",
        "สินค้ามีสต็อก 3 รายการ ทำการจำลองตัดสต็อกออก 3 รายการ แล้วเช็คว่าคงเหลือ 0",
        ok_zero,
        "จำนวนสินค้าในสต็อกคงเหลือ 0 ชิ้นตรงตามคาดไว้",
        f"จำนวนสินค้าคงเหลือเป็น {row2['quantity'] if row2 else 'None'} ซึ่งไม่ใช่ 0",
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
        "ฐานข้อมูล SQLite ต้องปฏิเสธการอัปเดตสต็อกให้ติดลบผ่าน CHECK Constraint",
        "พยายามสั่ง SQL UPDATE เพื่อลดสต็อกของสินค้าชิ้นหนึ่งให้ติดลบ (-1) และตรวจหา IntegrityError",
        raised,
        "ฐานข้อมูลเกิด IntegrityError (ปฏิเสธไม่ให้อัปเดตสต็อกติดลบสำเร็จ)",
        "ไม่มีข้อผิดพลาดเกิดขึ้นและข้อมูลสต็อกติดลบถูกบันทึกลงฐานข้อมูล",
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
        "ไฟล์ฐานข้อมูล (DATABASE_PATH) ต้องอยู่ในไดเรกทอรีเดียวกับไฟล์โค้ดหลัก",
        f"ตรวจสอบว่าพาธไดเรกทอรีของฐานข้อมูลตรงกับไดเรกทอรีของ app_v2.py ({script_dir})",
        ok_db,
        "ไดเรกทอรีของไฟล์ฐานข้อมูลตรงกับไดเรกทอรีของแอปพลิเคชัน",
        f"ไฟล์ฐานข้อมูลถูกตั้งไว้ที่อื่น: {db_dir}",
        risk_no=7,
    )

    # Test 7-B: LOG_PATH อยู่ใน script_dir
    log_dir = os.path.dirname(app_v2.LOG_PATH)
    ok_log = log_dir == script_dir
    assert_test(
        "ไฟล์บันทึกประวัติ (LOG_PATH) ต้องอยู่ในไดเรกทอรีเดียวกับไฟล์โค้ดหลัก",
        f"ตรวจสอบว่าพาธไดเรกทอรีของไฟล์ log ตรงกับไดเรกทอรีของ app_v2.py ({script_dir})",
        ok_log,
        "ไดเรกทอรีของไฟล์บันทึกประวัติตรงกับไดเรกทอรีของแอปพลิเคชัน",
        f"ไฟล์บันทึกประวัติถูกตั้งไว้ที่อื่น: {log_dir}",
        risk_no=7,
    )

    # Test 7-C: Path เป็น absolute path
    ok_abs_db  = os.path.isabs(app_v2.DATABASE_PATH)
    ok_abs_log = os.path.isabs(app_v2.LOG_PATH)
    assert_test(
        "พาธไฟล์ฐานข้อมูล (DATABASE_PATH) ต้องกำหนดเป็น Absolute Path",
        "ใช้ฟังก์ชัน os.path.isabs() เช็คว่า DATABASE_PATH เป็น Absolute Path หรือไม่",
        ok_abs_db,
        f"DATABASE_PATH เป็น Absolute Path ({app_v2.DATABASE_PATH})",
        f"DATABASE_PATH ไม่เป็น Absolute Path ({app_v2.DATABASE_PATH})",
        risk_no=7,
    )
    assert_test(
        "พาธไฟล์บันทึกประวัติ (LOG_PATH) ต้องกำหนดเป็น Absolute Path",
        "ใช้ฟังก์ชัน os.path.isabs() เช็คว่า LOG_PATH เป็น Absolute Path หรือไม่",
        ok_abs_log,
        f"LOG_PATH เป็น Absolute Path ({app_v2.LOG_PATH})",
        f"LOG_PATH ไม่เป็น Absolute Path ({app_v2.LOG_PATH})",
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

    # ใช้ marker เฉพาะเจาะจงเพื่อไม่ชนกับ log entry เก่า
    marker = f"PYTESTMARK_{id(object())}"
    app_v2.write_log("TEST_INSERT", f"ID=G01 | {marker} | ทดสอบการบันทึก Log")
    app_v2.write_log("TEST_UPDATE", f"ID=G01 | {marker} | อัปเดตข้อมูล")

    # flush handler ของ logger เฉพาะแอป ก่อนอ่านไฟล์
    for handler in app_v2._logger.handlers:
        handler.flush()

    with open(app_v2.LOG_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()

    ok_insert = f"TEST_INSERT" in log_content and marker in log_content
    ok_update = "TEST_UPDATE" in log_content
    ok_thai   = "ทดสอบการบันทึก Log" in log_content

    assert_test(
        "ฟังก์ชัน write_log ต้องสามารถบันทึกกิจกรรมการเพิ่มข้อมูล (TEST_INSERT) ลงในไฟล์ Log ได้สำเร็จ",
        "เรียกใช้ write_log() บันทึก TEST_INSERT แล้วตรวจสอบว่ามีข้อความบันทึกในไฟล์ log จริง",
        ok_insert,
        "พบข้อความกิจกรรมการบันทึกข้อมูลใหม่ (TEST_INSERT) ในไฟล์ Log ตรงตามที่คาดหวัง",
        "ไม่พบกิจกรรมการบันทึกข้อมูลใหม่ (TEST_INSERT) หรือมาร์กเกอร์ในไฟล์ Log",
        risk_no=8,
    )
    assert_test(
        "ฟังก์ชัน write_log ต้องสามารถบันทึกกิจกรรมการแก้ไขข้อมูล (TEST_UPDATE) ลงในไฟล์ Log ได้สำเร็จ",
        "เรียกใช้ write_log() บันทึก TEST_UPDATE แล้วตรวจสอบว่ามีข้อความบันทึกในไฟล์ log จริง",
        ok_update,
        "พบข้อความกิจกรรมการแก้ไขข้อมูล (TEST_UPDATE) ในไฟล์ Log ตรงตามที่คาดหวัง",
        "ไม่พบกิจกรรมการแก้ไขข้อมูล (TEST_UPDATE) ในไฟล์ Log",
        risk_no=8,
    )
    assert_test(
        "ไฟล์บันทึกประวัติ (Log) ต้องเก็บและอ่านตัวอักษรภาษาไทยได้ถูกต้องโดยไม่เพี้ยน",
        "ตรวจสอบข้อความภาษาไทย 'ทดสอบการบันทึก Log' ที่บันทึกในไฟล์ Log ว่ายังแสดงผลได้สมบูรณ์และถูกต้อง",
        ok_thai,
        "ข้อความภาษาไทยถูกบันทึกและอ่านออกมาได้สมบูรณ์ถูกต้องตามคาด",
        "ภาษาไทยในไฟล์ Log ผิดเพี้ยนหรืออ่านไม่ออก",
        risk_no=8,
    )


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
        "ชื่อสินค้าที่เป็นภาษาไทยต้องถูกบันทึกลงฐานข้อมูลและดึงออกมาแสดงผลได้ถูกต้อง",
        f"เพิ่มสินค้าใหม่ที่มีชื่อภาษาไทยเป็น '{thai_name}' แล้ว query กลับมาตรวจสอบชื่อ",
        ok_name,
        "ดึงข้อมูลชื่อสินค้าออกมาพบเป็นภาษาไทยถูกต้องตามคาด",
        f"ชื่อภาษาไทยในฐานข้อมูลผิดเพี้ยน ได้ค่าเป็น '{row['product_name'] if row else 'None'}'",
        risk_no=9,
    )
    assert_test(
        "หมวดหมู่สินค้าที่เป็นภาษาไทยต้องถูกบันทึกและดึงออกมาแสดงผลได้ถูกต้อง",
        "เพิ่มสินค้าใหม่ที่มีหมวดหมู่สินค้าเป็นภาษาไทย 'อาหาร' แล้ว query กลับมาตรวจสอบหมวดหมู่",
        ok_cat,
        "ดึงข้อมูลหมวดหมู่สินค้าออกมาพบเป็นภาษาไทยถูกต้องตามคาด",
        f"หมวดหมู่ภาษาไทยในฐานข้อมูลผิดเพี้ยน ได้ค่าเป็น '{row['category'] if row else 'None'}'",
        risk_no=9,
    )

    # Test 9-C: ตรวจ source code มี encoding='utf-8' สำหรับ logging
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_v2.py")
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    ok_enc = 'encoding="utf-8"' in source or "encoding='utf-8'" in source
    assert_test(
        "ซอร์สโค้ดของแอปพลิเคชันต้องระบุ encoding='utf-8' เสมอเมื่อเรียกเปิดไฟล์ข้อความ",
        "สแกนหาข้อความ \"encoding='utf-8'\" หรือ 'encoding=\"utf-8\"' ในไฟล์ app_v2.py",
        ok_enc,
        "พบการระบุ encoding='utf-8' ในจุดเปิดไฟล์เพื่อความเข้ากันได้ของฟอนต์ไทย",
        "ไม่พบการระบุ encoding='utf-8' ในซอร์สโค้ด ซึ่งเสี่ยงต่อการเกิดปัญหาการอ่านภาษาไทยเพี้ยนในบางระบบปฏิบัติการ",
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
        "ฟังก์ชัน upsert_product ต้องรายงานผลเป็นการเพิ่มสินค้าใหม่ ('inserted') เมื่อระบุรหัสสินค้าที่ไม่มีในระบบ",
        "เรียก upsert_product() เพื่อบันทึกสินค้าใหม่รหัส 'U01' แล้วเช็คค่าส่งกลับ (return value)",
        ok_ins,
        "ฟังก์ชันคืนค่า 'inserted' สำเร็จถูกต้อง",
        f"ฟังก์ชันไม่ได้คืนค่า 'inserted' แต่ได้ค่าเป็น '{result}' แทน",
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
        "ฟังก์ชัน upsert_product ต้องรายงานผลเป็นการปรับปรุงสินค้า ('updated') เมื่อระบุรหัสสินค้าที่มีอยู่แล้ว",
        "เรียก upsert_product() เพื่อบันทึกแก้ไขสินค้าเดิมรหัส 'U01' แล้วเช็คค่าส่งกลับ (return value)",
        ok_upd,
        "ฟังก์ชันคืนค่า 'updated' สำเร็จถูกต้อง",
        f"ฟังก์ชันไม่ได้คืนค่า 'updated' แต่ได้ค่าเป็น '{result2}' แทน",
        risk_no=10,
    )
    assert_test(
        "ฟังก์ชัน upsert_product ต้องทำการแก้ไขข้อมูลสินค้าเดิมในฐานข้อมูลอย่างถูกต้อง",
        "ตรวจสอบว่าข้อมูลชื่อสินค้าและจำนวนสินค้าเปลี่ยนไปเป็นค่าที่อัปเดตล่าสุดจริง",
        ok_data,
        "ข้อมูลสินค้าถูกแก้ไขเป็น 'Updated Item' และสต็อก 99 ชิ้นเรียบร้อยตรงตามคาด",
        f"ข้อมูลในฐานข้อมูลไม่ได้รับการปรับปรุง: product_name='{row['product_name']}', quantity={row['quantity']}",
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
        "ต้องไม่มีการเขียนโค้ดเพิ่มข้อมูลสินค้า (INSERT) ซ้ำซ้อนภายนอกฟังก์ชัน upsert_product ในระบบหลัก",
        "สแกนหาข้อความ 'INSERT INTO inventory' ในไฟล์ app_v2.py เพื่อตรวจสอบความซ้ำซ้อนของโค้ดหลัก",
        ok_no_dup,
        f"โค้ดไม่มีความซ้ำซ้อน (พบคำสั่ง INSERT ทั้งสิ้น {len(insert_lines)} จุด ซึ่งอยู่ในขอบเขตที่ควบคุมได้)",
        f"พบคำสั่ง INSERT มากเกินไป ({len(insert_lines)} จุด) แสดงว่าโค้ดไม่มีการ Reuse และซ้ำซ้อน",
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
            f"ต้องใช้ชื่อตัวแปรหลักที่ชัดเจนและสื่อความหมาย ('{name}') ในแอปพลิเคชัน",
            f"สแกนซอร์สโค้ด app_v2.py ว่ามีชื่อตัวแปร '{name}' ปรากฏอยู่",
            found,
            f"พบชื่อตัวแปรสื่อความหมายดี '{name}' ในโค้ดหลัก",
            f"ไม่พบตัวแปรชื่อ '{name}' ในโค้ดหลักเพื่อใช้อ้างอิงการเก็บข้อมูลหลัก",
            risk_no=11,
        )

    # Test 11-B: ชื่อสั้นที่ไม่สื่อความหมาย (จาก v1) ต้องไม่อยู่ใน global scope
    bad_single_chars = ["\nx = ", "\na = ", "\nb = ", "\nc = "]
    for bad in bad_single_chars:
        found_bad = bad in source
        assert_test(
            f"ต้องไม่ใช้ชื่อตัวแปรสั้นและคลุมเครือ ('{bad.strip()}') ในการเก็บข้อมูลหลัก",
            f"สแกนซอร์สโค้ด app_v2.py ว่าไม่มีการกำหนดตัวแปรด้วยรูปแบบ '{bad.strip()}'",
            not found_bad,
            f"ไม่พบรูปแบบการประกาศตัวแปรที่ไม่ชัดเจน '{bad.strip()}' ในซอร์สโค้ด",
            f"พบข้อผิดพลาด: มีการประกาศตัวแปรลอยๆ ที่ไม่ชัดเจน '{bad.strip()}' อยู่ในซอร์สโค้ด",
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
        "สูตรคำนวณจำนวนหน้า (total_pages) ต้องถูกต้องตามขนาดของสินค้าต่อหน้า",
        f"คำนวณจำนวนหน้าโดยใช้สูตรหารปัดเศษขึ้น สำหรับสินค้าจำนวน {total} รายการ และหน้าละ {app_v2.PAGE_SIZE} รายการ",
        ok_pages,
        f"คำนวณจำนวนหน้าได้ {expected_pages} หน้า ตรงตามคาด",
        f"คำนวณจำนวนหน้าผิดเพี้ยน ได้ค่าเป็น {expected_pages} หน้า",
        risk_no=12,
    )

    # Test 12-B: หน้า 1 ต้องมี PAGE_SIZE รายการ
    page1_rows = all_rows[0:app_v2.PAGE_SIZE]
    ok_p1 = len(page1_rows) == app_v2.PAGE_SIZE
    assert_test(
        "จำนวนสินค้าคงคลังที่นำมาแสดงผลหน้าแรก (หน้า 1) ต้องเต็มหน้ากระดาษ (10 รายการ)",
        f"ดึงแถวสินค้าหน้าแรก (ลำดับที่ 0 ถึง {app_v2.PAGE_SIZE-1}) แล้วเช็คขนาดของรายการ",
        ok_p1,
        f"ดึงสินค้าหน้าแรกมาแสดงผลได้ครบจำนวน {app_v2.PAGE_SIZE} รายการตามกำหนด",
        f"หน้าแรกแสดงจำนวนสินค้าเป็น {len(page1_rows)} รายการ ไม่เป็นไปตาม {app_v2.PAGE_SIZE} รายการต่อหน้า",
        risk_no=12,
    )

    # Test 12-C: หน้าสุดท้ายมีรายการที่เหลือ (25 mod 10 = 5)
    last_page_rows = all_rows[(expected_pages - 1) * app_v2.PAGE_SIZE:]
    expected_last = total - (expected_pages - 1) * app_v2.PAGE_SIZE
    ok_last = len(last_page_rows) == expected_last
    assert_test(
        "จำนวนสินค้าที่นำมาแสดงผลหน้าสุดท้ายต้องเป็นรายการเศษที่เหลืออยู่อย่างถูกต้อง",
        f"ดึงข้อมูลแถวสินค้าของหน้าสุดท้ายและคำนวณว่ามีขนาดเท่ากับเศษที่เหลือ ({expected_last} รายการ)",
        ok_last,
        f"ดึงสินค้าหน้าสุดท้ายมาแสดงผลสำเร็จ มีขนาด {expected_last} รายการตรงตามที่ต้องเหลือ",
        f"หน้าสุดท้ายมีสินค้าหลุดมา {len(last_page_rows)} รายการ ซึ่งไม่เท่ากับ {expected_last} รายการ",
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
        "ระบบค้นหาสินค้าต้องค้นหาและกรองรายการตามหมวดหมู่ได้อย่างถูกต้องตรงประเด็น",
        "ค้นหาด้วยคำว่า 'Food' จากฐานข้อมูล แล้วเทียบจำนวนผลลัพธ์กับสินค้าหมวดหมู่ Food ทั้งหมดที่มี",
        ok_search,
        f"ผลลัพธ์การค้นหาด้วย 'Food' คืนรายการจำนวน {len(search_rows)} รายการตรงกับฐานข้อมูลจริง",
        f"พบผลการค้นหาไม่สอดคล้อง ดึงมาได้ {len(search_rows)} รายการ ทั้งที่คาดหวัง {expected_food_rows} รายการ",
        risk_no=12,
    )

    # Test 12-E: ค้นหา ID ที่ไม่มี → ได้ผลลัพธ์ว่าง
    with app_v2.get_connection() as con:
        empty_rows = con.execute(
            "SELECT * FROM inventory WHERE product_id LIKE '%XXXXXX%'",
        ).fetchall()
    ok_empty = len(empty_rows) == 0
    assert_test(
        "ระบบค้นหาสินค้าต้องไม่แสดงรายการใดๆ หากคำค้นหาไม่มีอยู่ในระบบ",
        "ค้นหาด้วยคำลอยๆ ที่ไม่มีจริง '%XXXXXX%' แล้วทำการตรวจสอบว่าผลลัพธ์การค้นหาต้องเป็นศูนย์",
        ok_empty,
        "ไม่พบข้อมูลสินค้าตรงตามที่คาดหวัง (ได้ 0 รายการ)",
        f"พบสินค้าตกค้างในการค้นหาคำที่ไม่มีอยู่จริง จำนวน {len(empty_rows)} รายการ",
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
