# Integration Test & Code Coverage Report

| หัวข้อ | รายละเอียด |
|---|---|
| วันที่รัน | 2026-10-03 18:24 (+07:00) |
| Branch | `feature/atomic-file-writing` (ยังไม่ commit) |
| ไฟล์เทสต์ใหม่ | [`test_integration.py`](../test_integration.py) — Full Integration Test 12 เคส |
| เครื่องมือ | pytest 9.1.1, pytest-cov 7.1.0 (coverage.py 7.16.2), CPython 3.13.14 |
| Config | [`pyproject.toml`](../pyproject.toml) → `[tool.coverage.run]`, `[tool.coverage.report]` |
| หลักฐาน | โฟลเดอร์ [`test_evidence/`](test_evidence/) (รายการในหัวข้อ 4) |

## สรุปผล

| เกณฑ์ | เป้าหมาย | ผลจริง | สถานะ |
|---|---|---|:---:|
| ผลการรัน PyTest | ผ่าน 100% | **138 passed**, 0 failed, 0 skipped, 0 error (exit code 0) | ✅ |
| Overall Code Coverage | ≥ 90% | **98.00%** (499 statements, ขาด 10) | ✅ |
| Integration Test ใหม่ | — | 12/12 passed | ✅ |

Coverage ก่อนเพิ่ม integration test อยู่ที่ 82% (ขาด 89 จาก 499 statements) หลังเพิ่มเป็น 98%

---

## 1. Full Integration Test (`test_integration.py`)

**แนวคิด:** unit test เดิมทดสอบทีละคลาส ส่วนไฟล์นี้เปิดโปรแกรมผ่านเมนูหลัก `InventoryApp.run()` หรือ entry point จริง (`python <file>.py`) แล้วให้ทุกชั้นทำงานร่วมกันจริงทั้งหมด **ไม่ mock คลาสใดเลย** สิ่งเดียวที่จำลองคือการพิมพ์ของผู้ใช้ (`input`)

```
InventoryApp ─► Validator ─► Product ─► ProductRepository ─► DatabaseConnection ─► SQLite (.db จริง + schema.sql)
            ├─► Logger ─► ตาราง action_logs
            └─► CsvReportExporter ─► AtomicFileWriter ─► ไฟล์ .csv จริง
```

แต่ละเคสใช้ไฟล์ `.db` จริงบนดิสก์ในโฟลเดอร์ชั่วคราวของ pytest จึงไม่แตะ `inventory.db` จริง ถ้าโปรแกรมถาม input เกินกว่าที่สคริปต์ป้อนไว้ เทสต์จะ fail ทันทีแทนการวนค้าง และต้องใช้ input ครบพอดีด้วย

