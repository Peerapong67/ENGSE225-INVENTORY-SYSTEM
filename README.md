# ENGSE225 — ระบบสินค้าคงคลัง (Inventory System)

> **วิชา ENGSE225 | Software Quality Assurance**  

---

## 📦 ชื่อระบบ

**Inventory System** — ระบบบริหารจัดการสินค้าคงคลังแบบ Command-Line Interface (CLI)  
ใช้สำหรับบันทึก เพิ่ม แก้ไข ตัดสต็อก และสรุปมูลค่าสินค้าในคลังสินค้า

| รายการ | รายละเอียด |
|---|---|
| ภาษาโปรแกรม | Python 3 |
| เวอร์ชันต้นฉบับ | `app_v1.py` — INVENTORY SYSTEM v1.0 |
| เวอร์ชันที่แก้ไขแล้ว | `app_v2.py` — INVENTORY SYSTEM v2.0 |
| ที่เก็บข้อมูล | v1: `data.json` → v2: `inventory.db` (SQLite) |
| ระบบ Log | `inventory.log` |

---

## ⚠️ ปัญหาและความเสี่ยงที่พบใน v1.0

จากการวิเคราะห์ `app_v1.py` พบความเสี่ยงทั้งหมด **12 รายการ** บันทึกไว้ใน [`risk_register_app_v1.md`](./risk_register_app_v1.md)

### ความเสี่ยงระดับ **สูงมาก** 🔴

| # | ปัญหา | ผลกระทบ |
|---|---|---|
| 1 | บันทึกไฟล์ `data.json` โดยตรง — ถ้าไฟ้ดับระหว่างเขียน ข้อมูลทั้งหมดหาย | ข้อมูลเสียหายถาวร |
| 2 | ไม่มีการตรวจสอบ Input — กรอกตัวอักษรในช่องตัวเลขทำให้โปรแกรมหยุดทันที (`ValueError`) | ระบบพัง |
| 3 | เก็บข้อมูลใน JSON file — เปิด 2 หน้าต่างพร้อมกันข้อมูลชนกัน/เสียหาย | Data Corruption |

### ความเสี่ยงระดับ **สูง** 🟠

| # | ปัญหา | ผลกระทบ |
|---|---|---|
| 4 | แก้ไขสินค้าโดยไม่มีการยืนยัน — เขียนทับข้อมูลเดิมทันที | เสี่ยงแก้ไขข้อมูลผิดโดยไม่รู้ตัว |
| 5 | กรอกจำนวนหรือราคาเป็นตัวเลขติดลบได้ | ข้อมูลไม่ถูกต้องในระบบ |
| 6 | สต็อกอาจติดลบได้หากตัดพร้อมกัน | จำนวนสินค้าผิดพลาด |

### ความเสี่ยงระดับ **ปานกลาง** 🟡

| # | ปัญหา | ผลกระทบ |
|---|---|---|
| 7 | path ของไฟล์ขึ้นกับโฟลเดอร์ที่เปิดโปรแกรม | ไฟล์สร้างผิดตำแหน่ง |
| 8 | ไม่มีระบบ Log — ไม่รู้ว่าใครแก้อะไร เมื่อไหร่ | ตรวจสอบย้อนหลังไม่ได้ |
| 9 | ไม่กำหนด UTF-8 — ชื่อภาษาไทยอาจแสดงผลเป็น `????` | ข้อมูลแสดงผิด |
| 10 | โค้ด Add/Update ซ้ำกันทั้ง 2 กรณี — ดูแลยาก | Maintainability ต่ำ |

### ความเสี่ยงระดับ **ต่ำ** 🟢

| # | ปัญหา | ผลกระทบ |
|---|---|---|
| 11 | ชื่อตัวแปรสั้น ไม่สื่อความหมาย (`x`, `a`, `b`, `c`) | อ่านโค้ดยาก |
| 12 | แสดงสินค้าทั้งหมดในครั้งเดียว — ถ้ามีหลายร้อยรายการหน้าจอล้น | UX แย่ |

---

## 🔧 การแก้ไขที่ทำใน v2.0

### Risk #1 — Atomic Write → **เปลี่ยนมาใช้ SQLite**
`app_v1.py` เขียนทับ `data.json` โดยตรง หาก process ถูกหยุดกลางคัน ไฟล์เสียหายถาวร  
→ **แก้ไข:** เปลี่ยนมาใช้ SQLite ซึ่งมี transaction ในตัว ข้อมูลจะ commit เมื่อสำเร็จเท่านั้น

```python
# v1 — เสี่ยง
with open(db, 'w') as f:
    json.dump(x, f)           # ถ้าหยุดตรงนี้ = ข้อมูลหาย

# v2 — ปลอดภัย
with get_connection() as connection:
    connection.execute("UPDATE inventory SET ...")   # SQLite transaction
```

### Risk #2, #5 — Input Validation
`app_v1.py` ใช้ `int(input(...))` โดยตรง ทำให้ `ValueError` ถ้ากรอกตัวอักษร  
→ **แก้ไข:** สร้างฟังก์ชัน `input_non_negative_int()` และ `input_non_negative_float()` ที่วนซ้ำจนกว่าจะได้ค่าที่ถูกต้อง และปฏิเสธค่าติดลบ

### Risk #3 — SQLite แทน JSON (Concurrent Access)
→ **แก้ไข:** ย้ายการเก็บข้อมูลจาก `data.json` ไปยัง `inventory.db` (SQLite) ซึ่งรองรับการเข้าถึงพร้อมกันได้อย่างปลอดภัย

