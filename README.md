# ENGSE225 — Inventory System

ระบบจัดการสต็อกสินค้า (Inventory Management System) พัฒนาเป็นส่วนหนึ่งของวิชา ENGSE225 โดยเริ่มจากโปรแกรมต้นแบบเวอร์ชันแรก (`app_v1.py`) แล้ว refactor ใหม่ทั้งหมดให้เป็นสถาปัตยกรรมเชิงวัตถุที่แยกชั้นความรับผิดชอบชัดเจน ตาม Repository Pattern และ Singleton Pattern

## ทำไมต้อง Refactor

เวอร์ชันแรก (`app_v1.py`) เก็บข้อมูลในไฟล์ `data.json` ตรงๆ ผ่าน global dict ไม่มีการตรวจสอบข้อมูลนำเข้า และไม่มี unit test เลย ซึ่งเสี่ยงต่อข้อมูลเสียหายและแก้ไขยาก รายละเอียดความเสี่ยงทั้งหมดที่พบและแผนรับมือ ดูได้ที่ [`documents/risk_register_app_v1_emoji.md`](./documents/risk_register_app_v1_emoji.md)

เวอร์ชันปัจจุบัน (`inventory_app.py` และคลาสสนับสนุน) แก้ไขปัญหาเหล่านั้นด้วยการย้ายไปใช้ฐานข้อมูล SQLite, แยก logic การเข้าถึงข้อมูลออกจาก business logic (Repository Pattern), บังคับให้มี database connection เดียวทั้งระบบ (Singleton Pattern), และเพิ่ม validation ทุกจุดที่รับ input จากผู้ใช้

## สถาปัตยกรรม

```
InventoryApp   ─┬─ uses ─▶ Validator          (ตรวจสอบ input จากผู้ใช้)
                ├─ uses ─▶ ProductRepository   (เข้าถึงข้อมูลสินค้า)
                └─ uses ─▶ Logger              (บันทึก action log, Singleton)

ProductRepository ─┬─ creates and manages ─▶ Product            (entity)
                    └─ uses (Singleton)     ─▶ DatabaseConnection (เชื่อมต่อ SQLite เดียวทั้งระบบ)

CsvReportExporter ─┬─ uses ─▶ Product (List)   (แยกอิสระจาก UI/Repository — Static Method, ไม่มี State)
                   └─ uses ─▶ AtomicFileWriter (เขียนไฟล์ชั่วคราว → fsync → os.replace)
```

- **Repository Pattern** — `ProductRepository` เป็นจุดเดียวที่คุยกับฐานข้อมูล ทำให้ `InventoryApp` ไม่ผูกติดกับวิธีเก็บข้อมูล และทดสอบแยกส่วนได้ง่าย
- **Singleton Pattern** — `DatabaseConnection` และ `Logger` มี instance เดียวทั้งโปรแกรม ป้องกันการเปิด connection ซ้ำซ้อน
- **Single Responsibility (CsvReportExporter)** — แยกการ Export CSV ออกจาก UI/Repository เดิมโดยสิ้นเชิง ออกแบบเป็น Static Method ไร้ State ทดสอบแยกได้อิสระ

## ฟีเจอร์หลัก

| เมนู | คำอธิบาย |
|---|---|
| แสดงสินค้าทั้งหมด | แสดงรายการสินค้าทั้งหมด พร้อมแบ่งหน้า (pagination) ครั้งละ 10 รายการ |
| เพิ่ม/แก้ไขสินค้า | Upsert สินค้าตาม product_id พร้อมให้ยืนยันก่อนเขียนทับข้อมูลเดิม รองรับกรอก Barcode และ Reorder Point |
| ตัดสต็อก | ลดจำนวนสินค้า พร้อมเตือนเมื่อสต็อกเหลือน้อย (≤ Reorder Point ของสินค้าชิ้นนั้น) และป้องกันไม่ให้สต็อกติดลบ |
| รายงานสรุป | จำนวนชนิดสินค้า, จำนวนหน่วยรวม, มูลค่ารวม, จำนวนสินค้าใกล้หมด |
| ค้นหาสินค้า | ค้นหาแบบ partial match จากชื่อหรือหมวดหมู่ พร้อมแบ่งหน้า |
| แจ้งเตือนสินค้าใกล้หมด (Low Stock Alerts) | **[CR-01]** ดึงรายชื่อสินค้าที่ `quantity <= reorder_point` เพื่อแจ้งเตือนให้สั่งซื้อเพิ่มโดยอัตโนมัติ |
| **Export รายงานสินค้าใกล้หมดเป็น CSV** | **[CR-02]** ส่งออกรายชื่อสินค้าใกล้หมดเป็นไฟล์ `.csv` (Header: ProductID, ProductName, Barcode, Quantity, ReorderPoint, Price) สำหรับใช้สั่งซื้อ/ส่งต่อทีมจัดซื้อ |

