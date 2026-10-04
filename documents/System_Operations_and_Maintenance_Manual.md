# SYSTEM OPERATIONS & MAINTENANCE MANUAL (คู่มือปฏิบัติการและการบำรุงรักษาระบบ)
**Academic Reference:** ISO/IEC 14764:2006 (Software Engineering — Software Life Cycle Processes — Maintenance), ISO/IEC 12207 (Operation Process, Maintenance Process, Configuration Management)
**Course Context:** ENGSE225 Software Evolution & Maintenance — คู่มือส่งมอบคู่กับ [`Project_Completion_Certificate.md`](./Project_Completion_Certificate.md)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **Document ID** | **OMM-V2.0-01** |
| **ระบบ** | Inventory Management System **Version 2.0.1** (build `73e7cfd`) |
| **ผู้ใช้เอกสาร** | ผู้ดูแลระบบ (Operator), ทีมบำรุงรักษา (Maintainer: Developer, QA, Tech Lead), PM |
| **สถานะ** | ฉบับร่าง 1.0 — 2026-10-05 |

คำสั่งทุกคำสั่งในคู่มือนี้ทดลองรันแล้วบน clone ใหม่ของ repo เมื่อ 2026-10-05 (ดู [`Smoke_And_Regression_Test_Report.md`](./Smoke_And_Regression_Test_Report.md)) ให้รันจาก **โฟลเดอร์ root ของโปรเจกต์** เสมอ

---

## ส่วนที่ 1: ภาพรวมระบบ (System Overview)

ระบบจัดการสต็อกสินค้าแบบ Console เขียนด้วย Python 3.10+ ใช้ฐานข้อมูล SQLite และใช้เพียง standard library ตอนรันโปรแกรม

### 1.1 องค์ประกอบ (Components)

| องค์ประกอบ | ไฟล์ | หน้าที่ |
| :--- | :--- | :--- |
| UI (เมนู 1–8) | `inventory_app.py` | รับคำสั่ง แสดงผล แบ่งหน้า 10 รายการ บันทึก log ทุก action |
| Input validation | `validator.py` | วนถามจนได้ค่าที่ถูกต้อง, ยืนยันก่อนเขียนทับ |
| Entity | `product.py` | ตรวจค่าใน constructor, `is_low_stock()` |
| Data access | `product_repository.py` | SQL ทั้งหมด, กันบาร์โค้ดซ้ำ, `updateStock` แบบ transaction |
| Database connection | `database_connection.py` | Singleton, รัน `schema.sql` ทุกครั้งที่เชื่อมต่อ |
| Audit log | `logger.py` | Singleton, บันทึกลงตาราง `action_logs` |
| CSV export | `csv_report_exporter.py`, `atomic_file_writer.py` | ส่งออกสินค้าใกล้หมด (UTF-8 BOM) แบบ atomic write |
| Schema / ข้อมูลตั้งต้น | `schema.sql`, `seed_data.sql` | โครงสร้างตาราง, สินค้าตัวอย่าง 3 รายการ |
| ต้นแบบเดิม (Legacy) | `app_v1.py` | เก็บไว้อ้างอิงเท่านั้น ห้ามใช้งานจริง (ดูส่วนที่ 6.7) |

### 1.2 ข้อมูลที่ระบบสร้าง (Data Stores)

| ไฟล์ / ตาราง | ตำแหน่ง | เนื้อหา | ความสำคัญ |
| :--- | :--- | :--- | :--- |
| `inventory.db` | โฟลเดอร์ที่สั่งรันโปรแกรม (current working directory) | ฐานข้อมูลทั้งหมด | **สูง — ต้องสำรองข้อมูล** ไม่ถูก commit ขึ้น git (`.gitignore`) |
| ตาราง `products` | ใน `inventory.db` | สินค้า, จำนวน, ราคา, บาร์โค้ด, Reorder Point, `created_at`/`updated_at` | ข้อมูลหลัก |
| ตาราง `stock_movements` | ใน `inventory.db` | ประวัติการตัดสต็อก (`change_qty`, `reason`) | ใช้ตรวจสอบย้อนหลัง |
| ตาราง `action_logs` | ใน `inventory.db` | ประวัติ action ของผู้ใช้ทุกครั้ง | Audit trail |
| ไฟล์ CSV | ตามชื่อที่ผู้ใช้กรอกในเมนู 7 (ค่าเริ่มต้น `low_stock_report.csv`) | รายการสินค้าใกล้หมด | สร้างใหม่ได้ทุกเมื่อ |

