# PROJECT COMPLETION CERTIFICATE (หนังสือรับรองการปิดเฟสพัฒนา)
**Academic Reference:** ISO/IEC 12207 (Project Assessment and Control, Transition Process — ส่งมอบระบบและปิดเฟสอย่างเป็นทางการ), ISO/IEC 14764:2006 (Software Maintenance — ส่งต่อรายการคงค้างเข้าสู่รอบบำรุงรักษาถัดไป)
**Course Context:** ENGSE225 Software Evolution & Maintenance — ปิดเฟสพัฒนา Version 2.0 หลังสิ้นสุด Scope Freeze สัปดาห์ที่ 12

> เอกสารฉบับนี้เป็น **เอกสารจำลอง (Mock Certificate)** สำหรับการเรียนการสอนในรายวิชา ENGSE225 ผู้ลงนามทุกคนเป็นบทบาทจำลอง ไม่ใช่ลายมือชื่อของบุคคลจริง และไม่ใช่เอกสารที่มีผลผูกพันทางกฎหมาย
>
> **สถานะเอกสาร:** ✅ **อนุมัติปิดเฟสแล้ว (จำลอง)** ฉบับ 1.0 วันที่ 2026-10-05

---

## ส่วนที่ 1: ข้อมูลการรับรอง (Certificate Identification)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **Certificate ID** | **PCC-V2.0-01** |
| **Project Title** | Inventory Management System |
| **เฟสที่ปิด** | เฟสพัฒนา Version 2.0 (Sprint 1, Sprint 2 และช่วง Hardening/UAT จนถึง Scope Freeze สัปดาห์ที่ 12) |
| **Version ที่ส่งมอบ** | **2.0.1** ตาม [`CHANGELOG.md`](../CHANGELOG.md) |
| **Build ที่ส่งมอบ** | branch `main` @ **`73e7cfd`** — โค้ดโปรแกรม (`*.py`, `*.sql`) ตรงกับ `3a5a207` ซึ่งผ่าน UAT รอบ 2 และเป็นโค้ดเดียวกับ Baseline `f6d7e77` ที่ลงนามในสัญญา SFA-01 commit หลังจากนั้นเป็นเอกสารและสคริปต์ติดตั้งเท่านั้น |
| **Repository** | https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM |
| **ผู้อนุมัติ (Project Sponsor)** | อาจารย์ผู้สอน / Sponsor ประจำวิชา |
| **ผู้ส่งมอบ (Project Team)** | ทีมพัฒนา Inventory Management System (PM, Tech Lead, Developer, QA) |

---

## ส่วนที่ 2: ขอบเขตที่ส่งมอบ (Delivered Scope)

| หมวด | รายการที่ส่งมอบ | สถานะ |
| :--- | :--- | :---: |
| ฟังก์ชันหลัก | เมนู 1–8: แสดงสินค้า (แบ่งหน้า), เพิ่ม/แก้ไข, ตัดสต็อก, รายงานสรุป, ค้นหา, แจ้งเตือนสินค้าใกล้หมด, Export CSV, ออกจากโปรแกรม | ✅ |
| Change Requests | CR-01 Barcode & Reorder Point Alert, CR-02 Export Low Stock CSV | ✅ |
| Defects ที่แก้ | BUG-102, BUG-103, BUG-104, BUG-105, BUG-106, BUG-107, BUG-108 | ✅ ไม่มี Defect ค้าง |
| งานป้องกัน (Preventive) | Atomic File Write, rollback ของ `updateStock`, Flake8/Bandit = 0 | ✅ |
| การติดตั้ง | สคริปต์ติดตั้งอัตโนมัติ `scripts/setup.cmd`, `setup.ps1`, `setup.sh` | ✅ |

---

## ส่วนที่ 3: เกณฑ์การปิดเฟสและหลักฐาน (Exit Criteria & Evidence)

| # | เกณฑ์ | ผลลัพธ์ | หลักฐาน | ผ่าน |
| :---: | :--- | :--- | :--- | :---: |
| 1 | ฟังก์ชันครบตามขอบเขตที่ล็อกในสัญญา Scope Freeze | ครบตามส่วนที่ 2 ของสัญญา ไม่มีงานนอกขอบเขตแทรกเข้ามา | [`Scope_Freeze_Sign_off_Agreement.md`](./Scope_Freeze_Sign_off_Agreement.md) (ลงนามแล้ว) | ✅ |
| 2 | Unit + Integration Test ผ่านทั้งหมด | 158 passed, 0 failed | [`CHANGELOG.md`](../CHANGELOG.md) 2.0.1, [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md) ส่วนที่ 6.3 | ✅ |
| 3 | Code Coverage ≥ 90% | 98.12% | `python -m pytest --cov` | ✅ |
| 4 | Static Analysis และ Security Scan ไม่มีปัญหา | Flake8 0 findings, Bandit No issues | [`reports/Code_Quality_And_Security_Scan_Report.md`](../reports/Code_Quality_And_Security_Scan_Report.md) | ✅ |
| 5 | ผ่าน User Acceptance Testing | รอบ 2: 16/16 สถานการณ์ในขอบเขตผ่าน, FAIL 0, ลงนามรับรอง "ยอมรับ" ครบ 4 บทบาท | [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md), [`reports/uat_evidence_r2.txt`](../reports/uat_evidence_r2.txt) | ✅ |
| 6 | ติดตั้งบนเครื่องใหม่ได้ (Clean Environment Installation) | Windows และ Git Bash ผ่าน 12/12 ขั้นบน clone ใหม่ | [`Clean_Environment_Installation_Test.md`](./Clean_Environment_Installation_Test.md) | ✅ |
| 7 | เอกสารครบถ้วนและตรงกับโค้ด | README, CHANGELOG, รายงาน CR-01/CR-02, Risk Register, DoD ปรับให้ตรงกับ Version 2.0.1 แล้ว | [`README.md`](../README.md), [`CHANGELOG.md`](../CHANGELOG.md) | ✅ |
| 8 | CI บน GitHub Actions เขียวทุก job (Python 3.10/3.11/3.12 + lint) | ต้องตรวจที่หน้า Actions ของ commit `73e7cfd` | GitHub Actions | ☐ ตรวจก่อนส่งงานจริง |

