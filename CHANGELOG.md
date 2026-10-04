# Changelog — Maintenance History Log

บันทึกประวัติการเปลี่ยนแปลงทั้งหมดของ Inventory Management System ตั้งแต่ต้นแบบ `app_v1.py` จนถึง Version 2.0 ใช้รูปแบบ [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) แบ่งหมวด **Added / Changed / Removed / Fixed** และระบุประเภทงานตาม ISO/IEC 14764 (Corrective / Adaptive / Perfective / Preventive) พร้อม commit หรือ Pull Request (PR) อ้างอิงทุกรายการ

> **หมายเหตุเรื่องเลขเวอร์ชัน:** repo ยังไม่มี git tag เลขเวอร์ชันในไฟล์นี้กำหนดย้อนหลังตาม milestone ของโครงการ โดย Version 1.x คือช่วงต้นแบบ และ Version 2.0 คือระบบที่ refactor เป็น OOP + SQLite ซึ่งถูกล็อกขอบเขตตาม [`documents/Scope_Freeze_Sign_off_Agreement.md`](./documents/Scope_Freeze_Sign_off_Agreement.md) ช่วง Sprint ใช้รูปแบบ pre-release (`2.0.0-sprint.1`, `2.0.0-sprint.2`)

## [Unreleased]

### Changed
- สัญญา Scope Freeze SFA-01 ลงนามจำลองครบ 5 บทบาท (ฉบับ 1.0) Baseline ที่ลงนามคือ `f6d7e77` (Version 2.0.1) พร้อมอัปเดตสถานะคุณภาพเป็น 158 เทสต์, Coverage 98.12% และผล UAT รอบ 2
- รายงาน UAT ลงนามรับรองผลจำลองครบ 4 บทบาท (ฉบับ 1.0) ผลการรับรอง: ยอมรับ บน build `f6d7e77` (Version 2.0.1)

## [2.0.1] - 2026-10-04 — UAT Fixes (Baseline ที่ลงนามใน SFA-01)

แก้ UAT Defects ทั้ง 5 รายการจาก UAT รอบแรก (`3a5a207`) และ Re-test รอบ 2 ผ่านทุกสถานการณ์ที่อยู่ในขอบเขต (16/16) ดูรายละเอียดใน [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) ส่วนที่ 6

### Added
- รายงาน User Acceptance Testing [`documents/User_Acceptance_Testing_Report.md`](./documents/User_Acceptance_Testing_Report.md) ทดสอบ 17 สถานการณ์ธุรกิจกับโปรแกรมจริง จำแนก UAT Defect (BUG-104 ถึง BUG-108) แยกจาก New Scope (FB-01 ถึง FB-05) พร้อมผล Re-test รอบ 2 และหลักฐานดิบ [`reports/uat_evidence.txt`](./reports/uat_evidence.txt), [`reports/uat_evidence_r2.txt`](./reports/uat_evidence_r2.txt)
- ไฟล์ `CHANGELOG.md` (Maintenance History Log) ฉบับนี้
- ค่าคงที่ใน `product.py`: `SQLITE_MAX_INTEGER` (2⁶³−1 ขอบบนของคอลัมน์ INTEGER ใน SQLite) และ `DEFAULT_REORDER_POINT` (5 ตรงกับ DEFAULT ใน `schema.sql`)
- พารามิเตอร์ `default` ของ `Validator.inputNonNegativeInt(prompt, default=None)` คืนค่านี้เมื่อผู้ใช้กด Enter โดยไม่กรอกอะไร
- เทสต์ใหม่ 13 ตัวสำหรับ BUG-104 ถึง BUG-108 (เขียนให้ fail ก่อนแก้ แล้วจึงแก้ให้ผ่าน) รวมเป็น 158 เทสต์ Coverage 98.12%

### Changed
- สัญญา Scope Freeze: บันทึก FB-01 ถึง FB-05 จากผล UAT ลงตาราง Future Backlog สำหรับ Version 3.0
- ไฟล์ CSV จากเมนู 7 เขียนเป็น UTF-8 **พร้อม BOM** (`utf-8-sig`) แทน UTF-8 ไม่มี BOM โปรแกรมที่อ่านไฟล์นี้ควรเปิดด้วย `encoding="utf-8-sig"` (เทสต์ใน `test_csv_report_exporter.py` และ `test_integration.py` ปรับตามแล้ว)
- `ProductRepository.updateStock()` ไม่รับ `qty == 0` (raise `ValueError`) เพราะไม่ใช่การเคลื่อนไหวของสต็อก
- `Product` ปฏิเสธ `quantity` และ `reorder_point` ที่เกิน `SQLITE_MAX_INTEGER`

