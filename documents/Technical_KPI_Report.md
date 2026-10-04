# TECHNICAL KPI REPORT — Version 2.0.1
**Academic Reference:** ISO/IEC 12207 (Measurement, Quality Assurance), ISO/IEC 14764:2006 (Software Maintenance — Maintenance metrics)
**Course Context:** ENGSE225 Software Evolution & Maintenance — ตัวชี้วัดความสำเร็จทางเทคนิคสำหรับ Project Manager ใช้ประกอบการประเมินผลโครงการ

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **Report ID** | **KPI-V2.0-01** |
| **ผู้รับรายงาน** | Project Manager |
| **ระบบ / Build** | Inventory Management System Version 2.0.1 — `main` @ `80c6d22` (โค้ดโปรแกรมตรงกับ build ที่ส่งมอบ `73e7cfd`) |
| **วันที่วัด** | 2026-10-05 |
| **แหล่งข้อมูล** | Full Regression บน clone ใหม่ ([`Smoke_And_Regression_Test_Report.md`](./Smoke_And_Regression_Test_Report.md)), รายงาน UAT, Change Request Log, ประวัติ git |

> ตัวเลขทุกตัวในรายงานนี้ **วัดจริงจาก build ข้างต้น** ไม่ใช่ค่าประมาณ เช่น Code Coverage ที่วัดได้คือ **98.12%** ไม่ใช่ 94% ตัวชี้วัดใดที่วัดไม่ได้ในรอบนี้ระบุสถานะ "ยังไม่ยืนยัน" ไว้ชัดเจน

---

## ส่วนที่ 1: สรุปผู้บริหาร (Executive Summary)

| KPI หลัก | เป้าหมาย | ผลจริง | สถานะ |
| :--- | :--- | :--- | :---: |
| **Code Coverage** | ≥ 90% | **98.12%** | ✅ เกินเป้า 8.12 จุด |
| **Open Defects (Zero Defects)** | 0 | **0** (แก้แล้ว 7/7 BUG ID) | ✅ |
| **Test Pass Rate** | 100% | **100%** (158/158) | ✅ |
| **Static Analysis (Flake8)** | 0 | **0** (จาก 410) | ✅ |
| **Security Scan (Bandit)** | 0 | **0** (จาก 196) | ✅ |
| **UAT Acceptance** | ไม่มี FAIL | **16/16** สถานการณ์ในขอบเขตผ่าน | ✅ |
| **Clean Install Success** | ผ่านทุกขั้น | **12/12** ขั้น | ✅ |
| **CI (GitHub Actions)** | เขียวทุก job | ยังไม่ยืนยัน | ☐ |

**ข้อสรุป:** ตัวชี้วัดที่วัดได้ทั้ง 7 ตัวผ่านเป้าหมาย เหลือ CI ที่ต้องตรวจผลบน GitHub Actions ของ commit ที่ส่งมอบก่อนปิดการประเมิน

---

## ส่วนที่ 2: คุณภาพการทดสอบ (Test Quality)

### 2.1 Code Coverage

| โมดูล | Statements | Coverage | | โมดูล | Statements | Coverage |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| `app_v1.py` | 68 | 100% | | `logger.py` | 15 | 100% |
| `atomic_file_writer.py` | 20 | 90% | | `product.py` | 42 | 93% |
| `csv_report_exporter.py` | 16 | 100% | | `product_repository.py` | 49 | 100% |
| `database_connection.py` | 66 | 98% | | `validator.py` | 44 | 100% |
| `inventory_app.py` | 212 | 98% | | **รวม** | **532** | **98.12%** |

- โมดูลที่ได้ 100%: 5 จาก 9 โมดูล ทุกโมดูล ≥ 90%
- Coverage วัดเฉพาะโค้ดโปรแกรม ไม่นับไฟล์เทสต์ (`pyproject.toml`) และ CI บังคับ `fail_under = 90`

### 2.2 ปริมาณและความครอบคลุมของเทสต์