ทุก action ที่แก้ไขข้อมูลหรือดึงรายงาน (เพิ่ม/แก้/ตัดสต็อก/ค้นหา/ดู Low Stock Alerts/Export CSV) จะถูกบันทึกลงตาราง `action_logs` โดยอัตโนมัติผ่าน `Logger`

## โครงสร้างโปรเจกต์

```
.
├── inventory_app.py          # แอปหลัก (เมนู interactive)
├── product.py                 # Entity: Product (มี barcode, reorder_point, is_low_stock())
├── product_repository.py      # Repository: เข้าถึงข้อมูลสินค้า (มี getLowStockAlerts())
├── csv_report_exporter.py     # [CR-02] Export สินค้าสต็อกต่ำเป็นไฟล์ CSV (Static Method, แยกอิสระ)
├── atomic_file_writer.py      # เขียนไฟล์แบบ atomic (temp file → fsync → os.replace) ใช้กับ CSV และ data.json
├── database_connection.py     # Singleton: เชื่อมต่อ SQLite
├── logger.py                  # Singleton: บันทึก action log
├── validator.py                # ตรวจสอบ input จากผู้ใช้
├── schema.sql                  # โครงสร้างตาราง (products, stock_movements, action_logs)
├── seed_data.sql                # ข้อมูลตั้งต้นสำหรับทดสอบ/demo
├── app_v1.py                   # เวอร์ชันต้นแบบเดิม (เก็บไว้อ้างอิง ไม่ใช้งานจริงแล้ว)
├── conftest.py                  # pytest fixtures ส่วนกลาง (reset singleton, isolated db)
├── test_*.py                    # unit test แยกตามคลาส (แต่ละไฟล์รันเป็น Terminal Demo ได้ด้วย python test_*.py)
├── test_integration.py          # integration test แบบ end-to-end ผ่าน InventoryApp.run() และ entry point จริง
├── requirements.txt             # dependency สำหรับรันเทสต์ (pytest, pytest-cov)
├── requirements-dev.txt         # requirements.txt + flake8, bandit (เวอร์ชันเดียวกับ CI)
├── pyproject.toml / .flake8     # config ของ pytest, coverage (gate 90%), bandit และ flake8
├── CHANGELOG.md                 # Maintenance History Log (Added / Changed / Removed / Fixed)
├── scripts/                     # สคริปต์ติดตั้งอัตโนมัติ setup.cmd / setup.ps1 (Windows), setup.sh (Linux/macOS/Git Bash)
├── .gitattributes               # บังคับ line ending ของสคริปต์ (*.sh = LF, *.ps1/*.cmd = CRLF)
├── documents/                   # เอกสารโครงการ
│   ├── definition_of_done.md        # เกณฑ์คุณภาพกลาง ใช้กับทุก ticket
│   ├── dod_per_feature.md           # เกณฑ์ Definition of Done เฉพาะแต่ละ feature/ticket
│   ├── risk_register_app_v1_emoji.md # บันทึกความเสี่ยงของเวอร์ชันต้นแบบและแผนรับมือ
│   ├── Change_Request_And_Impact_Analysis_Report.md # เอกสารวิเคราะห์ผลกระทบ CR-01 ตาม ISO/IEC 14764
│   ├── Change_Request_And_Impact_Analysis_Report_CR02.md # เอกสารวิเคราะห์ผลกระทบ CR-02 ตาม ISO/IEC 14764
│   ├── Scope_Freeze_Sign_off_Agreement.md # เอกสารจำลองสัญญาล็อกขอบเขต Version 2.0 (สัปดาห์ที่ 12) + Future Backlog v3.0
│   ├── User_Acceptance_Testing_Report.md # ผล UAT 17 สถานการณ์ธุรกิจ + แยก Defect กับ New Scope + Re-test รอบ 2
│   └── Clean_Environment_Installation_Test.md # คู่มือสคริปต์ติดตั้งอัตโนมัติ + ผลทดสอบติดตั้งบนเครื่องสะอาด
├── reports/                    # รายงานผลสแกน Flake8/Bandit, Integration Test & Coverage และหลักฐานการรัน
└── .github/workflows/tests.yml   # CI: pytest + coverage gate และ lint (Flake8/Bandit) ทุก push/PR เข้า main และ develop
```