---

## ส่วนที่ 2: การติดตั้งและตั้งค่า (Installation & Configuration)

| งาน | คำสั่ง |
| :--- | :--- |
| ติดตั้งอัตโนมัติ (Windows) | `scripts\setup.cmd -Seed` |
| ติดตั้งอัตโนมัติ (Linux / macOS / Git Bash) | `bash scripts/setup.sh --seed` |
| ติดตั้งใหม่ทั้งหมด (ลบ `.venv` และ `inventory.db`) | เพิ่ม `-Clean` / `--clean` — **ข้อมูลหายถาวร สำรองก่อนเสมอ** |
| ติดตั้งแบบเร็ว ไม่ติดตั้งเครื่องมือทดสอบ | เพิ่ม `-SkipTests` / `--skip-tests` |

รายละเอียดสคริปต์อยู่ที่ [`Clean_Environment_Installation_Test.md`](./Clean_Environment_Installation_Test.md) และขั้นตอนทำทีละขั้นด้วยตนเองอยู่ใน [`README.md`](../README.md) หัวข้อ "การติดตั้งและเริ่มใช้งาน"

**ค่าที่ตั้งไว้ในโค้ด (ไม่มีไฟล์ config แยก):**

| ค่า | ตำแหน่ง | ค่าปัจจุบัน |
| :--- | :--- | :--- |
| ชื่อไฟล์ฐานข้อมูล | `DatabaseConnection.getInstance(db_name)` ค่าเริ่มต้น | `inventory.db` |
| เกณฑ์ใกล้หมดของรายงานสรุป (เมนู 4) | `LOW_STOCK_THRESHOLD` ใน `product_repository.py` | 5 |
| Reorder Point เริ่มต้น | `DEFAULT_REORDER_POINT` ใน `product.py` และ DEFAULT ใน `schema.sql` | 5 |
| จำนวนรายการต่อหน้า | `self.page_size` ใน `InventoryApp` | 10 |
| ค่าสูงสุดของจำนวน/Reorder Point | `SQLITE_MAX_INTEGER` ใน `product.py` | 2⁶³ − 1 |

---

## ส่วนที่ 3: การปฏิบัติงาน (Operations)

### 3.1 เริ่มและหยุดระบบ

```bash
.venv\Scripts\python.exe inventory_app.py     # Windows (หลังติดตั้งด้วยสคริปต์)
.venv/bin/python inventory_app.py             # Linux / macOS
python inventory_app.py                       # ใช้ Python ของเครื่องโดยตรงก็ได้ (ไม่ต้องติดตั้ง package)
```

หยุดระบบด้วยเมนู `8` ทุกครั้ง ไม่ควรปิดหน้าต่างระหว่างบันทึกข้อมูล (ทุก action commit ทันทีหลังทำเสร็จ)

### 3.2 เมนูและ Action ที่ถูกบันทึก

