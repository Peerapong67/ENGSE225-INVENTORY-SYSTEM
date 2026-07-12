"""
INVENTORY SYSTEM v2.0
=====================
แก้ไขความเสี่ยงทั้ง 12 รายการจาก Risk Register (risk_register_app_v1.md)

Risk #1  → Atomic Write ป้องกันข้อมูลเสียหายระหว่างบันทึก
Risk #2  → Input Validation ตรวจสอบข้อมูลก่อนประมวลผล
Risk #3  → ใช้ SQLite แทน JSON รองรับการใช้งานพร้อมกัน
Risk #4  → ยืนยันก่อนบันทึก แสดงข้อมูลเดิมเปรียบเทียบ
Risk #5  → ตรวจสอบตัวเลขต้อง >= 0
Risk #6  → ตรวจสอบสต็อกไม่ให้ต่ำกว่า 0
Risk #7  → กำหนด path ให้ relative กับไดเรกทอรีของโปรแกรมเสมอ
Risk #8  → บันทึก Log อัตโนมัติทุกครั้งที่มีการเปลี่ยนแปลง
Risk #9  → กำหนด UTF-8 ในทุกจุดที่เกี่ยวข้องกับไฟล์/ข้อความ
Risk #10 → รวมโค้ดซ้ำเป็นฟังก์ชันเดียว + Unit Test
Risk #11 → เปลี่ยนชื่อตัวแปรให้สื่อความหมาย
Risk #12 → แสดงผลทีละหน้า (Pagination) + ฟังก์ชันค้นหา
"""

import sqlite3
import os
import sys
import logging
import datetime

# ─────────────────────────────────────────────
# Risk #7: กำหนด path ให้ relative กับไดเรกทอรีของไฟล์โปรแกรมเสมอ
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "inventory.db")
LOG_PATH = os.path.join(BASE_DIR, "inventory.log")

PAGE_SIZE = 10  # Risk #12: จำนวนสินค้าต่อหน้า

# ─────────────────────────────────────────────
# Risk #8: ตั้งค่าระบบ Log อัตโนมัติ
# ─────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    # Risk #9: กำหนด encoding=utf-8 สำหรับ log file
    encoding="utf-8",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def write_log(action: str, detail: str) -> None:
    """Risk #8: บันทึก log ทุกครั้งที่มีการเปลี่ยนแปลงข้อมูล"""
    logging.info(f"ACTION={action} | {detail}")


# ─────────────────────────────────────────────
# Risk #3: ใช้ SQLite แทน JSON รองรับการใช้งานพร้อมกัน (Concurrent Access)
# ─────────────────────────────────────────────
def get_connection() -> sqlite3.Connection:
    """เปิด connection ไปยัง SQLite database"""
    # Risk #9: สั่ง SQLite ให้ใช้ UTF-8 (ค่าเริ่มต้นของ Python sqlite3)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row  # Risk #11: เข้าถึงคอลัมน์ด้วยชื่อแทนดัชนี
    return connection


def initialize_database() -> None:
    """สร้างตารางและข้อมูลตัวอย่าง ถ้ายังไม่มีอยู่"""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                product_id   TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                quantity     INTEGER NOT NULL CHECK(quantity >= 0),
                price        REAL NOT NULL CHECK(price >= 0),
                category     TEXT NOT NULL
            )
        """)
        # เพิ่มข้อมูลตัวอย่างถ้าตารางว่างเปล่า
        cursor = connection.execute("SELECT COUNT(*) FROM inventory")
        if cursor.fetchone()[0] == 0:
            default_products = [
                ("101", "Mama Noodles",   50,  6.0,  "Food"),
                ("102", "Lactasoy Milk",  20,  12.0, "Drink"),
                ("103", "Singha Water",  100,  10.0, "Drink"),
            ]
            connection.executemany(
                "INSERT INTO inventory VALUES (?,?,?,?,?)",
                default_products,
            )
            write_log("INIT", "สร้างฐานข้อมูลใหม่พร้อมข้อมูลตัวอย่าง")


# ─────────────────────────────────────────────
# Risk #2 & #5: ฟังก์ชันตรวจสอบ Input
# ─────────────────────────────────────────────
def input_non_empty(prompt: str) -> str:
    """รับข้อความที่ไม่ว่าง พร้อมวนซ้ำถ้าว่าง"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  ⚠  กรุณากรอกข้อมูลให้ครบ")