| ID | สถานการณ์ | สิ่งที่ตรวจ |
|---|---|---|
| IT-01 | ใช้งานครบทุกเมนู 1–8 ต่อเนื่องในรอบเดียว: เพิ่มสินค้า 3 ชิ้น (ชื่อภาษาไทย) → แสดงทั้งหมด → ตัดสต็อก → รายงาน → ค้นหา → แจ้งเตือน → Export CSV → เมนูผิด → ออก | ข้อความบนจอทุกขั้น, ยอดรวมและมูลค่าในรายงาน (27 หน่วย, 620.00 บาท), ข้อมูลในตาราง `products` และ `stock_movements`, ลำดับ `action_logs` ครบ 7 รายการ, เนื้อหาไฟล์ CSV ตรงทุกแถวและภาษาไทยไม่เพี้ยน |
| IT-02 | แก้ไขสินค้าเดิม ยืนยัน `y` แล้วลองแก้อีกครั้งแต่ตอบ `n` | แสดงข้อมูลเดิมเทียบข้อมูลใหม่, upsert ไม่สร้างแถวซ้ำ, ค่าที่บันทึกเป็นของครั้งที่ยืนยัน, log เป็น `ADD_PRODUCT` → `UPDATE_PRODUCT` |
| IT-03 | ข้อผิดพลาด 10 แบบในรอบเดียว: รหัสว่าง, ชื่อว่าง, กรอกตัวเลขผิด/ติดลบ (Validator ถามซ้ำ), บาร์โค้ดซ้ำ, ตัดสต็อกสินค้าที่ไม่มี, ตัดเกินสต็อก, ค้นหาคำว่าง, ค้นหาไม่พบ, แจ้งเตือนตอนไม่มีสินค้าใกล้หมด | ข้อความ error ถูกต้องทุกกรณี และ**ฐานข้อมูลไม่มีข้อมูลขยะ**: มีสินค้าเดียว สต็อกไม่เปลี่ยน ไม่มี stock movement ไม่มี log เกิน |
| IT-04 | สินค้า 23 รายการ (3 หน้า) เลื่อนหน้าผ่านเมนู: `p` ที่หน้าแรก, `n` จนเกินหน้าสุดท้าย, `p`, คำสั่งผิด, `q` | หัวหน้า 1/3, 2/3, 3/3, ช่วงรายการ 21–23, ข้อความเตือนขอบหน้าแรก/หน้าสุดท้าย และคำสั่งผิด |
| IT-05 | คลังว่างเปล่า: แสดงทั้งหมด, รายงาน, แจ้งเตือน | ไม่ crash แสดง 0 / 0.00 บาท และข้อความ "ไม่พบข้อมูล" |
| IT-06 | เพิ่มสินค้าและตัดสต็อก → ปิดโปรแกรม (ปิด connection, ล้าง singleton) → เปิดใหม่กับไฟล์เดิม | ข้อมูลและ log ยังอยู่ครบ, `schema.sql` ที่รันซ้ำตอนเปิดใหม่ไม่ลบข้อมูลเดิม, รายงานหลังเปิดใหม่ถูกต้อง |
| IT-07 | เขียน SQL ตรงข้ามชั้นแอป (Defense in Depth) | ฐานข้อมูลยังกันไว้ได้: บาร์โค้ดซ้ำ (partial UNIQUE index), จำนวนติดลบ (CHECK), stock movement ของสินค้าที่ไม่มี (FOREIGN KEY) และอนุญาตให้บาร์โค้ดว่างซ้ำกันได้ |
| IT-08 | Export CSV แล้วเปลี่ยนสต็อก จากนั้น Export ทับไฟล์เดิมผ่านเมนู | ไฟล์ใหม่แทนที่ไฟล์เดิมทั้งไฟล์, ไม่มีไฟล์ `.tmp` ค้างจาก atomic write, log export 2 ครั้ง |
| IT-09 | `python inventory_app.py` (entry point จริง) | เปิดเมนูได้ ดูรายงานแล้วออกได้ |
| IT-10 | `python inventory_app.py --selftest` | self-test DoD SCRUM-12 ผ่าน และลบสินค้าจำลองออกจากฐานข้อมูลหมด |
| IT-11 | `python database_connection.py` | self-test DoD SCRUM-6 ผ่าน และสร้างไฟล์ฐานข้อมูลจริง |
| IT-12 | `python app_v1.py` (ระบบเก่า) | เมนูรายงานทำงาน, ออกได้ และไม่เขียน `data.json` เมื่อแค่ดูรายงาน |

---

## 2. วิธีรัน

```
pip install -r requirements.txt
python -m pytest -v --cov --cov-report=term-missing
```

ถ้า coverage ต่ำกว่า 90% คำสั่งนี้จะ fail เอง เพราะตั้ง `fail_under = 90` ไว้ใน `pyproject.toml`

**CI:** job `pytest` ใน [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) รันคำสั่งเดียวกันนี้บน Python 3.10, 3.11 และ 3.12 ทุกครั้งที่ push หรือเปิด PR เข้า `main`/`develop` และ `pytest-cov` อยู่ใน `requirements.txt` แล้ว (จำกัดช่วงเวอร์ชันที่ทดสอบแล้ว: `pytest>=8.0,<10`, `pytest-cov>=7.0,<8`) ถ้ามีเทสต์ fail หรือ coverage ต่ำกว่า 90% CI จะ fail

---

## 3. ผล Coverage รายไฟล์