### Risk #4 — ยืนยันก่อนบันทึก (Confirmation Step)
`app_v1.py` เขียนทับทันทีโดยไม่มีการถามยืนยัน  
→ **แก้ไข:** แสดงข้อมูลเดิมเปรียบเทียบกับข้อมูลใหม่ และถามยืนยัน `(y/n)` ก่อนบันทึกทุกครั้ง

### Risk #6 — ป้องกันสต็อกติดลบ
→ **แก้ไข:** ตรวจสอบสต็อกก่อนตัด + เพิ่ม `CHECK(quantity >= 0)` constraint ใน SQLite schema เป็น 2 ชั้นป้องกัน

### Risk #7 — กำหนด Path ให้แน่นอน
→ **แก้ไข:** ใช้ `os.path.dirname(os.path.abspath(__file__))` เพื่อให้ไฟล์ database และ log อยู่ในโฟลเดอร์เดียวกับโปรแกรมเสมอ

### Risk #8 — ระบบ Log อัตโนมัติ
→ **แก้ไข:** ใช้ Python `logging` module บันทึกทุก action (INSERT / UPDATE / STOCK_OUT / EXIT) ลงไฟล์ `inventory.log` พร้อม timestamp

### Risk #9 — UTF-8 Encoding
→ **แก้ไข:** กำหนด `encoding="utf-8"` ในทุกจุดที่อ่าน/เขียนไฟล์ และ `sys.stdout.reconfigure(encoding="utf-8")` สำหรับ Windows

### Risk #10 — รวมโค้ดซ้ำ + Unit Test
`app_v1.py` มีโค้ด add/update ที่เหมือนกันทุกบรรทัด  
→ **แก้ไข:** สร้างฟังก์ชัน `upsert_product()` เดียวที่จัดการทั้ง insert และ update พร้อม Unit Test ครอบคลุม

### Risk #11 — ชื่อตัวแปรสื่อความหมาย
→ **แก้ไข:** เปลี่ยนชื่อตัวแปรทั้งหมด เช่น `x` → `inventory`, `a/b/c/d/e` → `product_id/product_name/quantity/price/category`

### Risk #12 — Pagination + ค้นหา
→ **แก้ไข:** เพิ่มฟังก์ชัน `show_products_paginated()` แสดงทีละ 10 รายการ และเมนูที่ 5 สำหรับค้นหาด้วย ID / ชื่อ / หมวดหมู่

---

## ✅ ผลการทดสอบ (Unit Test)

รันด้วย: `python3 app_v2.py --test`

```
test_price_cannot_be_negative     ... ok   ✔  ราคาติดลบถูกปฏิเสธโดย DB constraint
test_quantity_cannot_be_negative  ... ok   ✔  จำนวนติดลบถูกปฏิเสธโดย DB constraint
test_stock_cannot_go_negative_via_constraint ... ok   ✔  อัปเดตสต็อกติดลบไม่ได้
test_upsert_insert                ... ok   ✔  เพิ่มสินค้าใหม่สำเร็จ
test_upsert_update                ... ok   ✔  แก้ไขสินค้าที่มีอยู่สำเร็จ

----------------------------------------------------------------------
Ran 5 tests in 0.029s

OK
```

**ผลลัพธ์: 5/5 tests ผ่านทั้งหมด ✅**

| Test Case | ความเสี่ยงที่ครอบคลุม | ผล |
|---|---|---|
| `test_price_cannot_be_negative` | Risk #5 — ราคาต้องไม่ติดลบ | ✅ PASS |
| `test_quantity_cannot_be_negative` | Risk #5 — จำนวนต้องไม่ติดลบ | ✅ PASS |
| `test_stock_cannot_go_negative_via_constraint` | Risk #6 — สต็อกไม่ต่ำกว่า 0 | ✅ PASS |
| `test_upsert_insert` | Risk #10 — เพิ่มสินค้าใหม่ | ✅ PASS |
| `test_upsert_update` | Risk #10 — แก้ไขสินค้าที่มีอยู่ | ✅ PASS |

---

## 📁 โครงสร้างไฟล์

```
ENGSE225-INVENTORY-SYSTEM/
├── app_v1.py              # ต้นฉบับ — มีความเสี่ยง 12 รายการ
├── app_v2.py              # เวอร์ชันแก้ไข — แก้ครบทุกความเสี่ยง
├── inventory.db           # ฐานข้อมูล SQLite (สร้างอัตโนมัติ)
├── inventory.log          # ไฟล์บันทึก Log (สร้างอัตโนมัติ)
├── test_app.py            # ไฟล์ Script เพิ่อใช้ Test โดยละเอียด
└── README.md              # ไฟล์นี้
```

---

## 🚀 วิธีการใช้งาน

```bash
# รันโปรแกรมหลัก
python3 app_v2.py

# รัน Unit Test
python3 app_v2.py --test
```

---

## 📊 สรุปเปรียบเทียบ v1 vs v2

| คุณสมบัติ | v1.0 | v2.0 |
|---|---|---|
| ที่เก็บข้อมูล | JSON file | SQLite |
| ป้องกันข้อมูลเสียหาย | ❌ | ✅ (DB Transaction) |
| ตรวจสอบ Input | ❌ | ✅ |
| ป้องกันค่าติดลบ | ❌ | ✅ (Validation + DB Constraint) |
| ยืนยันก่อนบันทึก | ❌ | ✅ |
| ระบบ Log | ❌ | ✅ |
| รองรับ UTF-8 | ❌ | ✅ |
| แบ่งหน้าแสดงผล | ❌ | ✅ |
| ฟังก์ชันค้นหา | ❌ | ✅ |
| Unit Test | ❌ | ✅ (5 tests) |
| ชื่อตัวแปรชัดเจน | ❌ | ✅ |