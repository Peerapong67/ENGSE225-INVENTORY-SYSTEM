# SCOPE FREEZE SIGN-OFF AGREEMENT (เอกสารจำลองสัญญาล็อกขอบเขตระบบ)
**Academic Reference:** ISO/IEC 14764:2006 (Software Engineering — Software Life Cycle Processes — Maintenance), ISO/IEC 12207 (Configuration Management & Risk Management Process)
**Course Context:** ENGSE225 Software Evolution & Maintenance (Week 11 นำเสนอและเจรจา → Week 12 Scope Freeze)

> เอกสารฉบับนี้เป็น **เอกสารจำลอง (Mock Agreement)** สำหรับการเรียนการสอนในรายวิชา ENGSE225 ใช้ฝึกกระบวนการเจรจาขอบเขตงานและการลงนามยินยอมล็อกขอบเขตระบบกับ Sponsor ไม่ใช่สัญญาที่มีผลผูกพันทางกฎหมาย
>
> **สถานะเอกสาร:** ✅ **ลงนามแล้ว (จำลอง)** ฉบับ 1.0 วันที่ 2026-10-04 — ผู้ลงนามทุกคนเป็นบทบาทจำลอง ไม่ใช่ลายมือชื่อของบุคคลจริง (ดูส่วนที่ 6)

---

## ส่วนที่ 1: ข้อมูลเอกสาร (Agreement Identification)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **Agreement ID** | **SFA-01** |
| **Project Title** | Inventory Management System |
| **System Version ที่ล็อก** | **Version 2.0** (ระบบที่ refactor แล้ว: `inventory_app.py` + คลาสสนับสนุน + SQLite) — Version 1.0 คือต้นแบบ `app_v1.py` |
| **Baseline (Configuration Item)** | branch `main` ที่ commit **`f6d7e77`** (ณ วันลงนาม — โค้ดโปรแกรมตรงกับ `3a5a207` ซึ่งรวมการแก้ UAT Defect BUG-104 ถึง BUG-108 แล้ว) ตรงกับ Version 2.0.1 ใน [`CHANGELOG.md`](../CHANGELOG.md) — ร่างแรกของสัญญาอ้าง `c76c7b7` |
| **ช่วงเวลาล็อกขอบเขต (Freeze Period)** | ตลอด **สัปดาห์ที่ 12** จนถึงการส่งมอบงานครั้งสุดท้าย |
| **ผู้อนุมัติ (Sponsor)** | อาจารย์ผู้สอน / Sponsor ประจำวิชา |
| **ผู้เสนอ (Project Team)** | ทีมพัฒนา Inventory Management System (PM, Tech Lead, Developer, QA) |
| **Future Backlog Target** | **Version 3.0** (หลังสิ้นสุดภาคการศึกษา/รอบพัฒนาถัดไป) |

### 1.1 วัตถุประสงค์ของสัญญา
* **ปัญหาที่ต้องการป้องกัน:** ช่วงโค้งสุดท้ายก่อนส่งมอบ มักมีคำขอฟังก์ชันใหม่เข้ามาระหว่างนำเสนอผลงาน หากรับเข้ามาแทรกใน Sprint ปัจจุบัน ทีมจะต้องแก้โค้ดที่ผ่านการทดสอบและอนุมัติแล้ว โดยเหลือเวลาไม่พอสำหรับวงจร Test-First, Regression Test, QA Review และ Tech Lead Approve ตามที่กำหนดใน [`definition_of_done.md`](./definition_of_done.md)
* **วัตถุประสงค์:** ให้ Sponsor และทีมพัฒนาตกลงร่วมกันเป็นลายลักษณ์อักษรว่า ขอบเขตของ Version 2.0 ถูกล็อกไว้ตาม Baseline ในส่วนที่ 2 คำขอใหม่ทั้งหมดจะถูกบันทึกเข้า Future Backlog ตามส่วนที่ 3 และมีเพียงการแก้ไขตามเงื่อนไขในส่วนที่ 5 เท่านั้นที่อนุญาตในช่วง Freeze

---

## ส่วนที่ 2: ขอบเขตระบบที่ล็อก (Frozen Baseline Scope)
*(อ้างอิงตาม ISO/IEC 12207: Configuration Management — กำหนด Baseline ที่ใช้ส่งมอบ)*