| ไฟล์ | Statements | Miss | Cover | บรรทัดที่ยังไม่ถูกรัน และเหตุผล |
|---|---:|---:|---:|---|
| `app_v1.py` | 68 | 0 | 100% | |
| `atomic_file_writer.py` | 20 | 2 | 90% | 55-56: กรณีลบไฟล์ชั่วคราวไม่สำเร็จ (`OSError`) ระหว่างจัดการ error อีกตัว ต้องจำลองระบบไฟล์พังซ้อนสองชั้น |
| `csv_report_exporter.py` | 16 | 0 | 100% | |
| `database_connection.py` | 66 | 1 | 98% | 96: บรรทัด `raise` ของ `_verify` ทำงานเฉพาะเมื่อ self-test ล้มเหลว |
| `inventory_app.py` | 204 | 4 | 98% | 127-129: กันกรณี stock ถูกเปลี่ยนระหว่างเช็คกับตัดจริง (race condition) ซึ่งเกิดไม่ได้ในโปรแกรม single-user · 256: `raise` ของ `_verify` เหมือนด้านบน |
| `logger.py` | 15 | 0 | 100% | |
| `product.py` | 35 | 3 | 91% | 39: `reorder_point` ติดลบ (Validator กันไว้ก่อนถึงชั้นนี้) · 115: `__eq__` เทียบกับ object ที่ไม่ใช่ Product · 120: `__repr__` ใช้ตอน debug |
| `product_repository.py` | 42 | 0 | 100% | |
| `validator.py` | 33 | 0 | 100% | |
| **TOTAL** | **499** | **10** | **98%** | |

**ขอบเขตการวัด:** วัดเฉพาะไฟล์โค้ดโปรแกรม 9 ไฟล์ ไม่นับไฟล์เทสต์ (`test_*.py`, `conftest.py`) ตามแนวปฏิบัติทั่วไป เพราะเทสต์ไม่ใช่สิ่งที่ถูกทดสอบ ไม่มีการใช้ `# pragma: no cover` ซ่อนบรรทัดใด (คอลัมน์ excluded = 0 ในรายงาน HTML) ถ้านับไฟล์เทสต์รวมด้วยจะได้ 77% เพราะไฟล์เทสต์เดิมหลายไฟล์มีโหมด demo `if __name__ == "__main__":` ที่ไม่ได้ถูกเรียกตอนรันผ่าน pytest

---

## 4. หลักฐาน (`reports/test_evidence/`)

| ไฟล์ | เนื้อหา |
|---|---|
| [`pytest_coverage_summary.png`](test_evidence/pytest_coverage_summary.png) | ภาพสรุปสำหรับแนบ: หัว session, ผล integration test 12 เคส, ตาราง coverage, `Required test coverage of 90.0% reached. Total coverage: 98.00%` และ `138 passed` (บรรทัด PASSED ของไฟล์อื่นย่อไว้ โดยมีบรรทัดระบุจำนวนที่ย่อ) |
| [`pytest_coverage_full.png`](test_evidence/pytest_coverage_full.png) | ภาพผลการรันเต็ม ครบทั้ง 138 เทสต์ทีละบรรทัด |
| [`coverage_html_index.png`](test_evidence/coverage_html_index.png) | ภาพหน้าแรกของรายงาน Coverage แบบ HTML (98%) |
| [`pytest_coverage_output.txt`](test_evidence/pytest_coverage_output.txt) | ข้อความ output จาก CLI ฉบับเต็มของการรันเดียวกัน |
| `htmlcov/index.html` (ไม่ได้ commit) | รายงาน Coverage แบบ HTML ที่คลิกดูรายไฟล์ได้ว่าบรรทัดไหนถูกรัน/ไม่ถูกรัน `.gitignore` ของทีมตัด `htmlcov/` ออกจาก repo จึงไม่ได้ commit แต่สร้างใหม่ได้ด้วย `python -m pytest --cov --cov-report=html` แล้วเปิด `htmlcov/index.html` (ภาพหน้าแรกอยู่ใน `coverage_html_index.png`) |

**วิธีจัดทำภาพ:** ภาพทั้งสามสร้างจากการรันครั้งเดียวกัน (2026-10-03 18:24 +07:00) ภาพ terminal เก็บ output จริงของคำสั่ง `pytest` พร้อมสี แล้ว render เป็นภาพหน้าต่าง terminal ภาพ HTML จับหน้าจอด้วย Microsoft Edge แบบ headless ไม่ได้แก้ไขตัวเลขหรือข้อความใดในผลลัพธ์
