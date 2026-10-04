# Definition of Done แยกตามแต่ละ Feature — Sprint 1

เอกสารนี้ดึง "Definition of done" เฉพาะของแต่ละ ticket จากไฟล์ `sprint1_work_plan.md` มาเรียบเรียงเป็น checklist ที่ใช้เช็คได้จริง **ต้องใช้คู่กับ [`definition_of_done.md`](./definition_of_done.md)** ซึ่งเป็นเกณฑ์คุณภาพกลางที่ใช้กับทุก ticket เหมือนกันหมด (code เสร็จ, ผ่าน lint, ผ่าน CI/CD, QA/Tech Lead approve ตามระดับ branch ฯลฯ) — เอกสารนี้เป็นแค่ส่วนที่ "เพิ่มเติมเฉพาะของงานนั้น" เท่านั้น

ลำดับการเช็ค: ✅ DoD กลาง (ทุกข้อ) → ✅ DoD เฉพาะ feature (ด้านล่าง) → ปิด ticket เป็น Done

---

### SCRUM-4 — วางแผนโครงการ + ประสานงานทีม (P)
- [x] มี sprint backlog ที่ทีมเข้าใจ scope ตรงกัน กำหนด timeline ชัดเจน

### SCRUM-5 — ออกแบบ Database Schema (SQLite) (PY)
- [ ] ไฟล์ `schema.sql` มีตาราง `products` (product_id, name, category, quantity, price), `stock_movements`, `action_logs` ครบ
- [ ] มี CHECK constraint ป้องกัน quantity/price ติดลบ และ index บน name/category
- [ ] แนบตัวอย่าง query ให้ NJ ใช้อ้างอิงสำหรับทุกเมธอดของ `ProductRepository` (upsert, findById, findAll, search, updateStock, getSummary)

### SCRUM-6 — สร้างคลาส DatabaseConnection (NJ)
*รอ SCRUM-5*
- [ ] เขียน/อ่าน/แก้ข้อมูลผ่าน connection เดียวได้จริง
- [ ] เรียก `getInstance()` ซ้ำจากหลายจุด ได้ instance เดียวกันเสมอ ไม่เปิด connection ซ้ำซ้อน
- [ ] `beginTransaction()` / `commit()` / `rollback()` ทำงานถูกต้องตาม transaction จริง

### SCRUM-8 — สร้างคลาส Product (NJ)
*ไม่ต้องรอใคร*
- [ ] สร้าง object แล้วส่งต่อให้ `ProductRepository` ใช้งานได้ทันที
- [ ] Constructor ปฏิเสธค่าที่ quantity หรือ price ติดลบ

### SCRUM-9 — สร้างคลาส Validator (NJ)
*ไม่ต้องรอใคร*
- [ ] `InventoryApp` เรียกใช้แทนการเช็ค input เองได้ทั้งหมด (ไม่มีจุดไหนใน `InventoryApp` เช็ค input ตรงๆ เอง)

### SCRUM-10 — สร้างคลาส Logger (Singleton) (NJ)
*ไม่ต้องรอใคร*
- [ ] ทุก action สำคัญ (เพิ่ม/แก้/ตัดสต็อก) มี log ตามหลังอัตโนมัติ บันทึกลง `action_logs` สำเร็จ

### SCRUM-7 — สร้างคลาส ProductRepository (NJ)
*รอ SCRUM-6 + SCRUM-8*
- [ ] ทุกเมธอด (`upsertProduct`, `findById`, `findAll`, `search`, `updateStock`, `getSummary`) ทดสอบผ่านกับฐานข้อมูลจริง **ไม่ใช่ mock**
- [ ] `updateStock` อัปเดตทั้งตาราง `products` และบันทึกลง `stock_movements` พร้อมกันทุกครั้ง

### SCRUM-11 — Refactor InventoryApp (เมนูหลัก) (PY)
*รอ SCRUM-7 + SCRUM-9 + SCRUM-10*
- [ ] รันโปรแกรมแล้วใช้งานได้ครบทุกเมนู (`run`, `showMenu`, `addOrUpdateProduct`, `cutStock`, `showReport`, `searchProduct`) โดยไม่ error
- [ ] ทุก action ที่แก้ข้อมูลเรียก `Logger.log()` ต่อท้ายจริง

### SCRUM-12 — เพิ่มฟีเจอร์ค้นหา + แบ่งหน้าแสดงผล (NJ)
*รอ SCRUM-7 + SCRUM-11*
- [ ] ค้นหาด้วยชื่อหรือหมวดหมู่ได้ผลลัพธ์ถูกต้อง
- [ ] ผลลัพธ์จำนวนมากแสดงแบบแบ่งหน้า ไม่ล้นหน้าจอ

### SCRUM-13 — เขียน Unit Test (PyTest) (BS)
*เริ่มทยอยทำได้ตั้งแต่แต่ละคลาสในเฟส 2-3 เสร็จ*
- [ ] test suite รันผ่านทั้งหมด ครอบคลุม happy path + edge case หลักๆ (ค่าติดลบถูกปฏิเสธ, upsert ซ้ำ id เดิมอัปเดตไม่สร้างซ้ำ)
- [ ] มี test แยกตามคลาส (Product, Validator, Logger, ProductRepository) โดยใช้ database ทดสอบแยกจาก production

### SCRUM-14 — Integration Testing + แก้บั๊ก (BS)
*รอ SCRUM-11 + SCRUM-12*
- [ ] ใช้งานทุกเมนูจาก UI จริงได้ครบโดยไม่ error
- [ ] บั๊กที่พบถูกแก้และ verify ซ้ำแล้ว ไม่ใช่แค่รายงานทิ้งไว้

### SCRUM-15 — เขียน Docstring/Comment (BS)
*ทำคู่ขนานกับ SCRUM-13 ได้*
- [ ] ทุกเมธอด public ในทุกคลาสมี docstring ครบ ไม่ขาดแม้แต่ตัวเดียว

### SCRUM-16 — Code Review + ปรับปรุงตามข้อเสนอแนะ (PY)
*ทำต่อเนื่องทีละ ticket ไม่ใช่รวบทำท้าย sprint*
- [ ] ทุก ticket ที่รีวิวแล้วมี comment สรุปผลใน PR
- [ ] ข้อเสนอแนะที่ให้ไว้ถูกแก้ไขจริง หรือมีเหตุผลชี้แจงหากไม่แก้

---

**จุดที่ควรระวังจาก work plan (อ้างอิงถึงตอนเช็ค DoD):** SCRUM-6, 7, 8, 9, 10, 12 อยู่ที่ NJ คนเดียวและเป็น critical path เกือบทั้งสาย ถ้า SCRUM-5 (blocker หลัก) ล่าช้า ทุก DoD ด้านบนของเฟส 2 เป็นต้นไปจะขยับตามหมด ควรติดตามความคืบหน้า SCRUM-5 และ SCRUM-6/7 เป็นพิเศษตามที่ระบุไว้ในแผนงาน