### 2.1 ฟังก์ชันที่ส่งมอบใน Version 2.0

| เมนู | ฟังก์ชัน | ที่มา |
| :---: | :--- | :--- |
| 1 | แสดงสินค้าทั้งหมด แบ่งหน้าละ 10 รายการ | Sprint 1 (SCRUM-11, SCRUM-12) |
| 2 | เพิ่ม/แก้ไขสินค้า (Upsert) พร้อมยืนยันก่อนเขียนทับ รองรับ Barcode และ Reorder Point | Sprint 1 + CR-01 |
| 3 | ตัดสต็อก พร้อมเตือนเมื่อสต็อก ≤ Reorder Point และป้องกันสต็อกติดลบ | Sprint 1 + CR-01 |
| 4 | รายงานสรุป (จำนวนชนิด, หน่วยรวม, มูลค่ารวม, สินค้าใกล้หมด) | Sprint 1 |
| 5 | ค้นหาสินค้าตามชื่อหรือหมวดหมู่ แบ่งหน้า | Sprint 1 (SCRUM-12) |
| 6 | แจ้งเตือนสินค้าใกล้หมด (Low Stock Alerts) ตาม Reorder Point ของแต่ละสินค้า | CR-01 |
| 7 | Export รายงานสินค้าใกล้หมดเป็นไฟล์ CSV | CR-02 |
| 8 | ออกจากโปรแกรม | Sprint 1 |

### 2.2 รายการเปลี่ยนแปลงที่รวมอยู่ใน Baseline

