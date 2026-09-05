# Inventory Management System (ENGSE225)

ระบบจัดการคลังสินค้าแบบ CLI ภาษา Python ร่วมกับฐานข้อมูล SQLite และระบบทดสอบอัตโนมัติ PyTest บน GitHub Actions CI/CD[cite: 25, 27, 33]

---

## 1. ภาพรวมสถาปัตยกรรม (Layered Architecture)

* **Presentation Layer (`inventory_app.py`):** เมนู CLI หลัก (แสดงสินค้า, เพิ่ม/แก้, ตัดสต็อก, รายงานสรุป, ค้นหา) พร้อมระบบแบ่งหน้า (Pagination) หน้าละ 10 รายการ
* **Validation Layer (`validator.py`):** ตรวจสอบ input ตัวเลขไม่ให้ติดลบ ป้องกัน crash และยืนยันการบันทึกทับข้อมูลเดิม (`confirm`)[cite: 11]
* **Domain Layer (`product.py`):** Data Model ของสินค้า มี validation ดักจับค่าติดลบตั้งแต่ constructor[cite: 32]
* **Persistence Layer (`product_repository.py`):** จัดการข้อมูลผ่าน Parameterized Query, ฟังก์ชัน upsert ป้องกันข้อมูลซ้ำ และตัดสต็อกพร้อมบันทึกลง `stock_movements`[cite: 16]
* **Infrastructure Layer (`database_connection.py`, `logger.py`):** จัดการ connection เดียวทั้งระบบ (Singleton) และบันทึกประวัติการแก้ไขลง `action_logs`[cite: 27, 31]

---

## 2. โครงสร้างไฟล์ในระบบ

```text
.
├── .github/workflows/tests.yml   # CI/CD Pipeline ทดสอบ PyTest บน Python 3.10, 3.11, 3.12
├── .gitignore                    # กันไฟล์ขยะขึ้น Git (.db, .pyc, venv, cache)
├── app_v1.py                     # ระบบเดิมก่อนรีแฟกทอรี
├── conftest.py                   # PyTest Fixtures สำหรับแยก DB ทดสอบชั่วคราว
├── database_connection.py        # SQLite Singleton Connection
├── definition_of_done.md         # เกณฑ์คุณภาพกลางของทีม (DoD)
├── dod_per_feature.md            # DoD แยกตามฟีเจอร์
├── inventory_app.py              # จุดรันโปรแกรมหลัก (CLI Menu)
├── logger.py                     # Singleton Logger
├── product.py                    # Class Product
├── product_repository.py         # Data Access Layer
├── schema.sql                    # โครงสร้างตารางฐานข้อมูล SQLite
└── validator.py                  # Class ตรวจสอบ Input
```
