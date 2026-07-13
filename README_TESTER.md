# README — Tester (test_app.py)

> เอกสารนี้อธิบายว่า **ทดสอบระบบ Inventory System v2.0 อย่างไร** และ **สรุปผลลัพธ์โดยรวม**
> จัดทำจากการอ่านโค้ด `test_app.py` เทียบกับ `app_v2.py` (ระบบจริง), `README.md` (ของ dev) และ `risk_register_app_v1.md`
>
> ⚠️ หมายเหตุ: เอกสารนี้จัดทำจาก **การตรวจสอบโค้ดแบบ static review** (อ่านโค้ดเทียบ logic) ไม่ใช่ผลจากการรันสคริปต์จริง

---

## 🎯 วัตถุประสงค์ของการทดสอบ

`test_app.py` เป็นชุดทดสอบที่เขียนขึ้นเพื่อ **ตรวจสอบว่าการแก้ไขความเสี่ยงทั้ง 12 ข้อ** (จาก v1.0 → v2.0)
ใน `app_v2.py` ทำงานได้จริงตามที่ dev เคลมไว้ใน `README.md` โดยทดสอบทั้งระดับ **Application Layer**
(ฟังก์ชันใน `app_v2.py`) และ **Database Layer** (CHECK constraint ของ SQLite)

ต่างจาก unit test ชุดเดิมที่ dev แนบมาในตัว `app_v2.py` (`python3 app_v2.py --test` → 5 tests, คลาส `TestInventory`)
ตรงที่ `test_app.py` เป็นชุดทดสอบที่ **ครอบคลุมกว่า** — แตกออกเป็น **48 test case ย่อย** ครบทั้ง 12 ความเสี่ยง
พร้อมพิมพ์รายงานสรุปสีสวยงาม (PASS/FAIL) ในตอนท้าย

---

## ⚙️ วิธีการรันทดสอบ

**ข้อกำหนดเบื้องต้น:** ต้องมี `test_app.py` และ `app_v2.py` อยู่ในโฟลเดอร์เดียวกัน (สคริปต์ `import app_v2` โดยตรง)

```bash
python3 test_app.py
```

สคริปต์จะ:
1. รันฟังก์ชันทดสอบ `test_risk_1()` ถึง `test_risk_12()` เรียงตามลำดับ
2. แต่ละฟังก์ชันสร้าง **database ชั่วคราว** (`tempfile`) แล้วสลับค่า `app_v2.DATABASE_PATH` ไปชี้ที่นั่นชั่วคราว แยกจาก `inventory.db` จริง เพื่อไม่ให้กระทบข้อมูลใช้งานจริง
3. ใช้ `unittest.mock.patch` เพื่อจำลอง input จากผู้ใช้ (เช่น กรอกค่าติดลบ, กด y/n) และเรียกฟังก์ชันเมนูของ `app_v2.py` ตรง ๆ (เช่น `menu_add_or_update()`, `menu_stock_out()`)
4. พิมพ์ผลลัพธ์ PASS/FAIL ของแต่ละเคส พร้อมค่าที่ได้จริง (actual value)
5. สรุปผลรวมเป็นตารางท้ายรายงาน และ `exit code` เป็น `0` ถ้าผ่านทั้งหมด, `1` ถ้ามี fail

---

## 🧪 ขอบเขตการทดสอบ แยกตาม Risk (ตรวจสอบกับ `app_v2.py` จริงแล้ว)

| Risk # | หัวข้อที่ทดสอบ | จำนวน Test Case | ฟังก์ชัน/กลไกใน `app_v2.py` ที่ถูกทดสอบ |
|---|---|---|---|
| 1 | Atomic Write | 2 | `upsert_product()`, SQLite transaction ผ่าน `with get_connection()` |
| 2 | Input Validation | 4 | `input_non_negative_int()`, `input_non_negative_float()`, `input_non_empty()` |
| 3 | Concurrent Access | 2 | `get_connection()` — เปิด connection ใหม่ทุกครั้ง รองรับหลาย thread |
| 4 | Confirmation Before Save | 2 | `menu_add_or_update()` — ขั้นตอนถาม `y/n` ก่อนเรียก `upsert_product()` |
| 5 | No Negative Values | 4 | `input_non_negative_int/float()` + `CHECK(quantity >= 0)`, `CHECK(price >= 0)` ใน `initialize_database()` |
| 6 | Stock Cannot Go Negative | 3 | `menu_stock_out()` (ตรวจ `new_quantity < 0` ก่อนบันทึก) + DB `CHECK(quantity >= 0)` |
| 7 | Correct File Path | 4 | `BASE_DIR`, `DATABASE_PATH`, `LOG_PATH` (ผูกกับ `os.path.abspath(__file__)`) |
| 8 | Automatic Logging | 3 | `write_log()` + `logging.basicConfig(filename=LOG_PATH, encoding="utf-8", ...)` |
| 9 | UTF-8 Encoding | 3 | `encoding="utf-8"` ใน `logging.basicConfig` และ `sys.stdout.reconfigure()` |
| 10 | No Duplicate Code | 4 | `upsert_product()` — จุดเดียวจัดการทั้ง insert/update |
| 11 | Meaningful Variable Names | 12 | ชื่อตัวแปรทั่วทั้งไฟล์ เช่น `product_id`, `product_name`, `quantity`, `price`, `category`, `connection`, `total_inventory_value` |
| 12 | Pagination & Search | 5 | `show_products_paginated()` (`PAGE_SIZE = 10`), `menu_search()` (SQL `LIKE`) |
| **รวม** | **12 Risk** | **48 Test Case** | |

