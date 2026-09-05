# ENGSE225 — Inventory System

ระบบจัดการสต็อกสินค้า (Inventory Management System) พัฒนาเป็นส่วนหนึ่งของวิชา ENGSE225 โดยเริ่มจากโปรแกรมต้นแบบเวอร์ชันแรก (`app_v1.py`) แล้ว refactor ใหม่ทั้งหมดให้เป็นสถาปัตยกรรมเชิงวัตถุที่แยกชั้นความรับผิดชอบชัดเจน ตาม Repository Pattern และ Singleton Pattern

## ทำไมต้อง Refactor

เวอร์ชันแรก (`app_v1.py`) เก็บข้อมูลในไฟล์ `data.json` ตรงๆ ผ่าน global dict ไม่มีการตรวจสอบข้อมูลนำเข้า และไม่มี unit test เลย ซึ่งเสี่ยงต่อข้อมูลเสียหายและแก้ไขยาก รายละเอียดความเสี่ยงทั้งหมดที่พบและแผนรับมือ ดูได้ที่ [`risk_register_app_v1_emoji.md`](./risk_register_app_v1_emoji.md)

เวอร์ชันปัจจุบัน (`inventory_app.py` และคลาสสนับสนุน) แก้ไขปัญหาเหล่านั้นด้วยการย้ายไปใช้ฐานข้อมูล SQLite, แยก logic การเข้าถึงข้อมูลออกจาก business logic (Repository Pattern), บังคับให้มี database connection เดียวทั้งระบบ (Singleton Pattern), และเพิ่ม validation ทุกจุดที่รับ input จากผู้ใช้

## สถาปัตยกรรม

```
InventoryApp   ─┬─ uses ─▶ Validator          (ตรวจสอบ input จากผู้ใช้)
                ├─ uses ─▶ ProductRepository   (เข้าถึงข้อมูลสินค้า)
                └─ uses ─▶ Logger              (บันทึก action log, Singleton)

ProductRepository ─┬─ creates and manages ─▶ Product            (entity)
                    └─ uses (Singleton)     ─▶ DatabaseConnection (เชื่อมต่อ SQLite เดียวทั้งระบบ)
```

- **Repository Pattern** — `ProductRepository` เป็นจุดเดียวที่คุยกับฐานข้อมูล ทำให้ `InventoryApp` ไม่ผูกติดกับวิธีเก็บข้อมูล และทดสอบแยกส่วนได้ง่าย
- **Singleton Pattern** — `DatabaseConnection` และ `Logger` มี instance เดียวทั้งโปรแกรม ป้องกันการเปิด connection ซ้ำซ้อน

## ฟีเจอร์หลัก

| เมนู | คำอธิบาย |
|---|---|
| แสดงสินค้าทั้งหมด | แสดงรายการสินค้าทั้งหมด พร้อมแบ่งหน้า (pagination) ครั้งละ 10 รายการ |
| เพิ่ม/แก้ไขสินค้า | Upsert สินค้าตาม product_id พร้อมให้ยืนยันก่อนเขียนทับข้อมูลเดิม |
| ตัดสต็อก | ลดจำนวนสินค้า พร้อมเตือนเมื่อสต็อกเหลือน้อย (≤ 5 ชิ้น) และป้องกันไม่ให้สต็อกติดลบ |
| รายงานสรุป | จำนวนชนิดสินค้า, จำนวนหน่วยรวม, มูลค่ารวม, จำนวนสินค้าใกล้หมด |
| ค้นหาสินค้า | ค้นหาแบบ partial match จากชื่อหรือหมวดหมู่ พร้อมแบ่งหน้า |

ทุก action ที่แก้ไขข้อมูล (เพิ่ม/แก้/ตัดสต็อก/ค้นหา) จะถูกบันทึกลงตาราง `action_logs` โดยอัตโนมัติผ่าน `Logger`

## โครงสร้างโปรเจกต์

```
.
├── inventory_app.py          # แอปหลัก (เมนู interactive)
├── product.py                 # Entity: Product
├── product_repository.py      # Repository: เข้าถึงข้อมูลสินค้า
├── database_connection.py     # Singleton: เชื่อมต่อ SQLite
├── logger.py                  # Singleton: บันทึก action log
├── validator.py                # ตรวจสอบ input จากผู้ใช้
├── schema.sql                  # โครงสร้างตาราง (products, stock_movements, action_logs)
├── seed_data.sql                # ข้อมูลตั้งต้นสำหรับทดสอบ/demo
├── app_v1.py                   # เวอร์ชันต้นแบบเดิม (เก็บไว้อ้างอิง ไม่ใช้งานจริงแล้ว)
├── conftest.py                  # pytest fixtures ส่วนกลาง (reset singleton, isolated db)
├── test_*.py                    # unit test แยกตามคลาส
├── definition_of_done.md        # เกณฑ์คุณภาพกลาง ใช้กับทุก ticket
├── dod_per_feature.md           # เกณฑ์ Definition of Done เฉพาะแต่ละ feature/ticket
├── risk_register_app_v1_emoji.md # บันทึกความเสี่ยงของเวอร์ชันต้นแบบและแผนรับมือ
└── .github/workflows/tests.yml   # CI: รัน pytest อัตโนมัติทุก push/PR เข้า main และ develop
```

## การติดตั้งและเริ่มใช้งาน

ต้องมี Python 3.10 ขึ้นไป

```bash
# ติดตั้ง dependency
pip install -r requirements.txt

# รันโปรแกรม (สร้างฐานข้อมูล inventory.db จาก schema.sql ให้อัตโนมัติในการรันครั้งแรก)
python inventory_app.py
```

หากต้องการข้อมูลสินค้าตัวอย่างไว้ทดสอบ ให้รัน seed data เพิ่มหลังจากมีไฟล์ `inventory.db` แล้ว:

```bash
sqlite3 inventory.db < seed_data.sql
```

## การรันเทสต์

โปรเจกต์นี้มี unit test ครอบคลุมทุกคลาส (98 เทสต์ ผ่านทั้งหมด ณ ปัจจุบัน)

```bash
python -m pytest -v
```

CI (`.github/workflows/tests.yml`) รัน pytest อัตโนมัติทุกครั้งที่ push หรือเปิด/อัปเดต Pull Request เข้า branch `main` และ `develop` บน Python 3.10, 3.11 และ 3.12

## Merge & Release Policy

- Merge เข้า `develop`: ต้องผ่าน pytest บน CI/CD และ QA approve Pull Request
- Merge เข้า `main`: ต้องผ่าน CI/CD บน `develop` ล่าสุด และ Tech Lead ตรวจสอบ/approve Pull Request

รายละเอียดเกณฑ์คุณภาพทั้งหมดดูที่ [`definition_of_done.md`](./definition_of_done.md) และเกณฑ์เฉพาะแต่ละ feature ที่ [`dod_per_feature.md`](./dod_per_feature.md)

## ฐานข้อมูล

ใช้ SQLite มี 3 ตารางหลัก (นิยามใน [`schema.sql`](./schema.sql)):

- **products** — ข้อมูลสินค้า (product_id, name, category, quantity, price)
- **stock_movements** — ประวัติการเปลี่ยนแปลงสต็อกทุกครั้ง
- **action_logs** — ประวัติ action สำคัญของระบบ (เพิ่ม/แก้/ตัดสต็อก/ค้นหา)