| เมนู | งาน | Action ใน `action_logs` |
| :---: | :--- | :--- |
| 1 | แสดงสินค้าทั้งหมด (แบ่งหน้า `n`/`p`/`q`) | — |
| 2 | เพิ่ม/แก้ไขสินค้า (ยืนยัน `y`/`n` เมื่อรหัสซ้ำ) | `ADD_PRODUCT` / `UPDATE_PRODUCT` |
| 3 | ตัดสต็อก (ต้องมากกว่า 0 และไม่เกินคงเหลือ) | `CUT_STOCK` |
| 4 | รายงานสรุป | — |
| 5 | ค้นหาตามชื่อหรือหมวดหมู่ | `SEARCH_PRODUCT` |
| 6 | แจ้งเตือนสินค้าใกล้หมด (`quantity <= reorder_point`) | `LOW_STOCK_ALERT_VIEWED` (เมื่อมีรายการ) |
| 7 | Export CSV สินค้าใกล้หมด | `EXPORT_LOW_STOCK_CSV` (เมื่อสำเร็จ) |
| 8 | ออกจากโปรแกรม | — |

### 3.3 ตรวจสุขภาพระบบ (Health Check)

| ตรวจอะไร | คำสั่ง | ผลที่ถูกต้อง |
| :--- | :--- | :--- |
| ความสมบูรณ์ของไฟล์ฐานข้อมูล | `python -c "import sqlite3; print(sqlite3.connect('inventory.db').execute('PRAGMA integrity_check').fetchone()[0])"` | `ok` |
| ฟังก์ชันค้นหา/แบ่งหน้า | `python inventory_app.py --selftest` | "ผ่านเกณฑ์ … ครบถ้วน 100%" และลบข้อมูลทดสอบเอง |
| ทั้งระบบ (ต้องติดตั้งเครื่องมือทดสอบ) | `python -m pytest --cov` | ผ่านทั้งหมด, Coverage ≥ 90% |

### 3.4 ดู Audit Log และประวัติสต็อก

```bash
# action ล่าสุด 20 รายการ
python -c "import sqlite3; [print(r) for r in sqlite3.connect('inventory.db').execute('SELECT created_at, action, detail FROM action_logs ORDER BY log_id DESC LIMIT 20')]"

# การตัดสต็อกล่าสุด 20 รายการ
python -c "import sqlite3; [print(r) for r in sqlite3.connect('inventory.db').execute('SELECT created_at, product_id, change_qty, reason FROM stock_movements ORDER BY movement_id DESC LIMIT 20')]"
```

เวลาใน `created_at` เป็น UTC (`datetime('now')` ของ SQLite) เวลาประเทศไทยต้องบวก 7 ชั่วโมง

### 3.5 สำรองและกู้คืนข้อมูล (Backup & Restore)

**สำรองข้อมูล** — ใช้ backup API ของ SQLite ได้แม้โปรแกรมเปิดอยู่ ไฟล์ปลายทางชื่อ `inventory_backup_YYYY-MM-DD.db`

```bash
python -c "import sqlite3, datetime; src=sqlite3.connect('inventory.db'); dst=sqlite3.connect('inventory_backup_' + datetime.date.today().isoformat() + '.db'); src.backup(dst); dst.close(); src.close()"
```

**กู้คืนข้อมูล** — ปิดโปรแกรมก่อน (เมนู 8) แล้วคัดลอกไฟล์สำรองทับ `inventory.db` จากนั้นตรวจด้วย `PRAGMA integrity_check`

```bash
copy inventory_backup_2026-10-05.db inventory.db     # Windows (Command Prompt)
cp inventory_backup_2026-10-05.db inventory.db       # Linux / macOS / Git Bash / PowerShell
```

ไฟล์ `*.db` ทั้งหมดอยู่ใน `.gitignore` ไฟล์สำรองจึงไม่ถูก commit ต้องเก็บไว้นอก repo เอง

### 3.6 งานประจำ (Routine Tasks)

| ความถี่ | งาน | ผู้รับผิดชอบ |
| :--- | :--- | :--- |
| ทุกวันหลังปิดร้าน | สำรอง `inventory.db` (ส่วนที่ 3.5) | Operator |
| ทุกวัน | ดูเมนู 6 และ Export CSV ส่งฝ่ายจัดซื้อ | ฝ่ายจัดซื้อ |
| ทุกสัปดาห์ | `PRAGMA integrity_check` และ `--selftest` | Operator |
| ทุกสัปดาห์ | ทดลองกู้คืนไฟล์สำรองลงโฟลเดอร์ทดสอบ | Operator |
| ทุกครั้งที่มีการเปลี่ยนโค้ด | Regression เต็มชุด (ส่วนที่ 6.5) | QA |