---

## 📋 ผลลัพธ์โดยรวม (จากการตรวจโค้ด ไม่ใช่ผลรันจริง)

จากการเทียบ assertion ใน `test_app.py` กับโค้ดจริงใน `app_v2.py` ทีละ Risk พบว่า **โค้ดสอดคล้องกับสิ่งที่ test คาดหวังไว้ครบทุกจุด** ดังนี้:

- **Risk #7 (Path):** `DATABASE_PATH`/`LOG_PATH` ถูกสร้างจาก `BASE_DIR = os.path.dirname(os.path.abspath(__file__))` → เป็น absolute path และอยู่โฟลเดอร์เดียวกับสคริปต์เสมอ ตรงกับที่ test คาดไว้
- **Risk #9 (UTF-8):** พบ `encoding="utf-8"` ทั้งใน `logging.basicConfig` และ `sys.stdout.reconfigure(encoding="utf-8")` ตรงกับที่ test ค้นหาใน source code
- **Risk #10 (No Duplicate / upsert):** นับจำนวนบรรทัดที่มี `"INSERT INTO inventory"` ในไฟล์จริงได้ **4 ครั้ง** (1 ใน `initialize_database()`, 1 ใน `upsert_product()`, 2 ใน `run_unit_tests()`) ซึ่งน้อยกว่าเกณฑ์ `< 5` ที่ test กำหนดไว้ — ผ่านเงื่อนไข
- **Risk #11 (ชื่อตัวแปร):** ชื่อทั้ง 8 ที่ test เช็ค (`product_id`, `product_name`, `quantity`, `price`, `category`, `inventory`, `connection`, `total_inventory_value`) มีอยู่จริงในไฟล์ และไม่พบรูปแบบชื่อสั้นแบบ v1 (`x =`, `a =`, `b =`, `c =`) เลย
- **Risk #6 (Stock ≥ 0):** `menu_stock_out()` ตรวจ `new_quantity < 0` ก่อนบันทึกจริง และ schema มี `CHECK(quantity >= 0)` เป็นชั้นป้องกันที่สอง — ตรงกับทั้ง 3 test case
- Risk อื่น ๆ ที่เหลือ (#1–#5, #8, #12) ตรวจสอบแล้วฟังก์ชัน/พฤติกรรมที่ test เรียกใช้ (`upsert_product`, `write_log`, `show_products_paginated`, `PAGE_SIZE`, `menu_search`) มีอยู่จริงและ logic ตรงกับที่ test คาดหวัง

**สรุป:** จากการตรวจโค้ดแบบ static ทั้ง 48 test case **มีแนวโน้มสูงว่าจะ PASS ทั้งหมด** เพราะ implementation ใน `app_v2.py` สอดคล้องกับสิ่งที่ `test_app.py` ตรวจสอบในทุกจุดที่ตรวจสอบได้จากการอ่านโค้ด

> การตรวจแบบอ่านโค้ดไม่สามารถจับพฤติกรรม runtime บางอย่างได้ 100% (เช่น race condition จริงตอนรันหลาย thread พร้อมกันใน Risk #3 หรือพฤติกรรมจริงของ SQLite locking) จุดเหล่านี้ควรได้รับการยืนยันด้วยการรัน `python3 test_app.py` จริงอีกครั้งก่อนสรุปผลในรายงานฉบับทางการ

---

## 📁 ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | บทบาท |
|---|---|
| `app_v2.py` | ระบบจริงที่ถูกทดสอบ |
| `test_app.py` | ชุดทดสอบละเอียด 48 เคส ครอบคลุม 12 ความเสี่ยง |
| `README.md` | เอกสารของ dev อธิบายความเสี่ยงและการแก้ไข v1 → v2 |
| `README_TESTER.md` | ไฟล์นี้ — สรุปมุมมองฝั่ง Tester |