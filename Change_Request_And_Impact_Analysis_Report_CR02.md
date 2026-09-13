# CHANGE REQUEST & IMPACT ANALYSIS REPORT (CR-02)
**Academic Reference:** ISO/IEC 14764:2006 (Software Engineering — Software Life Cycle Processes — Maintenance), IEEE Std 1219-1998 (Software Maintenance Process)
**Course Context:** ENGSE225 Software Evolution & Maintenance (Week 10)

---

## ส่วนที่ 1: การบันทึกและจำแนกประเภทคำขอ (CR Identification & Logging)
*(อ้างอิงตาม ISO/IEC 14764 Clause 7.1: Step 1 Identification & Logging)*

| หัวข้อการบันทึก | ข้อมูลรายละเอียดของโครงการ |
| :--- | :--- |
| **Change Request ID** | **CR-02** |
| **Project Title** | Inventory Management System |
| **Date of Request** | สัปดาห์ที่ 10 (กึ่งกลาง Sprint 2 — Mid-Sprint Reality) |
| **Requester** | ลูกค้า (Customer) — ยื่นคำขอด่วนระหว่างรอบ Sprint |
| **Request Type** | **Emergency Change Request** — คำขอด่วนที่ต้องประเมินและตอบสนองเร็วกว่ากระบวนการ CR ปกติ |
| **Target Implementation** | Sprint 2 (แทรกกลาง Sprint แต่ไม่กระทบ Baseline เดิม) |
| **Maintenance Category** | **Perfective Maintenance (Expedited)** — ต่อเติมฟังก์ชันใหม่ตามคำขอลูกค้า ดำเนินการแบบเร่งด่วนกว่ากรณีปกติ |
| **Branch Assignment** | `feature/cr02-csv-export` (แตกกิ่งงานจาก `develop`) — ใช้ Feature Branch ไม่ใช่ Hotfix เพราะคำขอนี้รอรวมเข้าสาย `develop` ตามรอบ Sprint ปกติได้ ไม่ใช่บั๊กวิกฤตบน Production |

### 1.1 เหตุผลทางธุรกิจและขอบเขตข้อกำหนด (Business Justification)
* **ปัญหาเดิม:** ทีมจัดซื้อต้องดูรายชื่อสินค้าใกล้หมดผ่านเมนู Low Stock Alerts บนหน้าจอ Console เท่านั้น ไม่มีช่องทางนำข้อมูลออกไปใช้งานต่อนอกโปรแกรม (เช่น พิมพ์ใบสั่งซื้อ หรือส่งต่อให้ซัพพลายเออร์)
* **วัตถุประสงค์:** ให้ทีมจัดซื้อสามารถส่งออกรายชื่อสินค้าใกล้หมดเป็นไฟล์ที่เปิดใน Microsoft Excel ได้ทันที เพื่อนำไปสั่งซื้อสินค้าเติมคลังโดยไม่ต้องพิมพ์ข้อมูลซ้ำด้วยมือ
* **ขอบเขตการเปลี่ยนแปลง (Scope of Requirements):**
  1. **CSV Export Function:** ส่งออกรายชื่อสินค้าที่ `is_low_stock() == True` เป็นไฟล์ `.csv` พร้อม Header ครบ 6 คอลัมน์: `ProductID, ProductName, Barcode, Quantity, ReorderPoint, Price`
  2. **Single Responsibility Design:** แยกคลาส `CsvReportExporter` เป็นอิสระจาก UI (`ConsoleUI`) และ `InventoryRepository` เดิมโดยสิ้นเชิง ออกแบบเป็น Static Method ไร้ State เพื่อทดสอบแยกส่วนได้ง่าย ไม่ผูกติด Tight Coupling กับชั้นอื่น
  3. **UTF-8 Encoding & Safe File Handling:** ใช้ Context Manager (`with open`) จัดการปิดไฟล์อัตโนมัติ กำหนด Encoding `utf-8` รองรับข้อมูลภาษาไทยสมบูรณ์

---

## ส่วนที่ 2: การประเมินผลกระทบเชิงเทคนิค (Impact Analysis Framework)
*(อ้างอิงตาม ISO/IEC 14764 Clause 7.2: Step 2 Impact Analysis)*

### 2.1 ตารางวิเคราะห์ความเชื่อมโยงของผลกระทบ (Traceability Matrix)

| องค์ประกอบสถาปัตยกรรม (Architecture Component) | จุดกระทบเชิงเทคนิคที่ต้องปรับแก้ (Affected Code) | ผลกระทบด้านการทดสอบ (Test Impact) |
| :--- | :--- | :--- |
| **CsvReportExporter** (คลาสใหม่ — Presentation-independent) | • สร้างคลาสใหม่ทั้งหมด ไม่มีในระบบเดิมมาก่อน<br>• เมธอด `export_low_stock_products(products, output_path) -> int` เป็น `@staticmethod` ไร้ State<br>• ไม่ import `ProductRepository`/UI เข้ามาโดยตรง รับแค่ `List[Product]` ที่ถูกส่งเข้ามาเท่านั้น (Dependency Inversion) | เพิ่ม Unit Test ตรวจ Header ครบ 6 คอลัมน์, ตรวจ Filtering Logic (กรองเฉพาะ `is_low_stock()==True`), และ Edge Case กรณีไม่มีสินค้าต่ำเลย (0 แถว แต่ยังต้องสร้างไฟล์) |
| **InventoryApp / ConsoleUI** (Presentation & Service) | • เพิ่มเมนูใหม่เรียก `CsvReportExporter.export_low_stock_products()` โดยส่ง `repo.findAll()` เข้าไปทั้งหมด (ตัวกรองสินค้าต่ำอยู่ใน Exporter เอง ไม่กรองซ้ำที่ UI)<br>• รับ Input ชื่อไฟล์ปลายทางจากผู้ใช้ | ทดสอบ UI Mock Input ชื่อไฟล์ปลายทาง และยืนยันว่า `Logger` บันทึก Action `EXPORT_LOW_STOCK_CSV` ทุกครั้งที่เรียกใช้ |
| **Product** (Domain Model) | ไม่ต้องแก้โค้ดเพิ่ม — ใช้เมธอด `is_low_stock()` ที่มีอยู่แล้วจาก CR-01 โดยตรง (Reuse โครงสร้างเดิม ไม่สร้าง Logic ซ้ำ) | ไม่มี Test เพิ่มในชั้นนี้ (ครอบคลุมแล้วโดย Test Suite ของ CR-01) |

