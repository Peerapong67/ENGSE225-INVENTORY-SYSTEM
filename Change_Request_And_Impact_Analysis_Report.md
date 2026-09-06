# CHANGE REQUEST & IMPACT ANALYSIS REPORT (CR-01)
**Academic Reference:** ISO/IEC 14764:2006 (Software Engineering — Software Life Cycle Processes — Maintenance)[cite: 24]  
**Course Context:** ENGSE225 Software Evolution & Maintenance (Week 8 & Week 9)

---

## ส่วนที่ 1: การบันทึกและจำแนกประเภทคำขอ (CR Identification & Logging)
*(อ้างอิงตาม ISO/IEC 14764 Clause 7.1: Step 1 Identification & Logging)*[cite: 24]

| หัวข้อการบันทึก | ข้อมูลรายละเอียดของโครงการ |
| :--- | :--- |
| **Change Request ID** | **CR-01**[cite: 24] |
| **Project Title** | Inventory Management System[cite: 24, 25] |
| **Date of Request** | สัปดาห์ที่ 8 (Execution Phase / Sprint 1 Transition)[cite: 24, 25] |
| **Requester** | อาจารย์ผู้สอน / Sponsor ประจำวิชา[cite: 24] |
| **Target Implementation** | Sprint 2 (ไม่แทรกโค้ดจริงใน Sprint 1 เพื่อป้องกัน Scope Creep)[cite: 24, 25] |
| **Maintenance Category** | **Perfective Maintenance** (ISO/IEC 14764: การบำรุงรักษาเพื่อปรับปรุงประสิทธิภาพและต่อเติมฟังก์ชันใหม่ตามความต้องการ) |
| **Branch Assignment** | `feature/cr01-barcode-reorder-point` (แตกกิ่งงานจาก `develop`)[cite: 24, 25] |

### 1.1 เหตุผลทางธุรกิจและขอบเขตข้อกำหนด (Business Justification)
* **ปัญหาเดิม:** ระบบคลังสินค้าดั้งเดิมมีเพียงการกรอก Product ID ด้วยตนเอง ซึ่งเสี่ยงต่อ Human Error และไม่มีกลไกแจ้งเตือนเมื่อสต็อกสินค้าลดลงจนใกล้หมด[cite: 24, 25]
* **วัตถุประสงค์:** ยกระดับคลังสินค้าดั้งเดิมให้กลายเป็นระบบอัจฉริยะ (Smart Inventory)
* **ขอบเขตการเปลี่ยนแปลง (Scope of Requirements):**
  1. **Barcode Field:** เพิ่มการเก็บข้อมูลรหัสบาร์โค้ดประจำสินค้าในรูปแบบ String เพื่อรองรับการใช้งานร่วมกับเครื่องสแกนบาร์โค้ด[cite: 25]
  2. **Reorder Point Field:** กำหนดเกณฑ์สต็อกขั้นต่ำในรูปแบบ Integer เพื่อเป็นเกณฑ์ตัดสินใจเตือนภัยการสั่งเติมสินค้า[cite: 25]
  3. **Low Stock Alert:** เพิ่มระบบคัดกรองและแจ้งเตือนอัตโนมัติเมื่อจำนวนสินค้าคงเหลือถึงจุดวิกฤต (`quantity <= reorder_point`)[cite: 25]

---

## ส่วนที่ 2: การประเมินผลกระทบเชิงเทคนิค (Impact Analysis Framework)
*(อ้างอิงตาม ISO/IEC 14764 Clause 7.2: Step 2 Impact Analysis)*[cite: 24]

### 2.1 ตารางวิเคราะห์ความเชื่อมโยงของผลกระทบ (Traceability Matrix)

