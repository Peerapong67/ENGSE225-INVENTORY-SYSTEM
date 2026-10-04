# Code Quality & Security Scan Report

| หัวข้อ | รายละเอียด |
|---|---|
| วันที่สแกน | 2026-10-03 |
| Branch | `feature/atomic-file-writing` (ฐาน `45f6e36`) — Atomic Write commit ใน `4e0a5b7` และการแก้ไขตามรายงานนี้ commit ใน `6358919` แล้ว merge เข้า `main` ผ่าน PR #32 และ #33 |
| ขอบเขต | ไฟล์ `.py` ทั้งหมด 19 ไฟล์ใน root ของ repo (Bandit นับได้ 2,928 บรรทัดโค้ด) ไม่รวม `.git/`, `__pycache__/`, `reports/` |
| เครื่องมือ | Flake8 7.4.1 (pycodestyle 2.15.0, pyflakes 4.0.1, mccabe 0.7.0), Bandit 1.9.4, pytest 9.1.1, CPython 3.13.14 |
| Config | [`.flake8`](../.flake8), [`pyproject.toml`](../pyproject.toml) (`[tool.bandit]`) |
| Raw output (หลังแก้) | [`flake8_report.txt`](flake8_report.txt), [`bandit_report.txt`](bandit_report.txt), [`pytest_report.txt`](pytest_report.txt) |
| Raw output (ก่อนแก้) | [`flake8_report_before.txt`](flake8_report_before.txt), [`bandit_report_before.txt`](bandit_report_before.txt) |

## สรุปผล

| การสแกน | ก่อนแก้ | หลังแก้ | สถานะ |
|---|---:|---:|:---:|
| Flake8 (คุณภาพ/สไตล์) | 410 จุด | **0** (exit code 0) | ✅ ผ่าน 100% |
| Bandit (ความปลอดภัย) | 196 จุด (Low 196 / Medium 0 / High 0) | **0** — `No issues identified.` (exit code 0) | ✅ ผ่าน 100% |
| pytest (regression) | 126 passed | **126 passed** (exit code 0) | ✅ ไม่มีเทสต์พัง |

**ยืนยันผล:** โค้ดทั้ง 19 ไฟล์ผ่าน Flake8 และ Bandit ครบ 100% ตามเกณฑ์ที่กำหนดในหัวข้อ 3 และเทสต์เดิมทั้งหมดยังผ่าน

> **ข้อควรทราบ:** "100%" นี้วัดตามเกณฑ์ที่ทีมตั้งไว้ใน config ไม่ใช่ค่า default ล้วนของเครื่องมือ มีการปรับเกณฑ์ 2 จุด (ดูหัวข้อ 3) ถ้ารันด้วยค่า default จะยังเหลือ E501 ที่บรรทัดเกิน 79 ตัวอักษร และ B101 (`assert`) ในไฟล์เทสต์ 185 จุด ทั้งสองอย่างไม่ใช่ข้อบกพร่องด้านการทำงานหรือความปลอดภัย

---

## 1. วิธีรันซ้ำ

```
pip install -r requirements-dev.txt
python -m flake8 --statistics --count .
python -m bandit -c pyproject.toml -r .
python -m pytest -v
```

ทั้งสามคำสั่งต้องจบด้วย exit code 0

---

## 2. สิ่งที่แก้ไขในโค้ด

### Flake8

| Code | จำนวน | ความหมาย | วิธีแก้ |
|---|---:|---|---|
| E501 | 374 → 0 | บรรทัดยาวเกิน | ตั้ง `max-line-length = 120` (หัวข้อ 3) แล้วตัดบรรทัด 8 บรรทัดที่ยังเกิน 120 ใน `database_connection.py`, `inventory_app.py`, `test_database_connection.py`, `test_inventory_app.py`, `test_product_repository.py` |
| W292 | 10 | ไม่มีบรรทัดว่างท้ายไฟล์ | เพิ่ม newline ท้ายไฟล์ |
| W293 | 9 | บรรทัดว่างมี whitespace | ลบ whitespace (`app_v1.py` 8 จุด, `database_connection.py` 1 จุด) |
| E302 / E305 | 6 / 1 | เว้นบรรทัดก่อน/หลัง def/class ไม่ครบ 2 บรรทัด | เพิ่มบรรทัดว่าง |
| E127 | 4 | ย่อหน้าบรรทัดต่อเนื่องเกิน | จัดให้ตรงวงเล็บเปิด |
| F401 | 3 | import แล้วไม่ได้ใช้ | ลบ `import pytest` ใน `test_inventory_app.py`, `test_validator.py` และ `import sqlite3` ใน `test_product_repository.py` |
| E741 | 3 | ชื่อตัวแปรกำกวม `l` | เปลี่ยนเป็น `logger` ใน `test_logger.py` |

### Bandit