---

## ส่วนที่ 4: การแก้ไขปัญหา (Troubleshooting)

| อาการ | สาเหตุ | วิธีแก้ |
| :--- | :--- | :--- |
| ไม่เห็นข้อมูลเดิม / สินค้าหายหมด | รันโปรแกรมจากโฟลเดอร์อื่น จึงเปิด `inventory.db` คนละไฟล์ | `cd` ไปที่ root ของโปรเจกต์แล้วรันใหม่ |
| `sqlite3.OperationalError: no such table: products` | ใช้คำสั่งตรวจ/seed ก่อนสร้างตาราง หรือรันจากโฟลเดอร์อื่น | สร้างฐานข้อมูลก่อน (เปิดโปรแกรมหนึ่งครั้ง หรือดู README ขั้นที่ 2) |
| `UnicodeDecodeError` ตอนอ่าน `schema.sql`/`seed_data.sql` | เปิดไฟล์โดยไม่ระบุ encoding บน Windows ภาษาไทย (cp874) | ใส่ `encoding='utf-8'` ตามคำสั่งในคู่มือนี้ |
| PowerShell ไม่ยอมรัน `setup.ps1` (Execution Policy) | นโยบายเครื่องห้ามรันสคริปต์ | ใช้ `scripts\setup.cmd` ซึ่ง Bypass เฉพาะครั้งนั้น |
| `bash: $'\r': command not found` เมื่อรัน `setup.sh` | ไฟล์ถูกแปลงเป็น CRLF | ตรวจว่ามี `.gitattributes` แล้ว `git checkout -- scripts/setup.sh` ใหม่ |
| `python -m venv` ล้มเหลวบน Debian/Ubuntu | ไม่มีแพ็กเกจ venv | `sudo apt install python3-venv` |
| ภาษาไทยในไฟล์ CSV เพี้ยนเมื่อเปิดใน Excel | ไฟล์ CSV ที่สร้างจากเวอร์ชันก่อน 2.0.1 ไม่มี BOM | Export ใหม่จากเมนู 7 (เวอร์ชัน 2.0.1 เขียน UTF-8 BOM แล้ว) |
| Barcode แสดงเป็น `8.85E+12` ใน Excel | Excel ตีความคอลัมน์เป็นตัวเลข (FB-04) | จัดรูปแบบคอลัมน์เป็น Text ใน Excel หรือใช้ Data → From Text/CSV แล้วเลือกชนิดข้อความ |
| Export ขึ้น "ข้อผิดพลาด: ไม่สามารถบันทึกไฟล์ …" | โฟลเดอร์ปลายทางไม่มีอยู่ ชื่อไฟล์มีอักขระต้องห้าม หรือไม่มีสิทธิ์เขียน | ใช้ชื่อไฟล์ในโฟลเดอร์ที่มีอยู่จริง ไฟล์เดิมไม่ถูกแตะ |
| "ค่ามากเกินไป กรุณากรอกใหม่" | จำนวนเกิน 2⁶³ − 1 | กรอกค่าที่ถูกต้อง (มักเกิดจากพิมพ์ผิด) |
| `PRAGMA integrity_check` ไม่ได้ `ok` | ไฟล์ฐานข้อมูลเสียหาย | หยุดใช้งาน กู้คืนจากไฟล์สำรองล่าสุด (ส่วนที่ 3.5) แล้วเปิด BUG-xxx |

---

## ส่วนที่ 5: บทบาทและความรับผิดชอบ (Roles & Responsibilities)