## การติดตั้งและเริ่มใช้งาน

### ติดตั้งอัตโนมัติด้วยสคริปต์ (แนะนำ)

สคริปต์ชุดนี้ทำทุกขั้นด้านล่างให้ในคำสั่งเดียว: ตรวจ Python, สร้าง `.venv`, ติดตั้ง dependency, สร้างฐานข้อมูล, ใส่ seed data แล้วตรวจด้วย smoke test, self-test, pytest, Flake8 และ Bandit พร้อมสรุปผล PASS/FAIL ทีละขั้น

```bash
# Windows (Command Prompt หรือ PowerShell)
scripts\setup.cmd -Seed

# Linux / macOS / Git Bash
bash scripts/setup.sh --seed
```

| ตัวเลือก (Windows / bash) | ผล |
|---|---|
| `-Seed` / `--seed` | ใส่สินค้าตัวอย่าง 3 รายการ |
| `-Clean` / `--clean` | ลบ `.venv` และ `inventory.db` เดิมก่อนติดตั้ง (ข้อมูลหายถาวร) ใช้ทดสอบ Clean Environment Installation |
| `-SkipTests` / `--skip-tests` | ติดตั้งเร็วขึ้น ไม่ติดตั้งและไม่รัน pytest / Flake8 / Bandit |

หลังติดตั้ง เปิดโปรแกรมด้วย `.venv\Scripts\python.exe inventory_app.py` (Windows) หรือ `.venv/bin/python inventory_app.py` (Linux/macOS) รายละเอียดสคริปต์และผลทดสอบอยู่ที่ [`documents/Clean_Environment_Installation_Test.md`](./documents/Clean_Environment_Installation_Test.md)

ถ้าต้องการทำทีละขั้นเอง ดูหัวข้อย่อยต่อไปนี้

### 1. สิ่งที่ต้องมี

- Python 3.10 ขึ้นไป
- ตัวโปรแกรมใช้แค่ standard library ของ Python (รวมโมดูล `sqlite3`) **ไม่ต้องติดตั้ง package เพิ่มเพื่อรันโปรแกรม**
- ไม่จำเป็นต้องมีโปรแกรม `sqlite3` (command-line) ในเครื่อง ทุกขั้นตอนด้านล่างทำผ่าน Python ได้

ถ้าจะรันเทสต์หรือสแกนโค้ด ให้ติดตั้งเครื่องมือก่อน:

```bash
pip install -r requirements.txt       # pytest, pytest-cov (สำหรับรันเทสต์)
pip install -r requirements-dev.txt   # requirements.txt + flake8, bandit เวอร์ชันเดียวกับ CI
```

### 2. สร้างฐานข้อมูล (`schema.sql`)

> **สำคัญ:** รันทุกคำสั่งจาก **โฟลเดอร์ root ของโปรเจกต์** (โฟลเดอร์ที่มี `inventory_app.py`) เพราะโปรแกรมเปิดไฟล์ `inventory.db` ในโฟลเดอร์ที่สั่งรัน (current working directory) ถ้ารันจากโฟลเดอร์อื่นจะได้ฐานข้อมูลคนละไฟล์

**วิธี A — ให้โปรแกรมสร้างให้อัตโนมัติ (แนะนำ)**

```bash
python inventory_app.py
```

ทุกครั้งที่โปรแกรมเชื่อมต่อฐานข้อมูล จะรัน `schema.sql` ให้เอง ถ้ายังไม่มี `inventory.db` จะสร้างไฟล์ใหม่พร้อมตาราง `products`, `stock_movements`, `action_logs` และ index/trigger ครบ จากนั้นเลือกเมนู `8` เพื่อออกได้เลย

**วิธี B — สร้างเองโดยไม่ต้องเปิดเมนู**

```bash
python -c "import sqlite3; c=sqlite3.connect('inventory.db'); c.executescript(open('schema.sql', encoding='utf-8').read()); c.commit(); c.close()"
```

คำสั่งนี้ใช้ได้ทั้ง PowerShell, Command Prompt และ bash ต้องมี `encoding='utf-8'` เสมอ เพราะ `schema.sql` มีคอมเมนต์ภาษาไทย ถ้าไม่ระบุ Windows ภาษาไทยจะอ่านไฟล์ผิดและเกิด `UnicodeDecodeError`