### Fixed
- **BUG-104** (UAT-09, Critical) — *Corrective*: Export CSV ไปยังโฟลเดอร์ที่ไม่มีอยู่ หรือชื่อไฟล์มีอักขระต้องห้าม ทำให้โปรแกรมหยุดทำงานด้วย `FileNotFoundError`/`OSError` → `InventoryApp.exportLowStockCsv()` จับ `OSError` แจ้ง "ข้อผิดพลาด: ไม่สามารถบันทึกไฟล์ … ได้" แล้วกลับเมนู และไม่บันทึก log `EXPORT_LOW_STOCK_CSV` เมื่อ Export ไม่สำเร็จ (`3a5a207`)
- **BUG-105** (UAT-14, Critical) — *Corrective*: กรอกจำนวนหรือ Reorder Point เกินช่วง INTEGER ของ SQLite ทำให้โปรแกรมหยุดทำงานด้วย `OverflowError` → `Validator.inputNonNegativeInt()` แจ้ง "ค่ามากเกินไป กรุณากรอกใหม่" และถามใหม่ ส่วน `Product` raise `ValueError` เป็นชั้นป้องกันที่สอง (`3a5a207`)
- **BUG-106** (UAT-08, Major) — *Corrective*: ชื่อสินค้าภาษาไทยในไฟล์ CSV อ่านไม่ได้เมื่อเปิดใน Excel (Excel อ่านไฟล์ที่ไม่มี BOM ด้วย code page 874) → `CsvReportExporter` เขียนด้วย `utf-8-sig` (`3a5a207`)
- **BUG-107** (UAT-02, Minor) — *Corrective*: กด Enter ที่ "Reorder Point [ค่าเริ่มต้น 5]" แล้วถูกถามซ้ำแทนที่จะใช้ค่า 5 → เมนู 2 ส่ง `default=DEFAULT_REORDER_POINT` และข้อความ prompt ดึงค่าจากค่าคงที่เดียวกัน (`3a5a207`)
- **BUG-108** (UAT-06, Minor) — *Corrective*: ตัดสต็อก 0 ชิ้นแล้วระบบแจ้ง "ตัดสต็อกสำเร็จ" พร้อมบันทึก movement `0` และ log `qty=-0` → `InventoryApp.cutStock()` แจ้ง "ข้อผิดพลาด: จำนวนที่ตัดต้องมากกว่า 0" และ `updateStock()` ไม่รับ `qty == 0` (`3a5a207`)

## [2.0.0] - 2026-10-04 — Version 2.0 Baseline (Scope Freeze SFA-01)