| ตัวชี้วัด | ค่า |
| :--- | :--- |
| จำนวนเทสต์ทั้งหมด | **158** (Unit 146 + Integration end-to-end 12) |
| Test Pass Rate | **100%** (158 passed, 0 failed, 0 error) |
| เวลารันทั้งชุด | 2.55 วินาที |
| ขนาดโค้ดโปรแกรม (SLOC ไม่นับบรรทัดว่างและคอมเมนต์ รวม docstring) | 974 บรรทัด (ไม่รวมต้นแบบ `app_v1.py`: 893) |
| ขนาดโค้ดเทสต์ (SLOC) | 2,432 บรรทัด |
| **Test-to-Code Ratio** | **2.50 : 1** |
| เทสต์ที่ใช้ฐานข้อมูลจริง (ไม่ mock) | ทุกเทสต์ของ Repository/Integration ตาม DoD SCRUM-7 |

### 2.3 แนวโน้ม (Trend)

| จุดวัด | Commit | เทสต์ | Coverage |
| :--- | :--- | :---: | :---: |
| ก่อนเพิ่ม Integration Test | `6358919` | 126 | 82% |
| เพิ่ม Integration Test + Coverage Gate | `a7b0c73` | 138 | 98.00% |
| แก้ BUG-103 และงานป้องกัน | `d6da33b` | 145 | 98.04% |
| แก้ UAT Defects BUG-104 ถึง BUG-108 | `3a5a207` | **158** | **98.12%** |

---

## ส่วนที่ 3: Defect Metrics (Zero Defects)

### 3.1 สถานะ Defect

| ตัวชี้วัด | ค่า |
| :--- | :--- |
| Defect ที่บันทึกเป็น BUG ID | **7** (BUG-102 ถึง BUG-108) |
| แก้ไขแล้ว | **7** (100%) |
| **Open Defects** | **0** |
| Defect ที่เปิดซ้ำหลังแก้ (Reopened) | 0 |
| การแก้ไขที่ไม่มี BUG ID | 2 (หัวข้อเมนูค้นหาแสดง `[3]` แทน `[5]`, rollback ของ `updateStock`) |

**นิยาม Zero Defects ในรายงานนี้:** ไม่มี Defect ค้าง (Open = 0) ณ build ที่ส่งมอบ ไม่ได้หมายความว่าไม่เคยพบ Defect ระหว่างพัฒนา

### 3.2 รายละเอียดตามระดับความรุนแรงและช่วงที่พบ

| BUG ID | สรุป | ความรุนแรง | พบในช่วง | แก้ใน |
| :---: | :--- | :--- | :--- | :--- |
| BUG-102 | บาร์โค้ดซ้ำ, คำเตือนสต็อกใช้เกณฑ์ผิด, เมนู CSV ไม่เชื่อม UI | ไม่ได้จัดระดับตอนบันทึก | Sprint 2 (Bug Bashing) | PR #27, #29 |
| BUG-103 | ราคา `nan` ทำให้โปรแกรมแครช / `inf` ถูกบันทึก | Critical (แครช) | Code Review ก่อน UAT | `d347d8e` |
| BUG-104 | Export CSV ไปยัง path ผิดแล้วแครช | Critical | UAT รอบ 1 | `3a5a207` |
| BUG-105 | ตัวเลขเกินช่วง SQLite แล้วแครช | Critical | UAT รอบ 1 | `3a5a207` |
| BUG-106 | ภาษาไทยในไฟล์ CSV เพี้ยนใน Excel | Major | UAT รอบ 1 | `3a5a207` |
| BUG-107 | กด Enter ไม่ใช้ค่าเริ่มต้น Reorder Point | Minor | UAT รอบ 1 | `3a5a207` |
| BUG-108 | ตัดสต็อก 0 ชิ้นแล้วแจ้งสำเร็จ | Minor | UAT รอบ 1 | `3a5a207` |

| ตัวชี้วัด | ค่า | หมายเหตุ |
| :--- | :--- | :--- |
| Defect Density | **13.2 defects / 1,000 executable statements** (7 / 532) | นับทุก Defect ที่พบระหว่างพัฒนา ไม่ใช่ Defect ค้าง |
| Defect Removal Efficiency (DRE) | **100%** (เบื้องต้น) | ทุก Defect พบก่อนส่งมอบ ยังไม่มีข้อมูล Defect หลังส่งมอบ ต้องวัดซ้ำหลังใช้งานจริง |
| Critical Defects ค้าง | 0 | Critical ทั้ง 3 ตัวแก้แล้ว |

---

## ส่วนที่ 4: คุณภาพโค้ดและความปลอดภัย (Code Quality & Security)