### 2.2 การประมาณการทรัพยากร (Resource & Effort Estimation)

| องค์ประกอบงานทางเทคนิค (Task Breakdown) | ผู้รับผิดชอบ (Role) | Man-Hours | ระดับความเสี่ยง |
| :--- | :--- | :---: | :---: |
| 1. สร้างคลาส `CsvReportExporter` | Senior Developer | 2.0 ชม. | Low 🟢 |
| 2. เชื่อมโยงเมนู Console UI | Developer | 1.0 ชม. | Low 🟢 |
| 3. เขียน Unit Test ครอบคลุมไฟล์ CSV | QA Tester | 1.5 ชม. | Low 🟢 |
| **รวม Technical Effort ทั้งสิ้น** | | **4.5 Man-Hours** | **Overall: Low Risk** |

* **Cost Impact ส่งต่อวิชา SPM (ENGSE202):** ส่งมอบตัวเลข 4.5 Man-Hours ให้ Project Manager นำเข้าที่ประชุม Change Control Board (CCB) เพื่อเจรจากับลูกค้าและบันทึก Work Log สำหรับคำนวณ Cost Variance ($CV = EV - AC$)

---

## ส่วนที่ 3: แผนการทดสอบแบบ Test-Driven Refinement (TDR Design)
*(อ้างอิงตาม TDD in Maintenance: วงจร Red-Green-Refactor)*

การต่อเติมฟังก์ชัน CR-02 เขียน PyTest ดักตรรกะก่อนลงมือเขียนฟังก์ชันจริงเสมอ เพื่อป้องกันโค้ดส่วนเกินที่ลูกค้าไม่ได้สั่ง:

1. **🔴 RED Phase:** เขียน Test Case ตรวจสอบ Header และ Filtering Logic ของ `CsvReportExporter` แล้วสั่งรัน `pytest` → ต้องติดสถานะ **Fail (สีแดง)** เนื่องจากยังไม่มีคลาสจริง
2. **🟢 GREEN Phase:** เขียนโค้ดสั้นที่สุดในคลาส `CsvReportExporter` → สั่งรัน `pytest` ให้ผ่าน **Pass (สีเขียว 100%)**
3. **🔵 REFACTOR Phase:** ปรับปรุงโครงสร้างโค้ดให้สะอาดตามหลัก Single Responsibility โดยรักษาสภาวะ PyTest ให้ผ่านไฟเขียวสม่ำเสมอ

### 3.1 การออกแบบเคสทดสอบขอบเขต (Edge Cases Design)

| Test Case ID | กรณีเงื่อนไขขอบเขต (Test Condition) | ตรรกะการตรวจสอบ | ผลลัพธ์คาดหวัง (Expected Result) |
| :---: | :--- | :--- | :--- |
| **TC-CSV-01** | สินค้าสต็อกต่ำ 1 รายการ (มี barcode และ reorder_point ครบ) | เขียนไฟล์ CSV แล้วอ่านกลับมาตรวจ Header + แถวข้อมูล | Header ครบ 6 คอลัมน์ (`ProductID, ProductName, Barcode, Quantity, ReorderPoint, Price`) และแถวข้อมูลตรงกับสินค้าที่ส่งเข้าไปทุกช่อง 🟢 |
| **TC-CSV-02** | สินค้า 2 ชิ้น: P01 ต่ำ (qty=2, reorder_point=5), P02 ปกติ (qty=100, reorder_point=5) | ฟังก์ชันกรองด้วยการเรียก `p.is_low_stock()` ของแต่ละ Product เอง (Delegation) | เขียนลงไฟล์แค่ 1 แถว (เฉพาะ P01) ตัด P02 ออกจากไฟล์ทั้งที่อยู่ใน list ที่ส่งเข้ามา 🔴/🟢 |
| **TC-CSV-03** | สินค้าทุกชิ้นมี `quantity` มากกว่า `reorder_point` ทั้งหมด (ไม่มีตัวไหนสต็อกต่ำเลย) | เรียก `export_low_stock_products()` กับ list ที่ไม่มีสินค้าต่ำเลย | คืนค่า **0 แถว** แต่ยัง**สร้างไฟล์พร้อม Header ไว้เสมอ** ไม่ throw Exception แม้ไม่มีข้อมูลให้เขียน 🟢 |
| **TC-CSV-04** | ตรวจสอบว่า `export_low_stock_products` เป็น `@staticmethod` จริง | `isinstance(CsvReportExporter.__dict__["export_low_stock_products"], staticmethod)` | คืนค่า `True` — ยืนยันว่าเรียกใช้ได้โดยไม่ต้องสร้าง instance และไม่มี State แยกอิสระจาก UI/Repository ตาม Single Responsibility ที่กำหนดไว้ในขอบเขต |