ช่วง Hardening & Maintenance ก่อนล็อกขอบเขต (PR #32, #33 และ commit บน `main`) โค้ดโปรแกรม ณ จุดนี้คือ commit `c76c7b7` ซึ่งเป็น Baseline ในร่างแรกของ SFA-01 ส่วน Baseline ที่ลงนามจริงคือ 2.0.1

### Added
- `AtomicFileWriter` (`atomic_file_writer.py`) เขียนไฟล์ชั่วคราวในโฟลเดอร์เดียวกัน, fsync แล้ว `os.replace` เมื่อเขียนพังกลางทางไฟล์เดิมจะไม่เสียหาย — *Preventive* ลดความเสี่ยง "data.json เสียหาย" ใน Risk Register (`4e0a5b7`, PR #32)
- CI job `lint` รัน Flake8 และ Bandit คู่กับ pytest พร้อม config `.flake8` (max-line-length 120) และ `[tool.bandit]` ใน `pyproject.toml` — *Preventive* (`6358919`)
- `test_integration.py` Integration Test แบบ end-to-end 12 เคสผ่านเมนูและ entry point จริง และ Coverage Gate ≥ 90% ใน CI — *Preventive* (`a7b0c73`)
- รายงานใน `reports/`: Code Quality & Security Scan Report, Integration Test & Coverage Report พร้อม raw output และภาพหลักฐาน (`6358919`, `a7b0c73`)
- `requirements-dev.txt` รวม dependency ของเทสต์และ pin เวอร์ชัน flake8 7.4.1, bandit 1.9.4 ให้ตรงกับ CI — *Adaptive* (`9b9497a`)
- `CLAUDE.md` แนวทางการทำงานกับ codebase ตามกระบวนการ ISO/IEC 12207 และ ISO/IEC 14764 (`2b8a277`)
- เทสต์ใหม่ 7 ตัว: BUG-103 (5 ตัว), หัวข้อเมนูค้นหา, rollback ของ `updateStock` รวมเป็น 145 เทสต์ Coverage 98.04% (`d347d8e`, `0a33c8b`, `d6da33b`)
- เอกสารจำลองสัญญา Scope Freeze Sign-off Agreement (SFA-01) สำหรับสัปดาห์ที่ 12 พร้อมกลยุทธ์ Future Backlog สำหรับ Version 3.0 (`7e42f17`)

### Changed
- `app_v1.save()` และ `CsvReportExporter` เขียนไฟล์ผ่าน `AtomicFileWriter` แทน `open()` ตรงๆ (`4e0a5b7`)
- บล็อก self-test ใน `__main__` ใช้ `_verify()` แทน `assert` เพื่อให้ตรวจได้แม้รันด้วย `python -O` และ teardown ใน `conftest.py` กลืนเฉพาะ `sqlite3.Error` (`6358919`)
- `requirements.txt` กำหนดช่วงเวอร์ชันบน `pytest>=8.0,<10`, `pytest-cov>=7.0,<8` — *Adaptive* (`9b9497a`)
- `app_v1.py` ระบุใน docstring ว่าเป็นโมดูลอ้างอิง (Legacy) ห้าม import ในโค้ดใหม่ (`ef62bed`)
- เทสต์ `showMenu()` ตรวจครบ 8 เมนู (เดิมตรวจแค่ 1–6) และย้ายเทสต์ BUG-102 ขึ้นไปไว้ก่อนบล็อก `__main__` (`0a33c8b`, `d6da33b`)
- ย้ายเอกสารโครงการ (รายงาน CR-01/CR-02, DoD, DoD per feature, Risk Register) เข้าโฟลเดอร์ `documents/` และแก้การอ้างอิงทุกจุด (`c76c7b7`)
- README: อัปเดตจำนวนเทสต์, ผังโครงสร้าง, CI ทั้งสอง job และ Change Request Log; รายงาน CR-02 ระบุการเขียนผ่าน `AtomicFileWriter` (`31471c5`, `516a5ef`)

### Removed
- เครื่องหมาย `[cite: …]` ที่หลงเหลือ 51 จุดในรายงาน CR-01 (`31471c5`)

### Fixed
- **BUG-103** กรอกราคา `nan` แล้วโปรแกรมพังด้วย `IntegrityError` และราคา `inf` ถูกบันทึกลงฐานข้อมูลได้ — `Validator` ถามใหม่และ `Product` ปฏิเสธค่าที่ไม่จำกัด — *Corrective* (`d347d8e`)
- หัวข้อหน้าค้นหาแสดง `[3]` ทั้งที่เป็นเมนู 5 — *Corrective* (`0a33c8b`)
- `updateStock()` rollback ทั้ง `products` และ `stock_movements` เมื่อการบันทึกประวัติล้มเหลว ไม่ให้ยอดคงเหลือเปลี่ยนโดยไม่มีประวัติ — *Preventive* (`d6da33b`)
- ผล Flake8 จาก 410 → 0 และ Bandit จาก 196 → 0 findings (whitespace, unused import, ชื่อตัวแปร `l`, บรรทัดยาว, `assert` ในโค้ดจริง, `except Exception: pass`) — *Preventive* (`6358919`)

## [2.0.0-sprint.2] - 2026-09-14 — Sprint 2: CR-01, CR-02, BUG-102

### Added
- **CR-01 Barcode & Reorder Point Alert** — *Perfective*: ฟิลด์ `barcode` และ `reorder_point` ใน `Product` และตาราง `products` (มีค่า default เพื่อ Backward Compatibility), เมธอด `Product.is_low_stock()`, `ProductRepository.getLowStockAlerts()` และเมนู 6 แจ้งเตือนสินค้าใกล้หมด (`75af8d2`, PR #23)
- **CR-02 Export Low Stock Report เป็น CSV** (Emergency Change Request) — *Perfective (Expedited)*: คลาส `CsvReportExporter` แบบ Static Method แยกอิสระจาก UI/Repository พร้อม unit test และ Terminal Demo (`ebd4f0b`, `44f4038`, PR #25)
- เมนู 7 Export รายงานสินค้าใกล้หมดเป็น CSV เชื่อมเข้ากับ UI และบันทึก Action `EXPORT_LOW_STOCK_CSV` (`29d9b59`, PR #29)
- Partial UNIQUE INDEX `idx_products_barcode_unique` บน `barcode WHERE barcode != ''` เป็นชั้นป้องกันระดับฐานข้อมูล (`29d9b59`, PR #29)
- Action `LOW_STOCK_ALERT_VIEWED` ใน `action_logs` เมื่อเปิดเมนูแจ้งเตือน (PR #23)
- รายงาน Change Request & Impact Analysis ของ CR-01 และ CR-02 ตาม ISO/IEC 14764 (`8245989`, `7152454`)
- Terminal Demo ในทุกไฟล์ `test_*.py` (รัน `python test_xxx.py` แล้วแสดงตาราง DoD ภาษาไทย) (`2a71135`)

### Changed
- เมนูหลักขยายจาก 6 เป็น 8 ข้อ เมนูออกจากโปรแกรมย้ายจาก 6 → 7 (CR-01) → 8 (เชื่อมเมนู CSV) (PR #23, PR #29)
- เมนู 2 ถาม Barcode และ Reorder Point เพิ่ม และ `upsertProduct()` บันทึกทั้งสองฟิลด์ (PR #23)
- ปรับเทสต์เดิมให้ตรงกับลำดับคำถามใหม่ของเมนู 2 และฟิลด์ใหม่ใน `to_dict()` (`82e4def`, `e52b377`)
- README เพิ่มรายละเอียด CR-01/CR-02 และ Change Request Log (`81e968d`, `44f4038`)

### Removed
- ยกเลิก (Revert) การ merge CR-01 รอบแรก (PR #20) ผ่าน PR #21/#22 ก่อนนำกลับมา implement ใหม่ให้ครบใน PR #23 (`c8fc769`)

### Fixed
- **BUG-102** — *Corrective*:
  - สินค้าคนละรหัสใช้ Barcode ซ้ำกันได้ → `upsertProduct()` ปฏิเสธ Barcode ที่สินค้าอื่นใช้แล้ว (`f5778d3`, PR #27)
  - คำเตือนหลังตัดสต็อกใช้เกณฑ์ตายตัว `quantity < LOW_STOCK_THRESHOLD` แทน Reorder Point ของสินค้าแต่ละชิ้น → แก้ให้ใช้ `is_low_stock()` (`29d9b59`, PR #29)
  - ฟังก์ชัน CSV Export มีแต่ยังไม่ถูกเชื่อมเข้าเมนู (`29d9b59`, PR #29)

## [2.0.0-sprint.1] - 2026-09-06 — Sprint 1: Refactor เป็น OOP + SQLite

### Added
- `schema.sql` ตาราง `products`, `stock_movements`, `action_logs` พร้อม CHECK constraint ห้ามค่าติดลบ, FOREIGN KEY, index และ trigger `updated_at` (`0c95308`)
- คลาส `Product` (SCRUM-8) ตรวจสอบค่าใน constructor (`825c414`, PR #11)
- คลาส `Validator` (SCRUM-9) วนถามจนได้ค่าที่ถูกต้อง และยืนยันก่อนเขียนทับ (`dca1ed6`, PR #12)
- คลาส `Logger` แบบ Singleton (SCRUM-10) บันทึกลงตาราง `action_logs` (`6653490`, `2b60c1a`, PR #13)
- คลาส `DatabaseConnection` แบบ Singleton (SCRUM-6) (`6653490`, PR #13) และ `ProductRepository` (SCRUM-7) รวม SQL ทั้งหมดไว้ที่เดียว (`b705c74`, PR #14)
- `InventoryApp` เมนู Console ใหม่ (SCRUM-11) และการค้นหาพร้อมแบ่งหน้า 10 รายการต่อหน้า (SCRUM-12) (`5948d4d`, `ca90e79`, `759f528`, PR #15, PR #16)
- Unit test แยกตามคลาส, `conftest.py` แยกฐานข้อมูลทดสอบ, `test_app_v1.py` และ CI GitHub Actions รัน pytest บน Python 3.10–3.12 (`2c8710d`, `8d14fee`)
- `seed_data.sql` ข้อมูลตัวอย่าง 3 รายการ (`4708d19`)
- `definition_of_done.md` และ `dod_per_feature.md` (`8a81205`, `31ac00e`)
- README ฉบับใหม่ของระบบที่ refactor (`2f6a593`, `0de467f`)

### Changed
- `python inventory_app.py` เข้าเมนูใช้งานจริงเป็นค่าเริ่มต้น และย้าย self-test ไปไว้หลัง flag `--selftest` (เดิมต้องใช้ `--interactive`) (`a50fd00`)

### Removed
- ไฟล์ต้นแบบรุ่นที่สองและเอกสารเดิม ได้แก่ `app_v2.py`, `test_app.py`, `README.md` เดิม, `DoD.md`, `README_TESTER.md`, `.gitignore` เดิม เพื่อเริ่ม refactor ใหม่ โดยเก็บ `app_v1.py` ไว้อ้างอิง (`4ab3e66`, `e441c15`, `9f6d25c`, `b53aac8`, `74c13f4`, `32f55b0`, PR #5–#10)
- ไฟล์ที่ไม่ควรอยู่ใน repo: `__pycache__/` และ `inventory.db` (`39475bf`, `6a57284`)

### Fixed
- ย้าย `tests.yml` ไปไว้ที่ `.github/workflows/` เพื่อให้ GitHub Actions รันได้จริง (`8d14fee`)
- แก้ conflict ของ `inventory_app.py` ระหว่าง `main` กับ `develop` (`5084235`)

## [1.1.0] - 2026-07-20 — ต้นแบบรุ่นที่สอง (app_v2) และ Risk Register

### Added
- `app_v2.py` ต้นแบบรุ่นที่สอง และชุดทดสอบ `test_app.py` (`fe64f8c`, `d1991a5`, PR #1–#3)
- `README_TESTER.md`, `DoD.md` และ `.gitignore` (`138bfe2`, `19980cc`, `36214fc`)
- Risk Register ของ `app_v1.py` (`25a21c6`, `f615d73`, PR #4)

### Changed
- `app_v2.py` ใช้ named logger แยกจาก root logger เพื่อไม่ให้ชนกันตอนรันเทสต์ (`2bb8369`)
- Risk Register เปลี่ยนจากฉบับสี (`risk_register_app_v1_colored.md`) เป็นฉบับ Emoji (`risk_register_app_v1_emoji.md`) (`f615d73`)

### Removed
- ไฟล์ที่ไม่ควรอยู่ใน repo: `__pycache__/app_v2.cpython-312.pyc`, `inventory.db`, `inventory.log` (`36214fc`)
- `risk_register_app_v1_colored.md` (แทนที่ด้วยฉบับ Emoji) (`f615d73`)

### Fixed
- `test_app.py` raise `AssertionError` เมื่อเทสต์ไม่ผ่าน (เดิมไม่ทำให้การทดสอบล้ม) (`2bb8369`)

## [1.0.0] - 2026-07-12 — ต้นแบบแรก

### Added
- `app_v1.py` ระบบสต็อกสินค้าแบบ Console เก็บข้อมูลใน `data.json` ผ่าน global dict (`69a9ad4`)

[Unreleased]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/f6d7e77...main
[2.0.1]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/c76c7b7...f6d7e77
[2.0.0]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/90b6569...c76c7b7
[2.0.0-sprint.2]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/71af63b...90b6569
[2.0.0-sprint.1]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/4c80866...71af63b
[1.1.0]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/compare/69a9ad4...4c80866
[1.0.0]: https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM/commit/69a9ad4