`schema.sql` ใช้ `CREATE ... IF NOT EXISTS` ทั้งหมด จึงรันซ้ำได้โดยข้อมูลเดิมไม่หาย

### 3. ใส่ข้อมูลตัวอย่าง (`seed_data.sql`) — ไม่บังคับ

ต้องสร้างฐานข้อมูลในขั้นที่ 2 ก่อน (seed ต้องมีตาราง `products` อยู่แล้ว)

```bash
python -c "import sqlite3; c=sqlite3.connect('inventory.db'); c.executescript(open('seed_data.sql', encoding='utf-8').read()); c.commit(); c.close()"
```

ถ้าในเครื่องมีโปรแกรม `sqlite3` อยู่แล้ว ใช้คำสั่งนี้แทนได้ (ใช้ได้ทุก shell รวม PowerShell ซึ่งไม่รองรับ `<` แบบ `sqlite3 inventory.db < seed_data.sql`):

```bash
sqlite3 inventory.db ".read seed_data.sql"
```

ผลลัพธ์คือสินค้าตัวอย่าง 3 รายการ:

| รหัส | ชื่อ | หมวดหมู่ | คงเหลือ | ราคา |
|---|---|---|---|---|
| 101 | Mama Noodles | Food | 50 | 6.00 |
| 102 | Lactasoy Milk | Drink | 20 | 12.00 |
| 103 | Singha Water | Drink | 100 | 10.00 |

- seed ไม่ได้กำหนดบาร์โค้ดและ Reorder Point จึงได้ค่า default จาก schema (บาร์โค้ดว่าง, Reorder Point = 5)
- seed ใช้ `ON CONFLICT DO UPDATE` รันซ้ำแล้วไม่เกิดแถวซ้ำ แต่ชื่อ, หมวดหมู่, จำนวน และราคาของสินค้า 101–103 จะถูกเขียนกลับเป็นค่าตั้งต้น

### 4. ตรวจสอบและเริ่มใช้งาน

```bash
# นับจำนวนสินค้าในฐานข้อมูล (ควรได้ 3 หลังรัน seed)
python -c "import sqlite3; print(sqlite3.connect('inventory.db').execute('SELECT COUNT(*) FROM products').fetchone()[0])"

# เปิดโปรแกรม แล้วเลือกเมนู 1 เพื่อดูสินค้าทั้งหมด
python inventory_app.py
```

ถ้าคำสั่งนับจำนวนขึ้น `sqlite3.OperationalError: no such table: products` แปลว่ายังไม่ได้สร้างตาราง (ข้ามขั้นที่ 2) หรือรันจากโฟลเดอร์อื่น ให้กลับไปทำขั้นที่ 2 จากโฟลเดอร์ root ของโปรเจกต์

### 5. ล้างฐานข้อมูลแล้วเริ่มใหม่

ลบไฟล์ `inventory.db` (ข้อมูลทั้งหมดจะหายถาวร) แล้วทำขั้นที่ 2–3 ใหม่

```bash
# PowerShell
Remove-Item inventory.db

# bash / macOS / Linux
rm inventory.db
```

`inventory.db` อยู่ใน `.gitignore` จึงไม่ถูก commit ขึ้น repo แต่ละเครื่องมีฐานข้อมูลของตัวเอง

## การรันเทสต์

โปรเจกต์นี้มี unit test ครอบคลุมทุกคลาส และ integration test แบบ end-to-end (รวม 158 เทสต์ ผ่านทั้งหมด ณ ปัจจุบัน coverage 98%)

```bash
python -m pytest -v

# วัด coverage (ล้มเหลวถ้าต่ำกว่า 90% ตามที่ตั้งไว้ใน pyproject.toml)
python -m pytest --cov --cov-report=term-missing

# ตรวจคุณภาพโค้ดและความปลอดภัย (ต้องติดตั้ง requirements-dev.txt ก่อน)
python -m flake8 .
python -m bandit -c pyproject.toml -r .
```

แต่ละไฟล์ `test_*.py` ยังรันแบบ Terminal Demo ได้โดยตรง (แสดงผลตรวจสอบ Definition of Done แบบอ่านง่ายเป็นภาษาไทย) เช่น

```bash
python test_csv_report_exporter.py
```