| องค์ประกอบสถาปัตยกรรม (Architecture Component) | จุดกระทบเชิงเทคนิคที่ต้องปรับแก้ (Affected Code) | ผลกระทบด้านการทดสอบ (Test Impact) |
| :--- | :--- | :--- |
| **Class Product** (Domain Model)[cite: 24] | • เพิ่ม Attribute `barcode: str = ""`[cite: 24, 25]<br>• เพิ่ม Attribute `reorder_point: int = 5`[cite: 24, 25]<br>• เพิ่มเมธอด `is_low_stock(self) -> bool`[cite: 25]<br>• รักษา **Backward Compatibility** โดยกำหนด Default Value เสมอ เพื่อไม่ให้โค้ดเก่าที่สร้าง Product พัง[cite: 25] | เพิ่ม Unit Test ตรวจสอบชนิดข้อมูล (Data Types) และค่า Default ของ Barcode และ Reorder Point[cite: 24, 25] |
| **InventoryRepository** (Data Access Layer)[cite: 24] | • ปรับโครงสร้าง JSON/Database Serialization & Deserialization ให้รองรับคีย์ใหม่ (`barcode`, `reorder_point`)[cite: 24]<br>• เพิ่มเมธอด `get_low_stock_alerts() -> List[Product]` สำหรับกรองสินค้าวิกฤต[cite: 25] | เพิ่ม Test Case การอ่าน/เขียนไฟล์ และการบันทึกคีย์ใหม่ลง Persistence Layer[cite: 24] |
| **InventoryService / ConsoleUI** (Presentation & Service)[cite: 24, 25] | • เพิ่มช่องรับ Input Barcode และ Reorder Point[cite: 24]<br>• แสดงผลการแจ้งเตือน Reorder Alert เมื่อพบสินค้าสต็อกต่ำ[cite: 24]<br>• กักตัว Business Logic ไว้ใน Service Layer 100% ไม่ปะปนกับ `print()` บน Console UI[cite: 25] | ทดสอบ UI Mock Inputs และจำลอง Input ทาง CLI แบบครอบคลุม[cite: 24] |

### 2.2 การประมาณการทรัพยากร (Resource & Effort Estimation)
* **Technical Effort รวม:** ประมาณการ **8 Man-Hours**[cite: 24]
  * ดัดแปลงและขยาย Data Model คลาส `Product`: 2 ชั่วโมง[cite: 24, 25]
  * ปรับแต่ง Data Access Layer (`InventoryRepository`) และ Serialization: 3 ชั่วโมง[cite: 24]
  * พัฒนาเมธอดคัดกรองใน Service Layer และ Console UI: 1 ชั่วโมง[cite: 24, 25]
  * ออกแบบและเขียนชุดทดสอบแบบ TDR บน PyTest: 2 ชั่วโมง[cite: 24, 25]
* **Cost Impact ส่งต่อวิชา SPM (ENGSE202):** นำชั่วโมง 8 Man-Hours ไปบันทึก Work Log เพื่อคำนวณ Cost Variance ($CV = EV - AC$) และวางแผนตัดงบประมาณชดเชยจาก Contingency Reserve[cite: 24, 25]

---

## ส่วนที่ 3: แผนการทดสอบแบบ Test-Driven Refinement (TDR Design)
*(อ้างอิงตาม TDD in Maintenance: วงจร Red-Green-Refactor สำหรับ CR-01)*[cite: 25]

การต่อเติมฟังก์ชัน CR-01 จะต้องเขียน PyTest ดักตรรกะก่อนลงมือเขียนฟังก์ชันจริงเสมอเพื่อป้องกันโค้ดส่วนเกิน[cite: 25]:

1. **🔴 RED Phase:** เขียน Test Case ตรวจสอบ Reorder Point แล้วสั่งรัน `pytest` $\rightarrow$ ต้องติดสถานะ **Fail (สีแดง)** เนื่องจากระบบยังไม่มีฟิลด์และเมธอดจริง[cite: 25]
2. **🟢 GREEN Phase:** เขียนโค้ดสั้นที่สุดในคลาส `Product` และ `InventoryService` $\rightarrow$ สั่งรัน `pytest` ให้ผ่าน **Pass (สีเขียว 100%)**[cite: 25]
3. **🔵 REFACTOR Phase:** ปรับปรุงโครงสร้างโค้ดให้สะอาดตามหลัก Clean Code โดยรักษาสภาวะ PyTest ให้ผ่านไฟเขียวสม่ำเสมอ[cite: 25]

### 3.1 การออกแบบเคสทดสอบขอบเขต (Edge Cases Design)

| Test Case ID | กรณีเงื่อนไขขอบเขต (Test Condition) | ตรรกะการตรวจสอบ | ผลลัพธ์คาดหวัง (Expected Result) |
| :---: | :--- | :---: | :---: |
| **TC-CR01-01**[cite: 25] | จำนวนคงเหลือน้อยกว่าเกณฑ์สั่งซื้อ[cite: 25] | `quantity (3) < reorder_point (5)`[cite: 25] | `is_low_stock() == True` 🔴 (Alert แจ้งเตือน)[cite: 25] |
| **TC-CR01-02**[cite: 25] | จุดขอบเขต: จำนวนเท่ากับเกณฑ์พอดี[cite: 25] | `quantity (5) == reorder_point (5)`[cite: 25] | `is_low_stock() == True` 🔴 (Alert แจ้งเตือน)[cite: 25] |
| **TC-CR01-03**[cite: 25] | ปริมาณสต็อกยังปลอดภัย[cite: 25] | `quantity (6) > reorder_point (5)`[cite: 25] | `is_low_stock() == False` 🟢 (Normal สภาวะปกติ)[cite: 25] |