def input_non_negative_int(prompt: str) -> int:
    """
    Risk #2: ตรวจสอบว่าเป็นตัวเลขจำนวนเต็ม
    Risk #5: ตรวจสอบว่า >= 0
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < 0:
                print("  ⚠  ค่าต้องไม่ติดลบ กรุณากรอกใหม่")
                continue
            return value
        except ValueError:
            print(f"  ⚠  '{raw}' ไม่ใช่จำนวนเต็ม กรุณากรอกใหม่")


def input_non_negative_float(prompt: str) -> float:
    """
    Risk #2: ตรวจสอบว่าเป็นตัวเลขทศนิยม
    Risk #5: ตรวจสอบว่า >= 0
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("  ⚠  ค่าต้องไม่ติดลบ กรุณากรอกใหม่")
                continue
            return value
        except ValueError:
            print(f"  ⚠  '{raw}' ไม่ใช่ตัวเลข กรุณากรอกใหม่")


# ─────────────────────────────────────────────
# Risk #10: รวมโค้ดบันทึกสินค้า (เพิ่ม/แก้ไข) ไว้ที่เดียว
# ─────────────────────────────────────────────
def upsert_product(
    product_id: str,
    product_name: str,
    quantity: int,
    price: float,
    category: str,
) -> str:
    """
    Risk #10: ฟังก์ชันกลางสำหรับทั้งเพิ่มและแก้ไขสินค้า
    คืนค่า 'inserted' หรือ 'updated'
    """
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE inventory
                SET product_name=?, quantity=?, price=?, category=?
                WHERE product_id=?
                """,
                (product_name, quantity, price, category, product_id),
            )
            write_log(
                "UPDATE",
                f"ID={product_id} | ชื่อ={product_name} | จำนวน={quantity} | ราคา={price} | หมวด={category}",
            )
            return "updated"
        else:
            connection.execute(
                "INSERT INTO inventory VALUES (?,?,?,?,?)",
                (product_id, product_name, quantity, price, category),
            )
            write_log(
                "INSERT",
                f"ID={product_id} | ชื่อ={product_name} | จำนวน={quantity} | ราคา={price} | หมวด={category}",
            )
            return "inserted"


# ─────────────────────────────────────────────
# Risk #12: แสดงรายการสินค้าแบบแบ่งหน้า
# ─────────────────────────────────────────────
def show_products_paginated(rows: list, page: int = 1) -> None:
    """แสดงสินค้าทีละหน้า PAGE_SIZE รายการต่อหน้า"""
    total = len(rows)
    if total == 0:
        print("  (ไม่พบสินค้า)")
        return

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_rows = rows[start:end]

    print(f"\n{'─'*60}")
    print(f"  หน้า {page}/{total_pages}  (รวม {total} รายการ)")
    print(f"{'─'*60}")
    print(f"  {'ID':<6} {'ชื่อสินค้า':<20} {'จำนวน':>6} {'ราคา':>8}  {'หมวด'}")
    print(f"{'─'*60}")
    for row in page_rows:
        print(
            f"  {row['product_id']:<6} {row['product_name']:<20} "
            f"{row['quantity']:>6} {row['price']:>8.2f}  {row['category']}"
        )
    print(f"{'─'*60}")

    if total_pages > 1:
        print(f"  [p=หน้าก่อน  n=หน้าถัดไป  q=ออก]")
        while True:
            nav = input("  ไปหน้า: ").strip().lower()
            if nav == "n" and page < total_pages:
                show_products_paginated(rows, page + 1)
                return
            elif nav == "p" and page > 1:
                show_products_paginated(rows, page - 1)
                return
            elif nav == "q":
                return
            else:
                print("  ⚠  กด n=ถัดไป  p=ก่อนหน้า  q=ออก")


# ─────────────────────────────────────────────
# เมนู 1: แสดงสินค้าทั้งหมด (Risk #12)
# ─────────────────────────────────────────────
def menu_show_all() -> None:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM inventory ORDER BY product_id"
        ).fetchall()
    show_products_paginated(rows)


# ─────────────────────────────────────────────
# เมนู 2: เพิ่ม/แก้ไขสินค้า (Risk #4, #5, #10)
# ─────────────────────────────────────────────
def menu_add_or_update() -> None:
    product_id = input_non_empty("  กรอก ID สินค้า: ")

    # Risk #4: ตรวจสอบว่ามีสินค้าอยู่แล้วหรือไม่ แล้วแสดงข้อมูลเดิมให้เปรียบเทียบ
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchone()

    if existing:
        print(f"\n  ──── ข้อมูลเดิมของสินค้า ID {product_id} ────")
        print(f"  ชื่อ     : {existing['product_name']}")
        print(f"  จำนวน   : {existing['quantity']}")
        print(f"  ราคา    : {existing['price']:.2f} บาท")
        print(f"  หมวดหมู่ : {existing['category']}")
        print(f"  ─────────────────────────────────")
        action_label = "แก้ไข"
    else:
        print(f"\n  ไม่พบ ID {product_id} → จะเพิ่มสินค้าใหม่")
        action_label = "เพิ่ม"

    # Risk #2, #5: ใช้ฟังก์ชัน input ที่ตรวจสอบแล้ว
    product_name = input_non_empty("  กรอกชื่อสินค้า: ")
    quantity     = input_non_negative_int("  กรอกจำนวน: ")
    price        = input_non_negative_float("  กรอกราคา (บาท): ")
    category     = input_non_empty("  กรอกหมวดหมู่: ")

    # Risk #4: แสดงข้อมูลที่จะบันทึก และให้ยืนยันก่อน
    print(f"\n  ──── ข้อมูลที่จะ{action_label} ────")
    print(f"  ชื่อ     : {product_name}")
    print(f"  จำนวน   : {quantity}")
    print(f"  ราคา    : {price:.2f} บาท")
    print(f"  หมวดหมู่ : {category}")
    print(f"  ────────────────────────────────")

    confirm = input(f"  ยืนยันการ{action_label}? (y/n): ").strip().lower()
    if confirm != "y":
        print("  ยกเลิกการดำเนินการ")
        return

    result = upsert_product(product_id, product_name, quantity, price, category)
    if result == "inserted":
        print(f"  ✔ เพิ่มสินค้า '{product_name}' สำเร็จ")
    else:
        print(f"  ✔ แก้ไขสินค้า '{product_name}' สำเร็จ")


# ─────────────────────────────────────────────
# เมนู 3: ตัดสต็อก (Risk #2, #6)
# ─────────────────────────────────────────────
def menu_stock_out() -> None:
    product_id = input_non_empty("  กรอก ID สินค้าที่จะตัดสต็อก: ")

    with get_connection() as connection:
        product = connection.execute(
            "SELECT * FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchone()

        if not product:
            print(f"  ⚠  ไม่พบสินค้า ID '{product_id}'")
            return

        print(f"  สินค้า: {product['product_name']} | สต็อกปัจจุบัน: {product['quantity']} ชิ้น")

        # Risk #2: ตรวจสอบว่าเป็นตัวเลข
        amount_out = input_non_negative_int("  จำนวนที่ต้องการตัดออก: ")

        # Risk #6: ตรวจสอบไม่ให้สต็อกติดลบ
        new_quantity = product['quantity'] - amount_out
        if new_quantity < 0:
            print(f"  ⚠  สต็อกไม่พอ! มีแค่ {product['quantity']} ชิ้น ไม่สามารถตัด {amount_out} ชิ้นได้")
            return

        # Risk #6: กำหนดค่าขั้นต่ำ = 0 (ป้องกัน race condition เพิ่มเติม)
        safe_quantity = max(0, new_quantity)

        connection.execute(
            "UPDATE inventory SET quantity = ? WHERE product_id = ?",
            (safe_quantity, product_id),
        )
        write_log(
            "STOCK_OUT",
            f"ID={product_id} | ตัดออก={amount_out} | คงเหลือ={safe_quantity}",
        )

    print(f"  ✔ ตัดสต็อกสำเร็จ | คงเหลือ: {safe_quantity} ชิ้น")
    if safe_quantity < 5:
        print("  ⚠⚠  คำเตือน: สินค้าใกล้หมด! (น้อยกว่า 5 ชิ้น)")


# ─────────────────────────────────────────────
# เมนู 4: สรุปมูลค่าและแจ้งเตือนสต็อกต่ำ
# ─────────────────────────────────────────────
def menu_summary() -> None:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM inventory").fetchall()

    total_product_types = len(rows)
    total_inventory_value = sum(row['quantity'] * row['price'] for row in rows)
    low_stock_items = [row['product_name'] for row in rows if row['quantity'] < 10]

    print(f"\n  จำนวนประเภทสินค้า   : {total_product_types} ประเภท")
    print(f"  มูลค่าสินค้ารวม     : {total_inventory_value:,.2f} บาท")
    if low_stock_items:
        print(f"  ⚠  สินค้าใกล้หมด (<10): {', '.join(low_stock_items)}")
    else:
        print(f"  ✔ สินค้าทุกรายการมีสต็อกเพียงพอ")


# ─────────────────────────────────────────────
# เมนู 5: ค้นหาสินค้า (Risk #12)
# ─────────────────────────────────────────────
def menu_search() -> None:
    keyword = input_non_empty("  กรอกคำค้นหา (ชื่อ/หมวด/ID): ")
    # Risk #9: SQLite ใช้ LIKE ซึ่ง case-insensitive สำหรับ ASCII โดยปริยาย
    search_term = f"%{keyword}%"
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM inventory
            WHERE product_name LIKE ?
               OR category     LIKE ?
               OR product_id   LIKE ?
            ORDER BY product_id
            """,
            (search_term, search_term, search_term),
        ).fetchall()

    print(f"\n  ผลการค้นหา '{keyword}':")
    show_products_paginated(rows)