| บทบาท | ความรับผิดชอบด้านปฏิบัติการและบำรุงรักษา |
| :--- | :--- |
| Operator / ผู้ใช้หลัก | ใช้งานประจำวัน, สำรองข้อมูล, รายงานปัญหา |
| Developer | วิเคราะห์และแก้ไขตาม CR/BUG, เขียนเทสต์ก่อนแก้ |
| QA | ตรวจ PR เข้า `develop`, รัน Regression และ UAT ซ้ำ |
| Tech Lead | ตรวจและอนุมัติ release จาก `develop` เข้า `main` |
| PM / PO | รับคำขอ, จัดลำดับ Future Backlog, ปิด ticket |
| Sponsor | อนุมัติ CR ที่กระทบขอบเขต และลงนามยอมรับผล |

---

## ส่วนที่ 6: การบำรุงรักษาตาม ISO/IEC 14764 (Maintenance Process)

### 6.1 ประเภทงานบำรุงรักษาและตัวอย่างจากระบบนี้

| ประเภท (ISO/IEC 14764) | ความหมาย | ตัวอย่างในโครงการ | Commit prefix |
| :--- | :--- | :--- | :--- |
| **Corrective** | แก้ข้อผิดพลาดที่พบแล้ว | BUG-102 ถึง BUG-108 | `fix:` |
| **Adaptive** | ปรับให้ทำงานในสภาพแวดล้อมที่เปลี่ยน | pin เวอร์ชัน dependency (`9b9497a`), สคริปต์ติดตั้ง (`73e7cfd`) | `build:` |
| **Perfective** | เพิ่มหรือปรับปรุงความสามารถ | CR-01, CR-02, FB-01 ถึง FB-05 (Version 3.0) | `feat:` |
| **Preventive** | แก้ปัญหาแฝงก่อนเกิดขึ้นจริง | Atomic File Write, rollback ของ `updateStock`, Flake8/Bandit = 0 | `fix:` / `style:` / `test:` |

คำขอเร่งด่วนให้ระบุเป็น **Emergency Change Request** โดยคงประเภทเดิมไว้ เช่น CR-02 เป็น "Perfective (Expedited)"

### 6.2 ขั้นตอนการบำรุงรักษา (Maintenance Workflow)

| กิจกรรม (ISO/IEC 14764) | สิ่งที่ทำในโครงการนี้ | ผลลัพธ์ / เอกสาร |
| :--- | :--- | :--- |
| **Process Implementation** | ใช้คู่มือนี้, `CLAUDE.md`, DoD และ CI เป็นกรอบการทำงาน | คู่มือนี้, [`definition_of_done.md`](./definition_of_done.md) |
| **Problem & Modification Analysis** | รับคำขอ ออก ID จัดประเภท วิเคราะห์ผลกระทบทุกชั้น (UI, Validator, Product, Repository SQL, `schema.sql`, Logger, CSV, เทสต์ที่ใช้ลำดับ input นั้น) | `CR-xx` → `Change_Request_And_Impact_Analysis_Report_CRxx.md`, `BUG-xxx` → Change Request Log ใน README |
| **Modification Implementation** | แตก branch จาก `develop` (`feature/*`, `bugfix/*`) เขียนเทสต์ให้ fail ก่อน → แก้ → Refactor ทำเฉพาะในขอบเขตที่อนุมัติ | commit ตาม prefix ในส่วนที่ 6.1 พร้อม ID |
| **Maintenance Review / Acceptance** | PR เข้า `develop` (CI เขียว + QA approve) → PR เข้า `main` (Tech Lead approve) → UAT ถ้ากระทบผู้ใช้ | PR, รายงาน UAT, Sign-off |
| **Migration** | เปลี่ยนสภาพแวดล้อมหรือโครงสร้างข้อมูล (ดูส่วนที่ 6.6) | สคริปต์ migration + เอกสาร CR |
| **Software Retirement** | ปลดระบบหรือโมดูลเก่าออก (ดูส่วนที่ 6.7) | บันทึกใน CHANGELOG หมวด Removed |