> เกณฑ์ข้อ 8 ทีมยังไม่ได้แนบผลไว้ในเอกสาร เพราะการตรวจในเครื่องใช้ Python 3.13 เท่านั้น ก่อนยื่นใบรับรองฉบับจริงให้แนบภาพหรือลิงก์ผล CI ของ commit ที่ส่งมอบ

---

## ส่วนที่ 4: รายการคงค้างที่ส่งต่อ (Open Items Handed Over)

รายการต่อไปนี้ **ไม่ใช่เงื่อนไขการปิดเฟส** และส่งต่อไปยังรอบพัฒนา Version 3.0 ตามข้อตกลงในสัญญา SFA-01

| ID | รายการ | ประเภท | ส่งต่อไป |
| :---: | :--- | :--- | :--- |
| FB-01 | เมนูรับสินค้าเข้าคลัง (Restock) ที่บันทึก `stock_movements` | Perfective (Must) | Version 3.0 |
| FB-02 | หน้าจอยืนยันการแก้ไขแบบตาราง และกด Enter เพื่อคงค่าเดิม | Perfective (Should) | Version 3.0 |
| FB-03 | เกณฑ์ "ใกล้หมด" ของรายงานสรุป (รอ Sponsor ตัดสิน) | Perfective (Should) | Version 3.0 |
| FB-04 | Barcode แสดงครบทุกหลักใน Excel | Perfective (Could) | Version 3.0 |
| FB-05 | จัดคอลัมน์ตารางให้ตรงเมื่อชื่อเป็นภาษาไทย | Perfective (Could) | Version 3.0 |
| — | ทดสอบสคริปต์ติดตั้งบน Linux และ macOS จริง | Verification | รอบบำรุงรักษาถัดไป |

---

## ส่วนที่ 5: การอนุมัติปิดเฟส (Completion Approval)

ข้าพเจ้าในฐานะ Project Sponsor ได้ตรวจสอบขอบเขตที่ส่งมอบ (ส่วนที่ 2), เกณฑ์การปิดเฟสและหลักฐาน (ส่วนที่ 3) และรายการคงค้างที่ส่งต่อ (ส่วนที่ 4) แล้ว ขอรับรองว่าเฟสพัฒนา **Inventory Management System Version 2.0.1** เสร็จสมบูรณ์ตามขอบเขตที่ตกลงไว้ และอนุมัติให้ปิดเฟสพัฒนาอย่างเป็นทางการ โดยรายการในส่วนที่ 4 ยกไปดำเนินการใน Version 3.0

| บทบาท | ชื่อ-นามสกุล | ลายมือชื่อ | วันที่ |
| :--- | :--- | :--- | :--- |
| **Project Sponsor / อาจารย์ผู้สอน** (ผู้อนุมัติ) | ผู้แทน Sponsor (จำลอง) | ✍️ /ลงนามจำลอง/ | 05/10/2026 |
| Project Manager (PM) — ผู้ส่งมอบ | PM ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 05/10/2026 |
| Tech Lead — รับรองด้านเทคนิค | Tech Lead ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 05/10/2026 |
| QA — รับรองด้านคุณภาพ | QA ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 05/10/2026 |

### ความเห็นของ Project Sponsor

1. รับมอบระบบ Version 2.0.1 ที่ build `73e7cfd` และอนุมัติปิดเฟสพัฒนา
2. ทีมต้องแนบผล CI ของ commit ที่ส่งมอบ (เกณฑ์ข้อ 8) ประกอบการส่งงานฉบับจริง
3. ให้เริ่มวางแผน Version 3.0 จาก Future Backlog โดยจัด FB-01 เป็นลำดับแรกตามความเห็นของตัวแทนผู้ใช้ใน UAT

### บันทึกการอนุมัติ (Approval Record)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **วันที่อนุมัติ** | 2026-10-05 |
| **ผลการอนุมัติ** | ✅ อนุมัติปิดเฟสพัฒนา ผู้ลงนามครบ 4/4 บทบาท |
| **เอกสารอ้างอิงที่ลงนามแล้ว** | สัญญา Scope Freeze SFA-01 (2026-10-04), รายงาน UAT-V2.0-01 (2026-10-04) |
| **รูปแบบ** | การลงนามจำลองเพื่อการเรียนการสอน ผู้ลงนามเป็นบทบาทสมมติ ไม่ใช่ลายมือชื่อของบุคคลจริง |
| **ผลต่อ Scope Freeze** | สัญญา SFA-01 สิ้นสุดตามข้อ 5.4 เมื่อส่งมอบงานครั้งสุดท้าย การเปลี่ยนแปลงหลังจากนี้ให้เปิดเป็น CR/BUG ใหม่ในรอบ Version 3.0 |

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 2026-10-05 | ออกหนังสือรับรองการปิดเฟสพัฒนา Version 2.0.1 พร้อมการลงนามจำลองครบ 4 บทบาท |