# ─────────────────────────────────────────────
# เมนู หลัก
# ─────────────────────────────────────────────
def main() -> None:
    # Risk #9: ตั้ง stdout/stderr ให้รองรับ UTF-8 (สำหรับ Windows ด้วย)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    initialize_database()

    while True:
        print("\n╔══════════════════════════════════╗")
        print("║   INVENTORY SYSTEM v2.0           ║")
        print("╠══════════════════════════════════╣")
        print("║  1. แสดงสินค้าทั้งหมด (แบบแบ่งหน้า)  ║")
        print("║  2. เพิ่ม / แก้ไขสินค้า           ║")
        print("║  3. ตัดสต็อก                      ║")
        print("║  4. สรุปมูลค่าและแจ้งเตือน         ║")
        print("║  5. ค้นหาสินค้า                   ║")
        print("║  6. ออกจากโปรแกรม                 ║")
        print("╚══════════════════════════════════╝")

        # Risk #2: ตรวจสอบ input เมนู
        choice = input("  เลือกเมนู: ").strip()

        if choice == "1":
            menu_show_all()
        elif choice == "2":
            menu_add_or_update()
        elif choice == "3":
            menu_stock_out()
        elif choice == "4":
            menu_summary()
        elif choice == "5":
            menu_search()
        elif choice == "6":
            print("  ลาก่อน!")
            write_log("EXIT", "ผู้ใช้ปิดโปรแกรม")
            break
        else:
            print("  ⚠  ไม่มีเมนูนี้ กรุณาเลือกใหม่ (1-6)")