### 6.3 การรับคำขอและระบบ ID

| ID | ใช้กับ | บันทึกที่ |
| :--- | :--- | :--- |
| `CR-xx` | คำขอเปลี่ยนแปลงที่ได้รับอนุมัติ | รายงาน CR ใน `documents/` และ Change Request Log ใน `README.md` |
| `BUG-xxx` | ข้อผิดพลาด (ถัดไปคือ **BUG-109**) | Change Request Log ใน `README.md`, `CHANGELOG.md` หมวด Fixed |
| `FB-xx` | คำขอใหม่ที่ยกไปเวอร์ชันถัดไป (ถัดไปคือ **FB-06**) | Future Backlog ใน [`Scope_Freeze_Sign_off_Agreement.md`](./Scope_Freeze_Sign_off_Agreement.md) ส่วนที่ 3.3 |

เกณฑ์แยก Defect กับ New Scope ใช้ตาม [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md) ส่วนที่ 3.1: ขัดกับข้อกำหนดหรือโปรแกรมแครช = Defect, ทำงานตามข้อกำหนดแต่ต้องการความสามารถใหม่ = New Scope

### 6.4 Configuration Management และการออกเวอร์ชัน

- **Branch:** `feature/*`, `bugfix/*` → `develop` → `main`
- **Commit:** prefix `feat:`, `fix:`, `test:`, `style:`, `docs:`, `build:` พร้อม CR/BUG ID
- **เวอร์ชัน:** บันทึกใน [`CHANGELOG.md`](../CHANGELOG.md) แบบ Keep a Changelog (Added / Changed / Removed / Fixed) งานที่ยังไม่ออกเวอร์ชันอยู่ใต้ `[Unreleased]` ตอนนี้ repo ยังไม่มี git tag แนะนำให้สร้าง tag `v2.0.1` ที่ `73e7cfd`
- **Line ending:** ไฟล์ต้นฉบับเป็น CRLF (`core.autocrlf=true`), `*.sh` เป็น LF ตาม `.gitattributes`
- **ข้อห้าม:** ไม่ใส่ `# noqa`, `# nosec`, `# pragma: no cover` และไม่ใช้ `assert` ในโค้ดโปรแกรม (ใช้ `_verify()` ในบล็อก self-test)

### 6.5 Quality Gates ก่อน merge ทุกครั้ง

| เกณฑ์ | คำสั่ง | ต้องได้ |
| :--- | :--- | :--- |
| Regression + Coverage | `python -m pytest --cov --cov-report=term-missing` | ผ่านทั้งหมด, ≥ 90% |
| Lint | `python -m flake8 .` | 0 |
| Security | `python -m bandit -c pyproject.toml -r .` | No issues |
| Smoke | `python inventory_app.py --selftest` และเปิดเมนูจริงอย่างน้อย 1 รอบ (DoD ข้อ 2) | ไม่แครช |
| CI | GitHub Actions (`pytest` matrix 3.10/3.11/3.12 + `lint`) | เขียวทุก job |

### 6.6 ข้อควรระวังด้านเทคนิคและหนี้ทางเทคนิค (Technical Debt)

