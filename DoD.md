# Definition of Done (DoD)

> ขอบเขต: กระบวนการตั้งแต่ Developer พัฒนาโค้ด จนถึงการ Merge ขึ้น `main`
> โปรเจกต์: E-Filing Document Control System (ISO 9001:2015) — SE02

---

## 🔁 ภาพรวม Flow

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌────────┐
│  Developer   │ ──▶ │  Branch QA/Tester │ ──▶ │  Tech Lead       │ ──▶ │  main  │
│  เขียน Code  │     │  QA/Tester ทดสอบ   │     │  ตรวจสอบ & Approve │     │        │
│  + Unit Test │     │  + readme_tester  │     │  (1 approval)    │     │        │
└─────────────┘     └──────────────────┘     └─────────────────┘     └────────┘
```

---

## 1️⃣ ขั้นตอน Developer

**เงื่อนไขที่ต้องผ่านก่อนขอ merge เข้า branch `QA/Tester`:**

- [ ] เขียนโค้ดตาม requirement / task ที่ได้รับมอบหมายครบถ้วน
- [ ] เขียน Unit Test ครอบคลุม logic หลักของโมดูลที่พัฒนา (อย่างน้อยครอบคลุม happy path + edge case ที่ระบุใน Risk Register ที่เกี่ยวข้อง)
- [ ] รัน Unit Test ผ่านทั้งหมดในเครื่องตนเองก่อน push
- [ ] โค้ด build/run ได้ไม่มี error บน environment มาตรฐานของทีม
- [ ] Commit message และคำอธิบาย PR ระบุ Risk # หรือ Feature ที่แก้ไข/พัฒนาให้ชัดเจน
- [ ] เปิด Pull Request จาก branch ของตนเอง → branch `QA/Tester`

**Output ของขั้นตอนนี้:** PR ที่มีโค้ด + Unit Test พร้อม merge เข้า `QA/Tester`

---

## 2️⃣ ขั้นตอน QA/Tester

**เมื่อโค้ดถูก merge เข้า branch `QA/Tester` แล้ว:**

- [ ] ตรวจสอบ Risk Register (`risk_register_app_v1.md` หรือฉบับที่เกี่ยวข้อง) ว่ามีความเสี่ยงข้อใดบ้างที่งานนี้ต้องแก้ไข
- [ ] เขียนไฟล์ Script Test Case (เช่น `test_app.py`) ที่ครอบคลุม **ทุกข้อ** ใน Risk Register ที่เกี่ยวข้องกับงานนี้ — ห้ามมีข้อใดตกหล่น
- [ ] รัน Test Script จริงกับโค้ดใน branch `QA/Tester` (ไม่ใช่แค่ตรวจโค้ดแบบ static)
- [ ] ถ้าพบ Test ไม่ผ่าน (FAIL) → ส่งกลับ Developer พร้อมระบุ Risk # / test case ที่ล้มเหลว และ**ห้าม merge** จนกว่าจะแก้ไขและทดสอบผ่านใหม่
- [ ] เมื่อ Test ผ่านครบทุกเคสแล้ว จัดทำไฟล์ `readme_tester.md` สรุป:
  - วิธีการทดสอบ / วิธีรัน
  - ขอบเขตการทดสอบแยกตาม Risk
  - ผลลัพธ์การทดสอบจริง (จำนวน test, pass/fail, %)
- [ ] เปิด Pull Request จาก `QA/Tester` → `main` แนบ `test_app.py` และ `readme_tester.md`

**Output ของขั้นตอนนี้:** PR เข้า `main` พร้อมหลักฐานการทดสอบครบทุก Risk ที่เกี่ยวข้อง และผลลัพธ์เป็น PASS ทั้งหมด

---

## 3️⃣ ขั้นตอน Tech Lead

**ก่อนอนุมัติ PR เข้า `main`:**

- [ ] ตรวจสอบว่าขอบเขตการทดสอบใน `test_app.py` / `readme_tester.md` **ตรงกับหัวข้องานที่แจกจ่ายให้ (Risk Register)** ครบทุกข้อ ไม่มีข้อตกหล่นหรือทดสอบผิดจุด
- [ ] ตรวจสอบว่าผลการทดสอบเป็น PASS จริงตามที่ QA/Tester รายงาน (สุ่มตรวจ/รันซ้ำได้หากจำเป็น)
- [ ] ตรวจสอบว่า `readme_tester.md` มีเนื้อหาครบถ้วน อ่านเข้าใจได้ ตรวจสอบย้อนหลังได้
- [ ] หากพบว่าการทดสอบไม่ตรงกับ Risk Register หรือมีข้อบกพร่อง → **ปฏิเสธ (Request Changes)** และส่งกลับให้ QA/Tester หรือ Developer แก้ไข พร้อมระบุเหตุผล
- [ ] หากผ่านทุกเงื่อนไข → **Approve** PR

**Output ของขั้นตอนนี้:** การ Approve จาก Tech Lead อย่างน้อย 1 ท่าน

---

## 4️⃣ กฎการ Merge เข้า `main`

- 🔒 **ต้องมี Approve อย่างน้อย 1 คนจาก Tech Lead** จึงจะ merge เข้า `main` ได้ (บังคับใช้ผ่าน Branch Protection Rule)
- ❌ ห้าม merge เข้า `main` โดยตรงจาก branch ของ Developer — ต้องผ่าน branch `QA/Tester` ก่อนเสมอ
- ❌ ห้าม merge หาก Test Case ยังมีสถานะ FAIL แม้แต่ 1 เคส
- ❌ ห้าม merge หากไม่มีไฟล์ `readme_tester.md` แนบมากับ PR
- ✅ Merge เข้า `main` ได้ก็ต่อเมื่อ: Developer ส่งงานครบ → QA/Tester ทดสอบผ่านครบทุก Risk → Tech Lead ตรวจสอบและ Approve แล้วเท่านั้น

---

## ✅ สรุปเกณฑ์ "Done" ของงานนี้ (ภาพรวม)

งานหนึ่งชิ้นจะถือว่า **Done** ก็ต่อเมื่อครบทุกข้อต่อไปนี้:

1. โค้ดผ่าน Unit Test ของ Developer แล้ว merge เข้า `QA/Tester` สำเร็จ
2. QA/Tester ทดสอบครบทุก Risk ที่เกี่ยวข้อง ผลลัพธ์ PASS ทั้งหมด และมี `readme_tester.md` สรุปผลแนบไว้
3. Tech Lead ตรวจสอบขอบเขตการทดสอบตรงกับ Risk Register และ Approve แล้ว
4. PR มี Approve อย่างน้อย 1 คน ก่อน merge เข้า `main`
5. โค้ดถูก merge เข้า `main` เรียบร้อย