| ID | รายการ | ประเภทตาม ISO/IEC 14764 | สถานะ |
| :---: | :--- | :--- | :--- |
| CR-01 | Barcode & Reorder Point Alert | Perfective | ✅ Merged (PR #23) |
| CR-02 | Export Low Stock Report เป็น CSV | Perfective (Expedited) | ✅ Merged (PR #25) |
| BUG-102 | Barcode ซ้ำ + Low Stock Alert อิง threshold ผิด + เมนู CSV ยังไม่เชื่อม UI | Corrective | ✅ Merged (PR #27, #29) |
| — | Atomic File Write สำหรับ `data.json` และไฟล์ CSV | Preventive | ✅ Merged (PR #32) |
| BUG-103 | ราคา `nan` ทำให้โปรแกรมพัง / ราคา `inf` ถูกบันทึกได้ | Corrective | ✅ แก้ไขและผ่านการทดสอบ |
| — | `updateStock` rollback เมื่อบันทึก `stock_movements` ล้มเหลว | Preventive | ✅ แก้ไขและผ่านการทดสอบ |
| BUG-104 ถึง BUG-108 | UAT Defects: Export CSV พังเมื่อ path ผิด, ตัวเลขเกินช่วง SQLite ทำให้พัง, ภาษาไทยเพี้ยนใน Excel, กด Enter ไม่ใช้ค่าเริ่มต้น Reorder Point, ตัดสต็อก 0 ชิ้นแล้วแจ้งสำเร็จ | Corrective | ✅ แก้ไขและผ่าน UAT Re-test รอบ 2 (`3a5a207`) |

### 2.3 สถานะคุณภาพ ณ Baseline

| เกณฑ์ | ผลลัพธ์ | เกณฑ์ผ่าน |
| :--- | :--- | :--- |
| PyTest (Unit + Integration) | 158 passed, 0 failed | ผ่านทั้งหมด |
| Code Coverage | 98.12% | ≥ 90% |
| Flake8 | 0 findings | 0 |
| Bandit | 0 issues | 0 |
| CI Matrix (GitHub Actions) | Python 3.10, 3.11, 3.12 + Lint job | ต้องเขียวทุก job |
| User Acceptance Testing (UAT-V2.0-01 รอบ 2) | 16/16 สถานการณ์ในขอบเขตผ่าน, FAIL 0 ([`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md)) | ไม่มี FAIL |

---

## ส่วนที่ 3: กลยุทธ์ Future Backlog และการบริหารความคาดหวัง (Future Backlog Strategy)

### 3.1 หลักการ
1. **ไม่ปฏิเสธคำขอ แต่ไม่แทรกงาน:** ทุกคำขอฟังก์ชันใหม่จาก Sponsor/อาจารย์ระหว่างการนำเสนอ ถือเป็นข้อมูลที่มีคุณค่า ทีมจะบันทึกไว้ครบทุกรายการ แต่จะ **ไม่นำเข้า Sprint ปัจจุบัน**
2. **บันทึกทันทีระหว่างนำเสนอ:** PM เป็นผู้จดคำขอลงตาราง Future Backlog (ข้อ 3.3) พร้อมให้ผู้ขอยืนยันความเข้าใจตรงกันก่อนจบการนำเสนอ
3. **ประเมินเบื้องต้นเท่านั้น:** ในช่วง Freeze ทีมจะประเมินผลกระทบแบบคร่าวๆ (ชั้นที่กระทบ, ประเภทงาน, Effort โดยประมาณ) เพื่อช่วยจัดลำดับใน Version 3.0 ส่วน Impact Analysis เต็มรูปแบบตามโครงสร้างรายงาน CR-01/CR-02 จะทำเมื่อเริ่มรอบพัฒนา Version 3.0
4. **เส้นทางเดียวที่แทรกงานได้:** คำขอที่เข้าเงื่อนไขข้อยกเว้นในส่วนที่ 5 เท่านั้น

### 3.2 แนวทางการตอบคำขอระหว่างนำเสนอ (Expectation Management Script)

| สถานการณ์ | แนวทางการตอบของทีม |
| :--- | :--- |
| Sponsor ขอฟังก์ชันใหม่ | "ขอบคุณสำหรับข้อเสนอครับ/ค่ะ ทีมขอบันทึกเป็นรายการ FB-xx ใน Future Backlog สำหรับ Version 3.0 เนื่องจาก Version 2.0 อยู่ในช่วงล็อกขอบเขตตามสัญญา SFA-01 เพื่อรักษาคุณภาพที่ผ่านการทดสอบแล้ว" |
| Sponsor ขอให้แก้ "นิดเดียว" ในสัปดาห์นี้ | อธิบายว่าแม้แก้โค้ดไม่กี่บรรทัด ก็ต้องผ่าน Test-First, Regression 145 เทสต์, CI ทั้ง 3 เวอร์ชัน Python, QA และ Tech Lead approve ตาม DoD แล้วชี้ความเสี่ยงในส่วนที่ 4 จากนั้นเสนอบันทึกเป็น FB-xx |
| Sponsor แจ้งว่าพบข้อผิดพลาด (Bug) | แยกให้ชัดว่าเป็น Bug หรือคำขอใหม่ หากเป็น Bug ระดับ Critical/Blocker ให้เข้าเส้นทางข้อยกเว้นในส่วนที่ 5 หากไม่ใช่ ให้บันทึกเป็น BUG-xxx และกำหนดแก้ใน Version 3.0 |
| Sponsor ยืนยันว่าต้องการภายในสัปดาห์ที่ 12 | ใช้เส้นทาง Emergency Change Request ในข้อ 5.3 ซึ่งต้องมีลายลักษณ์อักษรจาก Sponsor และยอมรับผลกระทบด้านเวลา/ความเสี่ยงที่ระบุ |

### 3.3 ตาราง Future Backlog (Version 3.0)

> FB-01 ถึง FB-05 มาจาก New Scope ที่พบใน [`User_Acceptance_Testing_Report.md`](./User_Acceptance_Testing_Report.md) ส่วนที่ 3.3 (Effort: S = ไม่เกินครึ่งวัน, M = 1–2 วัน)
>
> กรอกระหว่างหรือหลังการนำเสนอ ID ใช้รูปแบบ `FB-xx` เมื่อเริ่มพัฒนาใน Version 3.0 แต่ละรายการจะถูกยกระดับเป็น `CR-xx` หรือ `BUG-xxx` ตามกระบวนการ ISO/IEC 14764

| FB ID | คำขอ (Request) | ผู้ขอ / วันที่ | ประเภทตาม ISO/IEC 14764 | ชั้นที่กระทบ (UI / Validator / Product / Repository / schema.sql / Logger / CSV) | Effort ประมาณการ | Priority (MoSCoW) | สถานะ |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| FB-01 | เมนูรับสินค้าเข้าคลัง (Restock) เพิ่มยอดตามจำนวนรับเข้า และบันทึก `stock_movements` | UAT-15 / 2026-10-04 | Perfective | UI, Repository (`updateStock` มีอยู่แล้ว), Logger (Action ใหม่) | M | Must | Deferred → v3.0 |
| FB-02 | หน้าจอยืนยันการแก้ไขแบบตารางเทียบข้อมูลเดิม/ใหม่ และกด Enter เพื่อคงค่าเดิม | UAT-03 / 2026-10-04 | Perfective | UI, Validator | M | Should | Deferred → v3.0 |
| FB-03 | รายงานสรุป (เมนู 4) ใช้เกณฑ์ใกล้หมดเดียวกับ Reorder Point หรือแสดงทั้งสองเกณฑ์ | UAT-11 / 2026-10-04 | Perfective | UI, Repository (`getSummary`) | S | Should (รอ Sponsor ตัดสินเกณฑ์) | Deferred → v3.0 |
| FB-04 | Barcode แสดงครบทุกหลักเมื่อเปิดใน Excel (Export `.xlsx` หรือคอลัมน์ข้อความ) | UAT-08 / 2026-10-04 | Perfective | CSV | M | Could | Deferred → v3.0 |
| FB-05 | จัดคอลัมน์ตารางให้ตรงเมื่อชื่อสินค้าเป็นภาษาไทย | UAT-17 / 2026-10-04 | Perfective | UI | S | Could | Deferred → v3.0 |
| FB-06 | | | | | | | |

---

## ส่วนที่ 4: ความเสี่ยงของการแก้ไขโค้ดในโค้งสุดท้าย (Late-Change Risk Disclosure)
*(อ้างอิงตาม ISO/IEC 12207: Risk Management — ใช้ระดับเดียวกับ [`risk_register_app_v1_emoji.md`](./risk_register_app_v1_emoji.md))*

🔴 สูงมาก &nbsp;|&nbsp; 🟠 สูง &nbsp;|&nbsp; 🟡 ปานกลาง &nbsp;|&nbsp; 🟢 ต่ำ

| ความเสี่ยงหากแก้โค้ดในสัปดาห์ที่ 12 | ระดับ | เหตุผลเฉพาะของระบบนี้ | มาตรการภายใต้สัญญานี้ |
| :--- | :---: | :--- | :---: |
| เกิด Regression ในฟังก์ชันที่ผ่านการทดสอบแล้ว | 🔴 สูงมาก | ทุกชั้นเชื่อมกันผ่าน `InventoryApp` → `Validator` → `Product` → `ProductRepository` → SQLite แก้จุดเดียวอาจกระทบหลายเมนู | ล็อก Baseline |
| เปลี่ยนโครงสร้างฐานข้อมูลแล้วข้อมูลเดิมใช้ไม่ได้ | 🔴 สูงมาก | `schema.sql` ใช้ `CREATE TABLE IF NOT EXISTS` จึงไม่ปรับตารางที่มีอยู่แล้วใน `inventory.db` เดิม ระบบยังไม่มีกลไก Migration | ห้ามแก้ schema ช่วง Freeze |
| เทสต์เดิมล้มจำนวนมากเมื่อเปลี่ยนลำดับการถาม Input | 🟠 สูง | เทสต์ของ UI และ Integration Test จำลอง Input เป็นลำดับตายตัว เพิ่มคำถามเพียงข้อเดียวในเมนูจะต้องแก้เทสต์ทุกตัวที่ใช้เมนูนั้น | ห้ามเพิ่ม/ลด prompt ช่วง Freeze |
| Coverage ต่ำกว่า 90% หรือ Lint ไม่ผ่าน ทำให้ CI แดงก่อนส่งงาน | 🟠 สูง | CI บังคับ Coverage ≥ 90%, Flake8 = 0, Bandit = 0 บน Python 3.10–3.12 โค้ดที่เขียนเร่งรีบมักขาดเทสต์และ docstring | ทุกการแก้ต้อง CI เขียว |
| ข้ามขั้นตอน Review เพื่อให้ทันเวลา | 🟠 สูง | DoD กำหนด QA approve ก่อนเข้า `develop` และ Tech Lead approve ก่อนเข้า `main` การเร่งงานมักทำให้ขั้นตอนนี้ถูกข้าม | ห้าม push ตรงเข้า `main` |
| เอกสารไม่ตรงกับโค้ด (Traceability ขาด) | 🟡 ปานกลาง | README, รายงาน CR และ Change Request Log ต้องอัปเดตตามทุกการเปลี่ยนแปลง ที่ผ่านมาเคยพบจำนวนเทสต์และสถานะ CR ใน README ล้าสมัย | อนุญาตแก้เอกสาร (`docs:`) |
| เวลาไม่พอสำหรับ Manual Smoke Test และ Terminal Demo | 🟡 ปานกลาง | DoD ข้อ 2 กำหนด Manual Smoke Test อย่างน้อย 1 รอบ และแต่ละไฟล์เทสต์มี Terminal Demo ที่ pytest ไม่ได้รัน | ล็อก Baseline |

**สรุปการประเมิน:** หากรับคำขอใหม่เข้ามาแทรก ความเสี่ยงโดยรวมอยู่ในระดับ 🔴 สูงมาก เมื่อเทียบกับประโยชน์ที่ได้ในช่วงเวลาที่เหลือ ทีมจึงเสนอให้ล็อกขอบเขตตามสัญญานี้ ซึ่งลดความเสี่ยงคงเหลือ (Residual Risk) ของการส่งมอบ Version 2.0 ลงเป็น 🟢 ต่ำ

---

## ส่วนที่ 5: ข้อตกลงการล็อกขอบเขต (Terms of Scope Freeze)

### 5.1 สิ่งที่ห้ามทำในช่วง Freeze
1. ห้ามเพิ่มฟังก์ชันใหม่หรือขยายฟังก์ชันเดิม (งานประเภท **Perfective**) เข้า branch `develop` และ `main`
2. ห้ามแก้ไข `schema.sql` ทุกกรณี
3. ห้ามเปลี่ยนลำดับหรือจำนวนคำถาม Input ของเมนู 1–8 และห้ามเปลี่ยนชื่อ Action ใน `Logger` (`ADD_PRODUCT`, `UPDATE_PRODUCT`, `CUT_STOCK`, `SEARCH_PRODUCT`, `LOW_STOCK_ALERT_VIEWED`, `EXPORT_LOW_STOCK_CSV`)
4. ห้าม push ตรงเข้า `main` ทุกการเปลี่ยนแปลงต้องผ่าน Pull Request

### 5.2 สิ่งที่อนุญาตในช่วง Freeze
1. **Corrective สำหรับ Bug ระดับ Critical/Blocker เท่านั้น** ได้แก่ โปรแกรมหยุดทำงาน (Crash), ข้อมูลเสียหายหรือสูญหาย, หรือผลลัพธ์ผิดจนใช้งานเมนูนั้นไม่ได้ โดยต้อง:
   * ออก `BUG-xxx` และบันทึกใน Change Request Log ของ `README.md`
   * เขียนเทสต์ที่ fail ก่อนแก้ (Red → Green → Refactor)
   * Regression Test ผ่านทั้งหมด, Coverage ≥ 90%, Flake8/Bandit = 0, CI เขียวทุก job
   * QA approve และ Tech Lead approve ตาม [`definition_of_done.md`](./definition_of_done.md)
   * แจ้ง Sponsor ทราบเป็นลายลักษณ์อักษรภายในวันที่แก้ไข
2. **แก้ไขเอกสาร** (`docs:`) ที่ไม่เปลี่ยนพฤติกรรมของโปรแกรม เช่น README, รายงาน, docstring

### 5.3 Emergency Change Request ระหว่าง Freeze
คำขอที่ Sponsor ยืนยันว่าต้องได้ภายในสัปดาห์ที่ 12 ต้องผ่านเงื่อนไขครบทุกข้อ มิฉะนั้นให้บันทึกเข้า Future Backlog:
1. Sponsor ลงนามอนุมัติเป็นลายลักษณ์อักษร โดยระบุว่ายอมรับความเสี่ยงในส่วนที่ 4
2. ทีมจัดทำ `Change_Request_And_Impact_Analysis_Report_CRxx.md` ตามโครงสร้างรายงาน CR-01/CR-02 ก่อนเริ่มเขียนโค้ด
3. ปฏิบัติตามเงื่อนไขคุณภาพเดียวกับข้อ 5.2 (1) ทุกข้อ
4. หากทำไม่ทันภายในช่วง Freeze ให้ถอนการเปลี่ยนแปลงออก และส่งมอบตาม Baseline เดิม

### 5.4 การสิ้นสุดการล็อกขอบเขต
การล็อกขอบเขตสิ้นสุดเมื่อเกิดกรณีใดกรณีหนึ่ง:
1. ส่งมอบงานและนำเสนอครั้งสุดท้ายของสัปดาห์ที่ 12 เสร็จสิ้น
2. Sponsor และ PM ลงนามร่วมกันให้ยกเลิกสัญญานี้

หลังสิ้นสุด รายการใน Future Backlog จะถูกนำมาจัดลำดับเป็น Sprint Backlog ของ Version 3.0

---

## ส่วนที่ 6: การลงนามยินยอม (Sign-off)

ข้าพเจ้าได้อ่านและเข้าใจขอบเขตระบบ (ส่วนที่ 2), กลยุทธ์ Future Backlog (ส่วนที่ 3), ความเสี่ยงของการแก้ไขโค้ดในโค้งสุดท้าย (ส่วนที่ 4) และข้อตกลงการล็อกขอบเขต (ส่วนที่ 5) แล้ว และยินยอมให้ล็อกขอบเขตระบบ Inventory Management System Version 2.0 ตาม Baseline ที่ระบุ ตลอดสัปดาห์ที่ 12

| บทบาท | ชื่อ-นามสกุล | ลายมือชื่อ | วันที่ |
| :--- | :--- | :--- | :--- |
| **Sponsor / อาจารย์ผู้สอน** (ผู้อนุมัติ) | ผู้แทน Sponsor (จำลอง) | ✍️ /ลงนามจำลอง/ | 04/10/2026 |
| Project Manager (PM) | PM ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 04/10/2026 |
| Tech Lead | Tech Lead ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 04/10/2026 |
| Developer | Developer ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 04/10/2026 |
| QA | QA ทีม Inventory (จำลอง) | ✍️ /ลงนามจำลอง/ | 04/10/2026 |

### ความเห็นเพิ่มเติมของ Sponsor (ถ้ามี)

1. อนุมัติให้ล็อกขอบเขต Version 2.0 ตาม Baseline `f6d7e77` ตลอดสัปดาห์ที่ 12 ตามส่วนที่ 5
2. รับทราบการแก้ UAT Defect BUG-104 ถึง BUG-108 ก่อนวันลงนาม และยอมรับให้รวมอยู่ใน Baseline รวมถึง BUG-107 และ BUG-108 ที่เป็นระดับ Minor และทีมแจ้งไว้ในรายงาน UAT ส่วนที่ 5
3. เห็นชอบให้ FB-01 ถึง FB-05 ยกไป Version 3.0 ระหว่างการนำเสนอไม่มีคำขอใหม่เพิ่ม (แถว FB-06 ยังว่าง) สำหรับ FB-03 จะกำหนดเกณฑ์ "ใกล้หมด" ของรายงานสรุปตอนวางแผน Version 3.0

### บันทึกการลงนาม (Sign-off Record)

| หัวข้อ | รายละเอียด |
| :--- | :--- |
| **วันที่ลงนาม** | 2026-10-04 |
| **Baseline ที่ลงนาม** | `main` @ `f6d7e77` (Version 2.0.1) |
| **ผลการลงนาม** | ✅ ผู้ลงนามครบ 5/5 บทบาท สัญญามีผลตั้งแต่วันลงนามจนถึงการส่งมอบครั้งสุดท้ายของสัปดาห์ที่ 12 |
| **รูปแบบ** | การลงนามจำลองเพื่อการเรียนการสอน ผู้ลงนามเป็นบทบาทสมมติ ไม่ใช่ลายมือชื่อของบุคคลจริง |
| **การแก้ไขโค้ดหลังวันลงนาม** | ต้องเป็นไปตามข้อยกเว้นในส่วนที่ 5.2 หรือ 5.3 เท่านั้น |

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 0.1 | 2026-10-04 | ร่างแรก จัดทำก่อนการนำเสนอเพื่อยื่นให้ Sponsor ลงนาม |
| 0.2 | 2026-10-04 | บันทึก FB-01 ถึง FB-05 จากผล UAT รอบแรก (UAT-V2.0-01) ลงตาราง Future Backlog |
| 1.0 | 2026-10-04 | อัปเดต Baseline เป็น `f6d7e77` และสถานะคุณภาพหลังแก้ BUG-104 ถึง BUG-108 แล้วลงนามจำลองครบ 5 บทบาท |
