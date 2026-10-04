# SMOKE TEST & FULL REGRESSION TEST REPORT — Fresh Environment
**Academic Reference:** ISO/IEC 12207 (Verification Process), ISO/IEC 14764:2006 (Software Maintenance — Regression testing หลังการเปลี่ยนแปลง)
**Course Context:** ENGSE225 Software Evolution & Maintenance — ยืนยันว่า build ที่ส่งมอบตาม [`Project_Completion_Certificate.md`](./Project_Completion_Certificate.md) ติดตั้งและทำงานได้บนสภาพแวดล้อมใหม่

> ผลทั้งหมดในเอกสารนี้มาจากการรันจริงเมื่อ 2026-10-05 หลักฐานดิบอยู่ที่ [`reports/regression_evidence_2026-10-05.txt`](../reports/regression_evidence_2026-10-05.txt)

---

## ส่วนที่ 1: สภาพแวดล้อมการทดสอบ (Test Environment)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **Test Run ID** | **REG-2026-10-05** |
| **Build** | `main` @ `80c6d22` (โค้ดโปรแกรมตรงกับ build ที่ส่งมอบ `73e7cfd` และ build ที่ผ่าน UAT `3a5a207`) |
| **วิธีเตรียมสภาพแวดล้อม** | `git clone` จาก GitHub ลงโฟลเดอร์ว่าง ไม่มี `.venv` และ `inventory.db` ใดๆ จากเครื่องผู้พัฒนา แล้วติดตั้งด้วย `scripts\setup.cmd -Clean -Seed` |
| **ระบบปฏิบัติการ** | Windows 11 (Windows PowerShell 5.1, Git Bash) |
| **Python** | CPython 3.13.14 ใน `.venv` ที่สร้างใหม่ |
| **เครื่องมือ (ติดตั้งจาก `requirements-dev.txt`)** | pytest 9.1.1, pytest-cov 7.1.0 (coverage 7.16.2), flake8 7.4.1 (pycodestyle 2.15.0, pyflakes 4.0.2), bandit 1.9.4 |

---

## ส่วนที่ 2: การติดตั้งบนสภาพแวดล้อมใหม่ (Clean Install)

`scripts\setup.cmd -Clean -Seed` ผ่าน **12/12 ขั้น** ใช้เวลา **32.4 วินาที** exit code **0**

| ขั้น | ผล |
| :--- | :---: |
| ตรวจ Python ≥ 3.10, ล้างสภาพแวดล้อม, สร้าง `.venv`, ติดตั้ง dependency | ✅ |
| สร้างฐานข้อมูลจาก `schema.sql`, ใส่ seed data, ตรวจโครงสร้างฐานข้อมูล | ✅ |
| Smoke test เบื้องต้น (เปิดโปรแกรมแล้วออก), `--selftest` | ✅ |
| PyTest + Coverage, Flake8, Bandit | ✅ |

---

## ส่วนที่ 3: Smoke Test — แอปพลิเคชันเปิดได้และไม่แครช

เปิด `inventory_app.py` **หนึ่งครั้ง** แล้วใช้งานครบทุกเมนู 1–8 ต่อเนื่องกัน บนฐานข้อมูลที่สร้างใหม่พร้อม seed data 3 รายการ

| เมนู | การทำงานที่ทดสอบ | ผลที่ต้องเห็น | ผล |
| :---: | :--- | :--- | :---: |
| 1 | แสดงสินค้าทั้งหมด | "จากทั้งหมด 3 รายการ" | ✅ |
| 2 | เพิ่มสินค้าใหม่ S1 (จำนวน 6) และกด Enter ที่ Reorder Point | "บันทึกสำเร็จ" และ reorder point = 5 | ✅ |
| 3 | ตัดสต็อก S1 ออก 2 ชิ้น (เหลือ 4 ≤ 5) | "!!! คำเตือน …" และ movement `-2` | ✅ |
| 4 | รายงานสรุป | "มูลค่าสินค้ารวม" | ✅ |
| 5 | ค้นหา "Drink" | "จากทั้งหมด 2 รายการ" | ✅ |
| 6 | แจ้งเตือนสินค้าใกล้หมด | "รวม 1 รายการที่ต้องสั่งซื้อเพิ่ม" | ✅ |
| 7 | Export CSV เป็น `smoke_report.csv` | "Export สำเร็จ: 1 รายการ" ไฟล์มี UTF-8 BOM และแถวข้อมูล S1 | ✅ |
| 8 | ออกจากโปรแกรม | "ขอบคุณที่ใช้บริการ" | ✅ |

