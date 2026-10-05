# แฟ้มประวัติวิศวกรรมบำรุงรักษาระบบฉบับสมบูรณ์ (Complete System Maintenance Dossier)
**มาตรฐานอ้างอิง:** ISO/IEC 14764:2006 (Software Engineering — Software Life Cycle Processes — Maintenance), ISO/IEC/IEEE 12207 (กระบวนการบำรุงรักษา การจัดการโครงแบบ และการจัดการสารสนเทศ)
**รายวิชา:** ENGSE225 Software Evolution & Maintenance

## วัตถุประสงค์ของเอกสาร

แฟ้มฉบับนี้รวบรวมประวัติวิศวกรรมบำรุงรักษาทั้งหมดของระบบ Inventory Management System ตั้งแต่ต้นแบบจนถึงเวอร์ชัน 2.0.1 ไว้ในที่เดียว เพื่อส่งมอบให้ทีมผู้ดูแลระบบรุ่นถัดไป ผู้รับมอบควรอ่านแฟ้มนี้เป็นเอกสารแรก แล้วจึงอ่านเอกสารอ้างอิงตามดัชนีในส่วนที่ 9

**ลำดับการอ่านที่แนะนำสำหรับทีมใหม่**
1. ส่วนที่ 1–2 เพื่อรู้จักระบบและเวอร์ชันปัจจุบัน
2. ส่วนที่ 8 รายการตรวจสอบการรับมอบ และงานแรกที่ควรทำ
3. ส่วนที่ 3 ประวัติการบำรุงรักษา และส่วนที่ 7 งานคงค้าง
4. [`System_Operations_and_Maintenance_Manual.md`](./System_Operations_and_Maintenance_Manual.md) สำหรับการปฏิบัติงานประจำวัน

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **รหัสเอกสาร** | **SMD-V2.0-01** |
| **ระบบ** | Inventory Management System เวอร์ชัน **2.0.1** |
| **ผู้ส่งมอบ** | ทีมพัฒนาเวอร์ชัน 2.0 (ผู้จัดการโครงการ, หัวหน้าฝ่ายเทคนิค, นักพัฒนา, ผู้ทดสอบ) |
| **ผู้รับมอบ** | ทีมผู้ดูแลระบบรุ่นถัดไป (เวอร์ชัน 3.0 และการบำรุงรักษาต่อเนื่อง) |
| **สถานะ** | ฉบับที่ 1.1 ลงวันที่ 5 ตุลาคม 2026 รอการลงนามรับมอบในส่วนที่ 10 |

---