| ตัวชี้วัด | ก่อนปรับปรุง | ปัจจุบัน | เป้าหมาย |
| :--- | :---: | :---: | :---: |
| Flake8 findings | 410 | **0** | 0 |
| Bandit issues | 196 (ทั้งหมดระดับ Low) | **0** | 0 |
| การปิดคำเตือนด้วย `# noqa` / `# nosec` / `# pragma: no cover` | — | **0** | 0 |
| Docstring ของเมธอด/ฟังก์ชัน public (ไม่รวมต้นแบบ `app_v1.py`) | — | **37/37 (100%)** | 100% ตาม DoD ข้อ 4 |
| Docstring ระดับคลาส | — | 6/8 (ขาด `DatabaseConnection`, `InventoryApp`) | — |

ข้อมูล "ก่อนปรับปรุง" อ้างอิงจาก [`reports/Code_Quality_And_Security_Scan_Report.md`](../reports/Code_Quality_And_Security_Scan_Report.md)

---

## ส่วนที่ 5: การยอมรับและการส่งมอบ (Acceptance & Delivery)

| ตัวชี้วัด | ค่า |
| :--- | :--- |
| Change Requests ที่ส่งมอบ | **2/2** (CR-01, CR-02) |
| UAT รอบ 1 (ก่อนแก้) | 11/16 สถานการณ์ในขอบเขตผ่าน (68.8%) |
| **UAT รอบ 2 (หลังแก้)** | **16/16 (100%)**, FAIL 0, ลงนามยอมรับครบ 4 บทบาท |
| Defect จาก UAT ที่แก้และผ่าน Re-test | 5/5 (100%) |
| New Scope ที่แยกออกจาก Defect และยกไป Version 3.0 | 5 รายการ (FB-01 ถึง FB-05) |
| Smoke Test ทุกเมนูบนสภาพแวดล้อมใหม่ | 8/8 เมนู ไม่แครช |
| Clean Install (Windows / Git Bash) | 12/12 ขั้น, ใช้เวลา 32.4 วินาทีบน Windows |
| การปฏิบัติตาม Scope Freeze | ไม่มีงาน Perfective แทรกช่วง Freeze การแก้ BUG-107/108 ที่เกินข้อยกเว้นได้รับการรับทราบจาก Sponsor ในการลงนาม SFA-01 |

---

## ส่วนที่ 6: ตัวชี้วัดกระบวนการ (Process Metrics)

| ตัวชี้วัด | ค่า | หมายเหตุ |
| :--- | :--- | :--- |
| Commit ทั้งหมดบน `main` | 111 | 2026-07-12 ถึง 2026-10-05 |
| Pull Request ที่ merge | 31 | |
| Commit ที่ไม่ใช่ merge และใช้ Conventional Commit prefix | 26/75 (35%) | ช่วงแรกของโครงการยังไม่ใช้ ช่วง Hardening/UAT ใช้ครบทุก commit |
| Effort ประมาณการของ CR | CR-01: 8 Man-Hours, CR-02: 4.5 Man-Hours | ค่าประมาณจากรายงาน CR ไม่มีบันทึกชั่วโมงจริง จึงคำนวณ Cost Variance ไม่ได้ |

---

## ส่วนที่ 7: ข้อจำกัดและข้อเสนอแนะ

| ประเด็น | ข้อเสนอแนะ |
| :--- | :--- |
| CI บน GitHub Actions ยังไม่ได้ยืนยัน | PM ตรวจหน้า Actions ของ `73e7cfd`/`80c6d22` ก่อนปิดการประเมิน |
| วัดบน Python 3.13 / Windows เท่านั้น | ใช้ผล CI matrix 3.10–3.12 บน Linux เป็นหลักฐานเสริม |
| DRE เป็นค่าเบื้องต้น | วัดซ้ำหลังใช้งานจริงอย่างน้อย 1 รอบ โดยนับ Defect ที่พบหลังส่งมอบ |
| ไม่มีบันทึกชั่วโมงทำงานจริง | เริ่มบันทึก Work Log ตั้งแต่ Version 3.0 เพื่อคำนวณ Cost Variance ($CV = EV - AC$) |
| Docstring ระดับคลาส 2 ตัว | เพิ่มเมื่อมีการแก้โมดูลนั้นครั้งถัดไป |

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 2026-10-05 | รายงาน KPI ทางเทคนิคของ Version 2.0.1 ส่งมอบให้ Project Manager |