CI (`.github/workflows/tests.yml`) รันอัตโนมัติทุกครั้งที่ push หรือเปิด/อัปเดต Pull Request เข้า branch `main` และ `develop` โดยมี 2 job:

- **pytest** — รัน pytest พร้อมวัด coverage บน Python 3.10, 3.11 และ 3.12 ถ้า coverage ต่ำกว่า 90% ถือว่าไม่ผ่าน
- **lint** — รัน Flake8 และ Bandit ต้องไม่พบปัญหาเลย

## Merge & Release Policy

- Merge เข้า `develop`: ต้องผ่าน CI ครบทั้ง job pytest และ lint และ QA approve Pull Request
- Merge เข้า `main`: ต้องผ่าน CI/CD บน `develop` ล่าสุด และ Tech Lead ตรวจสอบ/approve Pull Request

รายละเอียดเกณฑ์คุณภาพทั้งหมดดูที่ [`documents/definition_of_done.md`](./documents/definition_of_done.md) และเกณฑ์เฉพาะแต่ละ feature ที่ [`documents/dod_per_feature.md`](./documents/dod_per_feature.md)

## ฐานข้อมูล

ใช้ SQLite มี 3 ตารางหลัก (นิยามใน [`schema.sql`](./schema.sql)):

- **products** — ข้อมูลสินค้า (product_id, name, category, quantity, price, barcode, reorder_point)
- **stock_movements** — ประวัติการเปลี่ยนแปลงสต็อกทุกครั้ง
- **action_logs** — ประวัติ action สำคัญของระบบ (เพิ่ม/แก้/ตัดสต็อก/ค้นหา)

## Change Request Log

| CR ID | ชื่อ | สถานะ | เอกสารประกอบ |
|---|---|---|---|
| CR-01 | Barcode & Reorder Point Alert | ✅ Merged เข้า develop | [`Change_Request_And_Impact_Analysis_Report.md`](./documents/Change_Request_And_Impact_Analysis_Report.md) |
| CR-02 | Export Low Stock Report เป็น CSV (Emergency Change Request) | ✅ Merged เข้า develop (PR #25) | [`Change_Request_And_Impact_Analysis_Report_CR02.md`](./documents/Change_Request_And_Impact_Analysis_Report_CR02.md), `csv_report_exporter.py`, `test_csv_report_exporter.py` |
| BUG-102 | Barcode ซ้ำ + Low Stock Alert อิง threshold ผิด + เมนู CSV Export ยังไม่ถูกเชื่อมเข้า UI | ✅ Merged เข้า develop (PR #27, #29) | `schema.sql`, `inventory_app.py`, `test_inventory_app.py` |
| BUG-103 | กรอกราคา `nan` แล้วโปรแกรมพัง (IntegrityError) และราคา `inf` ถูกบันทึกลงฐานข้อมูลได้ (Corrective) | ✅ แก้ไขแล้ว ผ่านการทดสอบ (Merged เข้า main และ develop) | `validator.py`, `product.py`, `test_validator.py`, `test_product.py`, `test_inventory_app.py` |
| BUG-104 | Export CSV ไปยังโฟลเดอร์ที่ไม่มีอยู่/ชื่อไฟล์มีอักขระต้องห้าม ทำให้โปรแกรมพัง (UAT-09, Critical) | ✅ แก้ไขแล้ว ผ่าน UAT Re-test รอบ 2 | [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) |
| BUG-105 | กรอกจำนวน/Reorder Point เกินช่วง INTEGER ของ SQLite ทำให้โปรแกรมพัง (UAT-14, Critical) | ✅ แก้ไขแล้ว ผ่าน UAT Re-test รอบ 2 | [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) |
| BUG-106 | CSV ไม่มี UTF-8 BOM ชื่อภาษาไทยอ่านไม่ได้ใน Excel (UAT-08, Major) | ✅ แก้ไขแล้ว ผ่าน UAT Re-test รอบ 2 | [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) |
| BUG-107 | กด Enter ที่ Reorder Point ไม่ใช้ค่าเริ่มต้น 5 ตามข้อความบนหน้าจอ (UAT-02, Minor) | ✅ แก้ไขแล้ว ผ่าน UAT Re-test รอบ 2 | [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) |
| BUG-108 | ตัดสต็อก 0 ชิ้นแล้วแจ้งสำเร็จและบันทึก movement ว่าง (UAT-06, Minor) | ✅ แก้ไขแล้ว ผ่าน UAT Re-test รอบ 2 | [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) |