## ส่วนที่ 1: ข้อมูลระบบและ Baseline ปัจจุบัน

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| ลักษณะระบบ | โปรแกรมจัดการสต็อกสินค้าแบบเมนูคอนโซล 8 เมนู ภาษา Python 3.10 ขึ้นไป ฐานข้อมูล SQLite ใช้เฉพาะไลบรารีมาตรฐาน |
| คลังโค้ด | https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM |
| ชุดโค้ดที่ส่งมอบ | `main` ที่ commit `73e7cfd` (โค้ดโปรแกรมตรงกับ `3a5a207` ซึ่งผ่านการทดสอบการยอมรับ และตรงกับ Baseline `f6d7e77` ที่ลงนามในสัญญาล็อกขอบเขต) บวกการปรับโครงสร้างลดความซับซ้อนในรายการที่ 17 ซึ่งไม่เปลี่ยนพฤติกรรมของโปรแกรม แต่ยังไม่ได้ commit และต้องผ่าน CI และ QA ก่อนรวมเข้า `develop` |
| ป้ายกำกับเวอร์ชัน (tag) | `v1.0.0` (ต้นแบบ, 1 สิงหาคม 2026) ส่วน `v2.0.1` อยู่ระหว่างรอสร้างตามแผนการปล่อยระบบ |
| ชุดไฟล์กระจาย | sdist, wheel และ Docker image เวอร์ชัน 2.0.1 ผ่านการทดสอบทั้งหมด ([`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md)) |
| สถานะคุณภาพ | ชุดทดสอบผ่าน 158 รายการ, ความครอบคลุมร้อยละ 98.38, Flake8 และ Bandit เป็นศูนย์, Cyclomatic Complexity สูงสุด 6, ข้อบกพร่องคงค้าง 0, pip-audit ไม่พบช่องโหว่ และ Docker image ไม่มีช่องโหว่ของแพ็กเกจ Python (ข้อยกเว้นดูส่วนที่ 7.3) |

---

## ส่วนที่ 2: โครงสร้างระบบและรายการองค์ประกอบโครงแบบ (Configuration Items)

### 2.1 องค์ประกอบของโปรแกรม

| ชั้น | ไฟล์ | หน้าที่ |
| :--- | :--- | :--- |
| ส่วนติดต่อผู้ใช้ | `inventory_app.py` | เมนู 1–8, แบ่งหน้า, บันทึก log ทุกการทำงาน |
| ตรวจข้อมูลนำเข้า | `validator.py` | วนถามจนได้ค่าที่ถูกต้อง, ยืนยันก่อนเขียนทับ |
| ข้อมูลสินค้า | `product.py` | ตรวจค่าใน constructor, `is_low_stock()`, ค่าคงที่ `SQLITE_MAX_INTEGER` และ `DEFAULT_REORDER_POINT` |
| เข้าถึงข้อมูล | `product_repository.py` | คำสั่ง SQL ทั้งหมด, กันบาร์โค้ดซ้ำ, ตัดสต็อกแบบ transaction |
| เชื่อมต่อฐานข้อมูล | `database_connection.py` | Singleton, รัน `schema.sql` ทุกครั้งที่เชื่อมต่อ |
| บันทึกการทำงาน | `logger.py` | Singleton, บันทึกลงตาราง `action_logs` |
| ส่งออกรายงาน | `csv_report_exporter.py`, `atomic_file_writer.py` | ส่งออก CSV แบบ UTF-8 พร้อม BOM เขียนไฟล์แบบ atomic |
| โครงสร้างฐานข้อมูล | `schema.sql`, `seed_data.sql` | ตาราง ดัชนี trigger และข้อมูลตัวอย่าง |
| ต้นแบบเดิม | `app_v1.py` | เก็บไว้อ้างอิงเท่านั้น ห้ามแก้ไขโครงสร้าง |

### 2.2 องค์ประกอบสนับสนุน

| หมวด | ไฟล์ |
| :--- | :--- |
| ชุดทดสอบ | `test_*.py` 10 ไฟล์, `conftest.py` |
| การตั้งค่าเครื่องมือ | `pyproject.toml` (packaging, coverage, bandit), `.flake8`, `requirements.txt`, `requirements-dev.txt` |
| ระบบทดสอบอัตโนมัติ | `.github/workflows/tests.yml` (งาน `pytest` บน Python 3.10–3.12 และงาน `lint`) |
| การติดตั้งและกระจาย | `scripts/setup.cmd`, `scripts/setup.ps1`, `scripts/setup.sh`, `Dockerfile`, `.dockerignore` |
| การจัดการไฟล์ | `.gitignore`, `.gitattributes` |
| เอกสาร | `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `documents/`, `reports/` |

---

## ส่วนที่ 3: ประวัติการบำรุงรักษา (Maintenance History)

ตารางนี้รวบรวมคำขอเปลี่ยนแปลงและการบำรุงรักษาทุกรายการ จัดประเภทตาม ISO/IEC 14764 รายละเอียดการเปลี่ยนแปลงระดับไฟล์อยู่ใน [`CHANGELOG.md`](../CHANGELOG.md)

| ลำดับ | รหัส | รายการ | ประเภท | วันที่ | อ้างอิง | สถานะ |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | — | ต้นแบบ `app_v1.py` และ `app_v2.py` (tag `v1.0.0`) | — | ก.ค.–ส.ค. 2026 | PR #1–#4 | ✅ |
| 2 | SCRUM-4 ถึง 16 | ปรับโครงสร้างเป็นเชิงวัตถุ + SQLite (รอบพัฒนาที่ 1) | Perfective | 4–6 ก.ย. 2026 | PR #5–#19 | ✅ |
| 3 | CR-01 | บาร์โค้ดและการแจ้งเตือนตามจุดสั่งซื้อ | Perfective | 7 ก.ย. 2026 | PR #23 (`75af8d2`) | ✅ |
| 4 | CR-02 | ส่งออกรายการสินค้าใกล้หมดเป็น CSV (Emergency Change Request) | Perfective (Expedited) | 12 ก.ย. 2026 | PR #25 | ✅ |
| 5 | BUG-102 | บาร์โค้ดซ้ำ, คำเตือนใช้เกณฑ์ผิด, เมนู CSV ไม่เชื่อมส่วนติดต่อผู้ใช้ | Corrective | 13–14 ก.ย. 2026 | PR #27, #29 | ✅ |
| 6 | — | เขียนไฟล์แบบ atomic ตามทะเบียนความเสี่ยง | Preventive | 3 ต.ค. 2026 | `4e0a5b7` (PR #32) | ✅ |
| 7 | — | ผลตรวจ Flake8/Bandit เป็นศูนย์ และงาน `lint` ใน CI | Preventive | 3 ต.ค. 2026 | `6358919` | ✅ |
| 8 | — | ชุดทดสอบการทำงานร่วมกันและเกณฑ์ความครอบคลุม ≥ 90% | Preventive | 3 ต.ค. 2026 | `a7b0c73` | ✅ |
| 9 | — | กำหนดช่วงเวอร์ชันของเครื่องมือทดสอบ | Adaptive | 3 ต.ค. 2026 | `9b9497a` | ✅ |
| 10 | BUG-103 | ราคา `nan`/`inf` ทำให้โปรแกรมหยุดทำงาน | Corrective | 4 ต.ค. 2026 | `d347d8e` | ✅ |
| 11 | — | หัวข้อหน้าค้นหาแสดงเมนูผิด | Corrective | 4 ต.ค. 2026 | `0a33c8b` | ✅ |
| 12 | — | ย้อนการตัดสต็อกเมื่อบันทึกประวัติล้มเหลว | Preventive | 4 ต.ค. 2026 | `d6da33b` | ✅ |
| 13 | BUG-104 ถึง 108 | ข้อบกพร่องจากการทดสอบการยอมรับ 5 รายการ | Corrective | 4 ต.ค. 2026 | `3a5a207` | ✅ |
| 14 | — | สคริปต์ติดตั้งอัตโนมัติ | Adaptive | 4 ต.ค. 2026 | `73e7cfd` | ✅ |
| 15 | — | ชุดไฟล์กระจาย sdist, wheel และ Dockerfile | Adaptive | 5 ต.ค. 2026 | commit ที่ส่งมอบพร้อมแฟ้มนี้ | ✅ |
| 16 | — | อัปเกรด pip แก้ช่องโหว่ CVE-2026-13346 ในสคริปต์ติดตั้งและ Dockerfile | Preventive | 5 ต.ค. 2026 | commit ที่ส่งมอบพร้อมแฟ้มนี้ | ✅ |
| 17 | — | ปรับโครงสร้าง 6 ฟังก์ชันลด Cyclomatic Complexity สูงสุดจาก 10 เหลือ 6 โดยไม่เปลี่ยนพฤติกรรม | Preventive | 5 ต.ค. 2026 | commit ที่ส่งมอบพร้อมแฟ้มนี้ | ✅ |
| 18 | — | เพิ่มความปลอดภัยของ Docker image ตามผลสแกน Trivy (ถอน pip, ติดตั้ง security update ของ Debian) และสคริปต์ตรวจ `scripts/verify_docker.sh` | Preventive | 5 ต.ค. 2026 | commit ที่ส่งมอบพร้อมแฟ้มนี้ | ✅ |

**สรุปตามประเภท:** Perfective 3 รายการ, Corrective 4 กลุ่ม (ข้อบกพร่อง 8 รายการ รวมรายการที่ไม่มีรหัส), Preventive 7 รายการ, Adaptive 3 รายการ

---

## ส่วนที่ 4: บันทึกกระบวนการบำรุงรักษาตาม ISO/IEC 14764

| กิจกรรมตามมาตรฐาน | หลักฐานในโครงการนี้ |
| :--- | :--- |
| Process Implementation (วางกระบวนการ) | [`definition_of_done.md`](./definition_of_done.md), [`dod_per_feature.md`](./dod_per_feature.md), `CLAUDE.md`, คู่มือปฏิบัติการส่วนที่ 6 |
| Problem and Modification Analysis (วิเคราะห์ปัญหาและการแก้ไข) | รายงานคำขอเปลี่ยนแปลง [CR-01](./Change_Request_And_Impact_Analysis_Report.md) และ [CR-02](./Change_Request_And_Impact_Analysis_Report_CR02.md), ทะเบียนคำขอเปลี่ยนแปลงใน `README.md`, การจำแนกข้อบกพร่องและความต้องการใหม่ใน [รายงานการทดสอบการยอมรับ](./User_Acceptance_Testing_Report.md) ส่วนที่ 3 |
| Modification Implementation (ดำเนินการแก้ไข) | commit ตามรูปแบบ `fix:`/`feat:`/`build:` พร้อมรหัสอ้างอิง, เขียนชุดทดสอบให้ล้มเหลวก่อนแก้ทุกข้อบกพร่อง |
| Maintenance Review/Acceptance (ทบทวนและยอมรับ) | [`Scope_Freeze_Sign_off_Agreement.md`](./Scope_Freeze_Sign_off_Agreement.md), [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md), [`Project_Completion_Certificate.md`](./Project_Completion_Certificate.md) |
| Migration (ย้ายสภาพแวดล้อม) | [`Clean_Environment_Installation_Test.md`](./Clean_Environment_Installation_Test.md), [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md), การทดสอบความเข้ากันได้ของฐานข้อมูลระหว่างเวอร์ชันใน [`Disaster_Recovery_and_Rollback_Test_Report.md`](./Disaster_Recovery_and_Rollback_Test_Report.md) |
| Software Retirement (ปลดระบบ) | ต้นแบบ `app_v2.py` ถูกปลดแล้ว (PR #5–#10), `app_v1.py` เก็บไว้อ้างอิงตามคู่มือปฏิบัติการส่วนที่ 6.7 |

---

## ส่วนที่ 5: บันทึกการทวนสอบและการยืนยันความถูกต้อง

| การทดสอบ | ผลล่าสุด | เอกสาร |
| :--- | :--- | :--- |
| ชุดทดสอบหน่วยและการทำงานร่วมกัน | 158/158 ผ่าน, ความครอบคลุมร้อยละ 98.38 (หลังปรับโครงสร้างรายการที่ 17) | [`Smoke_And_Regression_Test_Report.md`](./Smoke_And_Regression_Test_Report.md), [`Technical_Metrics_Handover.md`](./Technical_Metrics_Handover.md) |
| การตรวจคุณภาพและความปลอดภัยของโค้ด | Flake8 0, Bandit 0 | [`reports/Code_Quality_And_Security_Scan_Report.md`](../reports/Code_Quality_And_Security_Scan_Report.md) |
| การตรวจช่องโหว่ของไลบรารีภายนอก | pip-audit 0 ช่องโหว่หลังอัปเกรด pip, Trivy บน Docker image: Python 0 และระบบปฏิบัติการที่มีแพตช์แล้ว 0 | [`Dependency_Security_Audit_Report.md`](./Dependency_Security_Audit_Report.md) |
| การทดสอบการยอมรับโดยผู้ใช้ | 16/16 สถานการณ์ในขอบเขตผ่าน ลงนามยอมรับแล้ว | [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md) |
| การทดสอบเบื้องต้นทุกเมนู | 8/8 เมนู | [`Smoke_And_Regression_Test_Report.md`](./Smoke_And_Regression_Test_Report.md) |
| การติดตั้งบนสภาพแวดล้อมใหม่ | ผ่านทุกขั้นตอนบน Windows และ Git Bash | [`Clean_Environment_Installation_Test.md`](./Clean_Environment_Installation_Test.md) |
| ชุดไฟล์กระจาย | sdist และ wheel ผ่าน 9/9, Docker image ผ่าน 11/11 | [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md) |
| การกู้คืนระบบและการถอยเวอร์ชัน | ผ่าน 5 สถานการณ์ | [`Disaster_Recovery_and_Rollback_Test_Report.md`](./Disaster_Recovery_and_Rollback_Test_Report.md) |

---

## ส่วนที่ 6: ตัวชี้วัดที่ส่งมอบ

| ตัวชี้วัด | ค่า | เอกสาร |
| :--- | :--- | :--- |
| ผลประเมินโครงการรวม | 4.42 จาก 5 (ดีมาก) | [`Project_KPI_Scorecard.md`](./Project_KPI_Scorecard.md) |
| Cyclomatic Complexity สูงสุด / เฉลี่ย | 6 / 2.51 (ต้นแบบ 14 / 5.67) | [`Technical_Metrics_Handover.md`](./Technical_Metrics_Handover.md) |
| ข้อบกพร่องที่พบ / แก้ไข / คงค้าง | 7 / 7 / 0 | [`Technical_KPI_Report.md`](./Technical_KPI_Report.md) |
| เวลากู้คืนฐานข้อมูลจากไฟล์สำรอง | 0.10 วินาที (เป้าหมาย RTO ที่เสนอ 15 นาที, RPO 1 วันทำการ) | [`Disaster_Recovery_and_Rollback_Test_Report.md`](./Disaster_Recovery_and_Rollback_Test_Report.md) |

---

## ส่วนที่ 7: งานคงค้างที่ส่งต่อ

### 7.1 ความต้องการใหม่ (Future Backlog สำหรับเวอร์ชัน 3.0)

| รหัส | รายการ | ลำดับความสำคัญ | ที่มา |
| :--- | :--- | :--- | :--- |
| FB-01 | เมนูรับสินค้าเข้าคลังที่บันทึกประวัติการเคลื่อนไหว | จำเป็นต้องมี | UAT-15 |
| FB-02 | หน้าจอยืนยันการแก้ไขแบบตาราง และคงค่าเดิมเมื่อกด Enter | ควรมี | UAT-03 |
| FB-03 | เกณฑ์ "สินค้าใกล้หมด" ของรายงานสรุป (รอผู้สนับสนุนโครงการตัดสิน) | ควรมี | UAT-11 |
| FB-04 | บาร์โค้ดแสดงครบทุกหลักใน Excel | มีได้หากมีเวลา | UAT-08 |
| FB-05 | จัดคอลัมน์ตารางให้ตรงเมื่อชื่อเป็นภาษาไทย | มีได้หากมีเวลา | UAT-17 |

### 7.2 รายการที่เสนอให้บันทึกเพิ่ม

| รหัสที่เสนอ | รายการ | ที่มา |
| :--- | :--- | :--- |
| BUG-109 | แสดงข้อความแนะนำแทน Traceback เมื่อไฟล์ฐานข้อมูลเสียหาย | DR-1 |
| FB-06 | แจ้งเตือนเมื่อสร้างฐานข้อมูลใหม่ และตรวจความสมบูรณ์ตอนเริ่มโปรแกรม | DR-2, DR-3 |
| BUG-110 | ไฟล์ CSV ที่ส่งออกบน Linux มีสิทธิ์ 0600 (อ่านได้เฉพาะเจ้าของ) เพราะ `AtomicFileWriter` ใช้ `tempfile.mkstemp()` | ทดสอบ Docker image ([`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md) ส่วนที่ 5.1) |

### 7.3 หนี้ทางเทคนิค

| รายการ | ประเภท | อ้างอิง |
| :--- | :--- | :--- |
| ไม่มีกลไกปรับโครงสร้างฐานข้อมูล (migration) | Adaptive | คู่มือปฏิบัติการส่วนที่ 6.6 |
| โมดูลอยู่ระดับบนสุดของ `site-packages` ด้วยชื่อทั่วไป และไม่มี console script | Adaptive | [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md) ส่วนที่ 6 |
| `inventory_app.py` มีค่า Maintainability Index ต่ำสุด (44.3) เพราะรวม 8 เมนูไว้ในคลาสเดียว (ความซับซ้อนรายฟังก์ชันแก้แล้วในรายการที่ 17) | Preventive | [`Technical_Metrics_Handover.md`](./Technical_Metrics_Handover.md) ส่วนที่ 2.3 |
| ไลบรารีที่เครื่องมือพัฒนาเรียกใช้ไม่ได้ระบุเวอร์ชันตายตัว | Adaptive | [`Dependency_Security_Audit_Report.md`](./Dependency_Security_Audit_Report.md) ส่วนที่ 5 |
| ยังไม่ได้ทดสอบสคริปต์ติดตั้งบน Linux/macOS จริง และ wheel บน Python 3.10–3.11 / Linux | Preventive | [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md) ส่วนที่ 6 |
| Docker image มีช่องโหว่ระบบปฏิบัติการที่ Debian ยังไม่ออกแพตช์ 166 รายการ | Preventive | [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md) ส่วนที่ 6 |
| ไลบรารีที่ pip 26.2.1 ฝังไว้ (`urllib3`, `msgpack`) มีช่องโหว่ ยังอยู่ใน venv ของนักพัฒนาและผู้ใช้จนกว่า pip จะออกรุ่นใหม่ | Preventive | [`Dependency_Security_Audit_Report.md`](./Dependency_Security_Audit_Report.md) ส่วนที่ 3.6 |
| แนวทางปรับปรุงสินทรัพย์กระบวนการ 11 รายการ | — | [`Lessons_Learned_Register.md`](./Lessons_Learned_Register.md) ส่วนที่ 3 |

---

## ส่วนที่ 8: รายการตรวจสอบการรับมอบ (Handover Checklist)

### 8.1 สิทธิ์และเครื่องมือ

| ลำดับ | รายการ | สถานะ |
| :---: | :--- | :---: |
| H1 | ได้รับสิทธิ์เขียนในคลังโค้ด GitHub และสิทธิ์ตั้งค่าการป้องกัน branch | ☐ |
| H2 | ได้รับสิทธิ์ในบอร์ด Jira (โครงการ `SCRUM`) | ☐ |
| H3 | ติดตั้งสภาพแวดล้อมด้วย `scripts\setup.cmd -Clean -Seed` หรือ `bash scripts/setup.sh --clean --seed` และผ่านทุกขั้นตอน | ☐ |
| H4 | ตรวจผล GitHub Actions ของ `main` ล่าสุดว่าผ่านทุกงาน | ☐ |

### 8.2 การถ่ายทอดความรู้

| ลำดับ | หัวข้อ | เอกสาร | สถานะ |
| :---: | :--- | :--- | :---: |
| K1 | โครงสร้างระบบ ข้อตกลงการเขียนโค้ด และข้อควรระวัง | `README.md`, `CLAUDE.md` | ☐ |
| K2 | การปฏิบัติงาน การสำรองและกู้คืนข้อมูล | [`System_Operations_and_Maintenance_Manual.md`](./System_Operations_and_Maintenance_Manual.md) | ☐ |
| K3 | กระบวนการรับคำขอเปลี่ยนแปลงและแก้ไขข้อบกพร่อง | คู่มือปฏิบัติการส่วนที่ 6, รายงาน CR-01/CR-02 เป็นแม่แบบ | ☐ |
| K4 | บทเรียนจากโครงการ | [`Lessons_Learned_Register.md`](./Lessons_Learned_Register.md) | ☐ |
| K5 | ซ้อมกู้คืนระบบด้วยตนเองหนึ่งครั้ง | [`Disaster_Recovery_and_Rollback_Test_Report.md`](./Disaster_Recovery_and_Rollback_Test_Report.md) | ☐ |

### 8.3 งานแรกที่ควรดำเนินการหลังรับมอบ

1. ดำเนินการตาม [`Release_Management_and_Board_Cleanup_Plan.md`](./Release_Management_and_Board_Cleanup_Plan.md) ได้แก่ ยืนยันผล CI สร้าง tag `v2.0.1` แนบชุดไฟล์กระจาย และปรับ `develop` ให้ตรงกับ `main`
2. ตั้งค่าการป้องกัน branch `main` และ `develop` ก่อนเริ่มงานเวอร์ชัน 3.0
3. เปิด PR การปรับโครงสร้างลดความซับซ้อน (รายการที่ 17) และการแก้ Dockerfile (รายการที่ 18) เข้า `develop` ให้ CI ผ่านและ QA อนุมัติ แล้ว build ชุดไฟล์กระจายใหม่จาก commit นั้นก่อนแนบ Release
4. พิจารณาบันทึก BUG-109, BUG-110 และ FB-06 อย่างเป็นทางการ
5. วางแผนเวอร์ชัน 3.0 โดยเริ่มจาก FB-01

---

## ส่วนที่ 9: ดัชนีเอกสาร

| หมวด | เอกสาร |
| :--- | :--- |
| ภาพรวมและประวัติ | [`README.md`](../README.md), [`CHANGELOG.md`](../CHANGELOG.md), [`CLAUDE.md`](../CLAUDE.md) |
| เกณฑ์และความเสี่ยง | [`definition_of_done.md`](./definition_of_done.md), [`dod_per_feature.md`](./dod_per_feature.md), [`risk_register_app_v1_emoji.md`](./risk_register_app_v1_emoji.md) |
| คำขอเปลี่ยนแปลง | [`Change_Request_And_Impact_Analysis_Report.md`](./Change_Request_And_Impact_Analysis_Report.md), [`Change_Request_And_Impact_Analysis_Report_CR02.md`](./Change_Request_And_Impact_Analysis_Report_CR02.md) |
| การยอมรับและปิดเฟส | [`Scope_Freeze_Sign_off_Agreement.md`](./Scope_Freeze_Sign_off_Agreement.md), [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md), [`Project_Completion_Certificate.md`](./Project_Completion_Certificate.md) |
| การทดสอบ | [`Smoke_And_Regression_Test_Report.md`](./Smoke_And_Regression_Test_Report.md), [`Clean_Environment_Installation_Test.md`](./Clean_Environment_Installation_Test.md), [`Disaster_Recovery_and_Rollback_Test_Report.md`](./Disaster_Recovery_and_Rollback_Test_Report.md), [`reports/Integration_Test_And_Coverage_Report.md`](../reports/Integration_Test_And_Coverage_Report.md) |
| ความปลอดภัยและการกระจาย | [`Dependency_Security_Audit_Report.md`](./Dependency_Security_Audit_Report.md), [`Package_Distribution_Artifact_Report.md`](./Package_Distribution_Artifact_Report.md), [`reports/Code_Quality_And_Security_Scan_Report.md`](../reports/Code_Quality_And_Security_Scan_Report.md) |
| การปฏิบัติการ | [`System_Operations_and_Maintenance_Manual.md`](./System_Operations_and_Maintenance_Manual.md) |
| ตัวชี้วัดและการประเมิน | [`Technical_KPI_Report.md`](./Technical_KPI_Report.md), [`Technical_Metrics_Handover.md`](./Technical_Metrics_Handover.md), [`Project_KPI_Scorecard.md`](./Project_KPI_Scorecard.md) |
| การปิดโครงการ | [`Lessons_Learned_Register.md`](./Lessons_Learned_Register.md), [`Release_Management_and_Board_Cleanup_Plan.md`](./Release_Management_and_Board_Cleanup_Plan.md) |
| หลักฐานดิบ | โฟลเดอร์ [`reports/`](../reports/) |

---

## ส่วนที่ 10: การส่งมอบและรับมอบ

| บทบาท | ชื่อ-นามสกุล | ลายมือชื่อ | วันที่ |
| :--- | :--- | :--- | :--- |
| ผู้จัดการโครงการ (ผู้ส่งมอบ) | | | ____/____/________ |
| หัวหน้าฝ่ายเทคนิค (ผู้ส่งมอบ) | | | ____/____/________ |
| ตัวแทนทีมผู้ดูแลระบบรุ่นถัดไป (ผู้รับมอบ) | | | ____/____/________ |
| ผู้สนับสนุนโครงการ (รับทราบ) | | | ____/____/________ |

---

## ภาคผนวก: ประวัติการแก้ไขเอกสาร

| ฉบับที่ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 5 ตุลาคม 2026 | จัดทำแฟ้มประวัติวิศวกรรมบำรุงรักษาฉบับสมบูรณ์ของเวอร์ชัน 2.0.1 สำหรับส่งมอบทีมผู้ดูแลรุ่นถัดไป |
| 1.1 | 5 ตุลาคม 2026 | เพิ่มรายการบำรุงรักษาที่ 17 (ลด Cyclomatic Complexity สูงสุดเหลือ 6) และ 18 (เพิ่มความปลอดภัย Docker image ตามผล Trivy) อัปเดตผลทดสอบ Docker image และเสนอ BUG-110 |