| Test ID | จำนวน | ตำแหน่ง | วิธีแก้ |
|---|---:|---|---|
| B101 `assert_used` | 10 | บล็อก self-test `if __name__ == "__main__":` ใน `database_connection.py` (5) และ `inventory_app.py` (5) | เปลี่ยนเป็น `_verify(condition, message)` ที่ `raise AssertionError` เอง ทำให้การตรวจยังทำงานแม้รันด้วย `python -O` |
| B110 `try_except_pass` | 1 | `conftest.py` (teardown ปิด connection) | เปลี่ยนเป็น `contextlib.suppress(sqlite3.Error)` จับเฉพาะ error ของ SQLite ไม่กลืน `Exception` ทุกชนิดแบบเดิม |
| B101 `assert_used` | 185 | ไฟล์ `test_*.py` และ `conftest.py` | ไม่แก้โค้ด แต่ตั้ง config ให้ข้ามเฉพาะไฟล์เทสต์ (หัวข้อ 3) |

ไม่มีการใช้ `# noqa` หรือ `# nosec` ในโค้ดเลย (Bandit รายงาน `Total lines skipped (#nosec): 0`)

---

## 3. เกณฑ์ที่ปรับจากค่า default และเหตุผล

| Config | ค่า | เหตุผล |
|---|---|---|
| `.flake8` → `max-line-length` | `120` (default 79) | docstring และข้อความในโปรแกรมเป็นภาษาไทย ซึ่ง Flake8 นับสระบน/ล่างและวรรณยุกต์เป็นตัวอักษรด้วย บรรทัดที่ดูสั้นจึงถูกนับเกิน 79 ได้ง่าย ทีมเลือก 120 แทนการตัด 374 บรรทัดเป็นท่อนสั้นๆ |
| `pyproject.toml` → `[tool.bandit.assert_used] skips` | `*/test_*.py`, `*/conftest.py` | pytest ใช้ `assert` เป็นกลไกหลักในการตรวจผล และโค้ดเทสต์ไม่ได้รันใน production ข้าม **เฉพาะ B101 ในไฟล์เทสต์** ไฟล์เทสต์ยังถูกตรวจกฎอื่นของ Bandit ครบ และโค้ดโปรแกรมจริงยังถูกตรวจ B101 ตามปกติ |

ตรวจแล้วว่า config ไม่ได้ซ่อนปัญหาอื่น:
- Bandit ยังสแกนครบทั้ง 19 ไฟล์ `.py` (`Files in scope (19)` ใน `bandit_report.txt`) ไฟล์ที่ถูก exclude มีแต่ไฟล์ที่ไม่ใช่ `.py`
- รัน Bandit ซ้ำโดย**ไม่ใช้** config พบเฉพาะ B101 ในไฟล์เทสต์ 185 จุด ไม่มีปัญหาประเภทอื่นหลงเหลือ

---

## 4. ผลด้านความปลอดภัยที่ควรทราบ

- **ไม่พบ SQL Injection (B608):** ทุก query ใช้ parameterized query (`?`) ผ่าน `DatabaseConnection.executeQuery()`
- ไม่พบการใช้ `eval`/`exec`, `pickle`, `subprocess` แบบ `shell=True`, รหัสผ่าน hardcode หรือ temp file ที่ไม่ปลอดภัย (B108) — `AtomicFileWriter` ใช้ `tempfile.mkstemp()` ซึ่งปลอดภัย
- ตั้งแต่ก่อนแก้ก็ไม่มีปัญหาระดับ Medium หรือ High

---

## 5. การยืนยันว่าการแก้ไม่ทำให้ระบบพัง

- `python -m pytest -v` → **126 passed** เท่ากับก่อนแก้ ([`pytest_report.txt`](pytest_report.txt))
- รัน self-test ของ `database_connection.py` และ `inventory_app.py --selftest` บนสำเนาในโฟลเดอร์ชั่วคราว (ไม่แตะ `inventory.db` จริง) ผ่านทุกเกณฑ์หลังเปลี่ยนเป็น `_verify`

---

## 6. การป้องกันระยะยาว (CI)

เพิ่ม job `lint` ใน [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) แล้ว job นี้รันคู่ขนานกับ `pytest` ทุกครั้งที่ push หรือเปิด PR เข้า `main`/`develop` ติดตั้งจาก `requirements-dev.txt` ซึ่งล็อก `flake8==7.4.1` และ `bandit[toml]==1.9.4` (เวอร์ชันเดียวกับที่ใช้ในรายงานนี้) แล้วรัน `python -m flake8 --statistics --count .` และ `python -m bandit -c pyproject.toml -r .` ถ้าพบปัญหาแม้แต่จุดเดียว CI จะ fail

**เวอร์ชันเครื่องมือ:** ล็อกไว้ใน `requirements-dev.txt` ที่เดียว ทั้ง CI และเครื่องของทุกคนในทีมติดตั้งจากไฟล์นี้ จึงได้เวอร์ชันเดียวกันเสมอ