# ─────────────────────────────────────────────
# Unit Tests — Risk #10
# ─────────────────────────────────────────────
def run_unit_tests() -> None:
    """
    Risk #10: Unit Test ตรวจสอบฟังก์ชันหลัก
    รันด้วย:  python app_v2.py --test
    """
    import tempfile
    import unittest

    # ชี้ database ไปที่ไฟล์ชั่วคราวระหว่าง test
    global DATABASE_PATH
    original_db = DATABASE_PATH
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    DATABASE_PATH = tmp.name
    tmp.close()

    class TestInventory(unittest.TestCase):

        def setUp(self):
            initialize_database()

        # Risk #5: ค่าลบต้องกรองออก
        def test_price_cannot_be_negative(self):
            with get_connection() as con:
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute(
                        "INSERT INTO inventory VALUES (?,?,?,?,?)",
                        ("999", "Test", 10, -1.0, "Test"),
                    )

        def test_quantity_cannot_be_negative(self):
            with get_connection() as con:
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute(
                        "INSERT INTO inventory VALUES (?,?,?,?,?)",
                        ("998", "Test", -5, 10.0, "Test"),
                    )

        # Risk #10: upsert ทำงานถูกต้องทั้งกรณี insert และ update
        def test_upsert_insert(self):
            result = upsert_product("T01", "TestItem", 5, 10.0, "TestCat")
            self.assertEqual(result, "inserted")

        def test_upsert_update(self):
            upsert_product("T02", "Original", 5, 10.0, "Cat")
            result = upsert_product("T02", "Updated", 10, 20.0, "Cat")
            self.assertEqual(result, "updated")
            with get_connection() as con:
                row = con.execute(
                    "SELECT * FROM inventory WHERE product_id='T02'"
                ).fetchone()
            self.assertEqual(row["product_name"], "Updated")
            self.assertEqual(row["quantity"], 10)

        # Risk #6: สต็อกต้องไม่ต่ำกว่า 0 ผ่าน CHECK constraint
        def test_stock_cannot_go_negative_via_constraint(self):
            upsert_product("T03", "StockTest", 3, 5.0, "Cat")
            with get_connection() as con:
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute(
                        "UPDATE inventory SET quantity = -1 WHERE product_id='T03'"
                    )

    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestInventory)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    finally:
        DATABASE_PATH = original_db
        os.unlink(tmp.name)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_unit_tests()
    else:
        main()