| ประเด็น | ผลกระทบ | แนวทางบำรุงรักษา | ประเภท |
| :--- | :--- | :--- | :--- |
| ไม่มีระบบ Migration: `schema.sql` ใช้ `CREATE … IF NOT EXISTS` จึงไม่แก้ตารางที่มีอยู่แล้ว | เพิ่มคอลัมน์/constraint ใหม่จะไม่มีผลกับ `inventory.db` เดิม | ทุก CR ที่แก้ schema ต้องมีสคริปต์ `ALTER TABLE` แยก, คอลัมน์ใหม่ต้องมีค่า DEFAULT (แบบเดียวกับ CR-01) และทดสอบกับฐานข้อมูลเก่า | Adaptive |
| `requirements-dev.txt` pin เฉพาะ flake8/bandit ไม่ pin dependency ย่อย (เช่น pyflakes ได้ 4.0.2 ขณะรายงานสแกนเดิมใช้ 4.0.1) | ผล lint อาจเปลี่ยนโดยไม่มีการแก้โค้ด | พิจารณาใช้ไฟล์ constraints หรือ lock file | Adaptive |
| "ใกล้หมด" มี 2 ความหมาย: รายงานสรุปใช้ `LOW_STOCK_THRESHOLD = 5` แต่ Alerts/CSV ใช้ `reorder_point` ของแต่ละสินค้า | ผู้ใช้อาจสับสน (UAT-11) | ห้ามรวมโดยไม่มีการตัดสินใจของ Sponsor (FB-03) | Perfective |
| ทดสอบสคริปต์ติดตั้งเฉพาะ Windows และ Git Bash | Linux/macOS จริงยังไม่ยืนยัน | เพิ่ม CI job รัน `bash scripts/setup.sh --clean --seed` บน `ubuntu-latest` | Preventive |
| บรรทัดที่ยังไม่มีเทสต์ 10 บรรทัด (เช่น `atomic_file_writer.py` 55–56, `inventory_app.py` 134–136) | ความเสี่ยงต่ำ ส่วนใหญ่เป็นเส้นทาง error | เพิ่มเทสต์เมื่อมีการแก้ไขโมดูลนั้น | Preventive |
| ตารางแสดงผลเลื่อนเมื่อชื่อเป็นภาษาไทย | ความสวยงามเท่านั้น | FB-05 | Perfective |

### 6.7 Software Retirement

`app_v1.py` เป็นต้นแบบรุ่นแรกที่เก็บข้อมูลใน `data.json` ผ่าน global dict ถูกเก็บไว้เพื่อเปรียบเทียบกับ Risk Register เท่านั้น **ห้าม import ในโค้ดใหม่และห้าม refactor** หากจะปลดออกในอนาคต ต้องลบพร้อม `test_app_v1.py` และ integration test ที่เรียก entry point ของไฟล์นี้ แล้วบันทึกในหมวด Removed ของ CHANGELOG และปรับ Risk Register ที่อ้างถึง

---

## ส่วนที่ 7: เอกสารอ้างอิง (References)

| เอกสาร | ใช้เมื่อ |
| :--- | :--- |
| [`README.md`](../README.md) | ติดตั้งทีละขั้น, ภาพรวมสถาปัตยกรรม, Change Request Log |
| [`CHANGELOG.md`](../CHANGELOG.md) | ประวัติการเปลี่ยนแปลงทุกเวอร์ชัน |
| [`CLAUDE.md`](../CLAUDE.md) | แนวทางการแก้โค้ดและกระบวนการ ISO/IEC 12207 / 14764 |
| [`definition_of_done.md`](./definition_of_done.md), [`dod_per_feature.md`](./dod_per_feature.md) | เกณฑ์ "เสร็จ" ของงาน |
| [`risk_register_app_v1_emoji.md`](./risk_register_app_v1_emoji.md) | ความเสี่ยงและมาตรการ |
| [`Change_Request_And_Impact_Analysis_Report.md`](./Change_Request_And_Impact_Analysis_Report.md), [`…_CR02.md`](./Change_Request_And_Impact_Analysis_Report_CR02.md) | แม่แบบรายงาน CR |
| [`Scope_Freeze_Sign_off_Agreement.md`](./Scope_Freeze_Sign_off_Agreement.md) | Future Backlog |
| [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md) | สถานการณ์ UAT สำหรับ re-test |
| [`Technical_KPI_Report.md`](./Technical_KPI_Report.md) | ตัวชี้วัดคุณภาพปัจจุบัน |

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 2026-10-05 | ฉบับร่างแรก ครอบคลุมการติดตั้ง ปฏิบัติการ แก้ไขปัญหา และกระบวนการบำรุงรักษาตาม ISO/IEC 14764 |