**ผล: ✅ PASS** — exit code 0, stderr ว่าง (ไม่มี Traceback), ข้อมูลในฐานข้อมูลและไฟล์ CSV ถูกต้อง, `action_logs` บันทึก `ADD_PRODUCT`, `CUT_STOCK`, `SEARCH_PRODUCT`, `LOW_STOCK_ALERT_VIEWED`, `EXPORT_LOW_STOCK_CSV` ครบอย่างละ 1 ครั้ง

---

## ส่วนที่ 4: Full Regression Test

| ชุดทดสอบ | ผลลัพธ์ | เกณฑ์ | ผล |
| :--- | :--- | :--- | :---: |
| PyTest (Unit + Integration) | **158 passed**, 0 failed, 0 error ใน 2.55 วินาที | ผ่านทั้งหมด | ✅ |
| Code Coverage | **98.12%** (532 statements, missed 10) | ≥ 90% | ✅ |
| Flake8 | **0** findings | 0 | ✅ |
| Bandit | **No issues identified** (สแกน 3,351 บรรทัด, `#nosec` = 0) | 0 | ✅ |
| `python inventory_app.py --selftest` | ผ่าน และลบข้อมูลทดสอบเรียบร้อย | ผ่าน | ✅ |
| Terminal Demo (`python test_*.py`) | 9 ไฟล์ Pass Rate 100%, `test_integration.py` ไม่มีบล็อก demo (exit 0) | exit 0 ทุกไฟล์ | ✅ |

### 4.1 จำนวนเทสต์แยกตามไฟล์

| ไฟล์ | เทสต์ | ไฟล์ | เทสต์ |
| :--- | :---: | :--- | :---: |
| `test_app_v1.py` | 17 | `test_inventory_app.py` | 30 |
| `test_atomic_file_writer.py` | 5 | `test_logger.py` | 6 |
| `test_csv_report_exporter.py` | 4 | `test_product.py` | 21 |
| `test_database_connection.py` | 19 | `test_product_repository.py` | 26 |
| `test_integration.py` | 12 | `test_validator.py` | 18 |
| **รวม** | | | **158** |

### 4.2 Coverage แยกตามโมดูล

| โมดูล | Statements | Missed | Coverage | บรรทัดที่ยังไม่ถูกทดสอบ |
| :--- | :---: | :---: | :---: | :--- |
| `app_v1.py` | 68 | 0 | 100% | — |
| `atomic_file_writer.py` | 20 | 2 | 90% | 55–56 |
| `csv_report_exporter.py` | 16 | 0 | 100% | — |
| `database_connection.py` | 66 | 1 | 98% | 96 |
| `inventory_app.py` | 212 | 4 | 98% | 134–136, 273 |
| `logger.py` | 15 | 0 | 100% | — |
| `product.py` | 42 | 3 | 93% | 53, 131, 136 |
| `product_repository.py` | 49 | 0 | 100% | — |
| `validator.py` | 44 | 0 | 100% | — |
| **รวม** | **532** | **10** | **98.12%** | |

---

## ส่วนที่ 5: สรุปผลและข้อจำกัด

**ผลรวม: ✅ PASS** — ติดตั้งบนสภาพแวดล้อมใหม่ได้, แอปพลิเคชันเปิดและใช้งานครบทุกเมนูโดยไม่แครช และ Regression ทุกชุดผ่าน ไม่พบ regression จาก build ที่ผ่าน UAT

| ข้อจำกัด | ผลกระทบ | แนวทาง |
| :--- | :--- | :--- |
| ทดสอบเฉพาะ Python 3.13 บน Windows | Python 3.10–3.12 และ Linux ไม่ได้ทดสอบในรอบนี้ | ตรวจผล GitHub Actions (matrix 3.10/3.11/3.12 บน ubuntu-latest) ของ commit ที่ส่งมอบ |
| `pyflakes` ไม่ได้ pin เวอร์ชัน ได้ 4.0.2 (รายงานสแกนเดิมใช้ 4.0.1) | ผล lint อาจเปลี่ยนเมื่อ dependency ย่อยออกเวอร์ชันใหม่ | บันทึกเป็นงาน Adaptive ใน [คู่มือปฏิบัติการและบำรุงรักษา](./System_Operations_and_Maintenance_Manual.md) ส่วนที่ 6 |

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 2026-10-05 | ผล Smoke Test ครบ 8 เมนู และ Full Regression บน clone ใหม่ของ `80c6d22` |
