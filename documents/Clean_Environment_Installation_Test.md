# CLEAN ENVIRONMENT INSTALLATION TEST — Automated Setup Scripts
**Academic Reference:** ISO/IEC 12207 (Transition Process — ติดตั้งระบบในสภาพแวดล้อมเป้าหมาย และ Verification Process — ยืนยันว่าติดตั้งแล้วทำงานถูกต้อง)
**Course Context:** ENGSE225 Software Evolution & Maintenance — ตรวจว่าคนที่เพิ่ง clone repo บนเครื่องใหม่ ติดตั้งและใช้งาน Version 2.0.1 ได้โดยไม่ต้องพึ่งของที่ค้างอยู่ในเครื่องผู้พัฒนา

---

## ส่วนที่ 1: ชุดสคริปต์ติดตั้งอัตโนมัติ (Automated Setup Scripts)

| ไฟล์ | ใช้กับ | วิธีรัน |
| :--- | :--- | :--- |
| [`scripts/setup.cmd`](../scripts/setup.cmd) | Windows (Command Prompt / PowerShell / ดับเบิลคลิก) | `scripts\setup.cmd -Clean -Seed` |
| [`scripts/setup.ps1`](../scripts/setup.ps1) | Windows PowerShell 5.1 ขึ้นไป | `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Clean -Seed` |
| [`scripts/setup.sh`](../scripts/setup.sh) | Linux, macOS, Git Bash บน Windows | `bash scripts/setup.sh --clean --seed` |

`setup.cmd` เป็นเพียงตัวเรียก `setup.ps1` ด้วย `-ExecutionPolicy Bypass` เฉพาะการรันครั้งนั้น (ไม่เปลี่ยนค่า Execution Policy ของเครื่อง) ทั้งสามไฟล์รันจากโฟลเดอร์ไหนก็ได้ สคริปต์จะย้ายไปทำงานที่ root ของโปรเจกต์ให้เอง

### 1.1 ตัวเลือก

| PowerShell | bash | ผล |
| :--- | :--- | :--- |
| `-Clean` | `--clean` | ลบ `.venv` และ `inventory.db` เดิมก่อนติดตั้ง เพื่อจำลองเครื่องใหม่ (**ข้อมูลในฐานข้อมูลหายถาวร**) |
| `-Seed` | `--seed` | ใส่สินค้าตัวอย่าง 3 รายการจาก `seed_data.sql` |
| `-SkipTests` | `--skip-tests` | ไม่ติดตั้งเครื่องมือทดสอบ และไม่รัน pytest / Flake8 / Bandit (ยังรัน smoke test และ self-test) |

### 1.2 ขั้นตอนที่สคริปต์ทำ

| ขั้น | รายละเอียด | ถ้าล้มเหลว |
| :---: | :--- | :--- |
| 1 | ตรวจหา Python ≥ 3.10 (Windows: `py -3`, `python`, `python3` / bash: `python3`, `python`) | หยุดทันที |
| 2 | (`-Clean`) ลบ `.venv` และ `inventory.db` | หยุดทันที |
| 3 | สร้าง virtual environment `.venv` (มีอยู่แล้วจะใช้ของเดิม) | หยุดทันที |
| 4 | `pip install -r requirements-dev.txt` ลงใน `.venv` (ข้ามเมื่อ `-SkipTests`) | หยุดทันที |
| 5 | สร้าง `inventory.db` จาก `schema.sql` (อ่านด้วย UTF-8) | หยุดทันที |
| 6 | (`-Seed`) ใส่ข้อมูลจาก `seed_data.sql` | หยุดทันที |
| 7 | ตรวจว่ามีตาราง `products`, `stock_movements`, `action_logs`, ดัชนีกันบาร์โค้ดซ้ำ และ trigger `updated_at` ครบ และจำนวนสินค้าถูกต้อง | บันทึก FAIL แล้วทำขั้นถัดไป |
| 8 | Smoke test: เปิด `inventory_app.py` ป้อนเมนู `8` ต้องออกได้และ exit code 0 | บันทึก FAIL แล้วทำขั้นถัดไป |
| 9 | `python inventory_app.py --selftest` | บันทึก FAIL แล้วทำขั้นถัดไป |
| 10–12 | `pytest --cov` (เกณฑ์ ≥ 90%), Flake8, Bandit (ข้ามเมื่อ `-SkipTests`) | บันทึก FAIL แล้วทำขั้นถัดไป |

จบด้วยตารางสรุป PASS/FAIL ทุกขั้น และคืน **exit code 0 เมื่อผ่านทุกขั้น หรือ 1 เมื่อมีขั้นใดล้มเหลว** จึงใช้ใน CI หรือสคริปต์อื่นได้

### 1.3 ข้อกำหนดทางเทคนิคของไฟล์สคริปต์

| ข้อกำหนด | เหตุผล |
| :--- | :--- |
| [`.gitattributes`](../.gitattributes) บังคับ `*.sh` เป็น LF และ `*.ps1`, `*.cmd` เป็น CRLF | repo ตั้ง `core.autocrlf=true` ถ้าไม่บังคับ `setup.sh` จะถูก checkout เป็น CRLF แล้ว bash รันไม่ได้ (`$'\r': command not found`) |
| `setup.ps1` บันทึกเป็น UTF-8 **มี BOM** | Windows PowerShell 5.1 อ่านไฟล์ที่ไม่มี BOM ด้วย code page ของเครื่อง ข้อความภาษาไทยในสคริปต์จะเพี้ยน |
| `setup.cmd` เป็น ASCII ล้วน | cmd.exe อ่านไฟล์ `.cmd` ด้วย OEM code page (เหตุผลเดียวกับที่ `requirements*.txt` ต้องเป็น ASCII) |
| `setup.ps1` รันโค้ด Python ผ่านไฟล์ชั่วคราว ไม่ pipe เข้า stdin | PowerShell 5.1 แปลงข้อความที่ pipe เข้า native process เป็น ASCII ทำให้ภาษาไทยเป็น `?` และ input ไม่ถึงโปรแกรม (พบในการทดสอบรอบแรก ดูส่วนที่ 3) |
| สคริปต์เป็น `.ps1`/`.sh` ไม่ใช่ `.py` | `pyproject.toml` วัด coverage จาก `source = ["."]` ไฟล์ `.py` ใหม่ที่ไม่มีเทสต์จะทำให้ coverage ลดลง |

---

## ส่วนที่ 2: ขั้นตอนทดสอบ Clean Environment Installation

1. Clone repo ลงโฟลเดอร์ว่างที่ไม่มี `.venv` และ `inventory.db`
   ```bash
   git clone https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM.git inventory-clean-test
   cd inventory-clean-test
   ```
2. รันสคริปต์ติดตั้งตามระบบปฏิบัติการ พร้อม `-Clean -Seed` (หรือ `--clean --seed`)
3. ตรวจว่าตารางสรุปเป็น PASS ทุกขั้น และ exit code เป็น 0
4. ทดสอบกรณีล้มเหลว: เปลี่ยนชื่อ `schema.sql` ชั่วคราวแล้วรันด้วย `-SkipTests` ต้องได้ FAIL ที่ขั้น "Create database" และ exit code 1 จากนั้นเปลี่ยนชื่อกลับ
5. รันซ้ำโดยไม่ใส่ `-Clean` ต้องใช้ `.venv` เดิมได้และผ่านทุกขั้น (ทดสอบการรันซ้ำ)
6. ลบโฟลเดอร์ทดสอบทิ้งเมื่อเสร็จ

---

## ส่วนที่ 3: ผลการทดสอบ (2026-10-04)

**สภาพแวดล้อม:** Windows 11, Python 3.13.14 (`py` launcher), Windows PowerShell 5.1, Git Bash · clone สดจาก `main` @ `24a9c75` แล้วเพิ่มไฟล์สคริปต์ชุดนี้

| # | กรณีทดสอบ | คำสั่ง | ผล | Exit code |
| :---: | :--- | :--- | :--- | :---: |
| 1 | ติดตั้งสะอาดบน Windows (รอบแรก) | `scripts\setup.cmd -Clean -Seed` | ❌ 11/12 ขั้นผ่าน Smoke test ได้ `EOFError` และข้อความไทยของขั้นตรวจฐานข้อมูลเป็น `?????` สาเหตุคือการ pipe เข้า native process ของ PowerShell 5.1 จึงแก้ให้รันโค้ด Python ผ่านไฟล์ชั่วคราว | 1 |
| 2 | ติดตั้งสะอาดบน Windows (หลังแก้) | `scripts\setup.cmd -Clean -Seed` | ✅ 12/12 ขั้นผ่าน: 158 passed, Coverage 98.12%, Flake8 0, Bandit 0 | 0 |
| 3 | รันซ้ำบน Windows (ใช้ `.venv` เดิม) | `scripts\setup.cmd -SkipTests` | ✅ ใช้ `.venv` เดิม ผ่านทุกขั้น ข้อความไทยแสดงถูกต้อง | 0 |
| 4 | ติดตั้งสะอาดด้วย Git Bash | `bash scripts/setup.sh --clean --seed` | ✅ 12/12 ขั้นผ่าน: 158 passed, Coverage 98.12% | 0 |
| 5 | กรณีล้มเหลว (ไม่มี `schema.sql`) — Windows | `scripts\setup.cmd -SkipTests` | ✅ หยุดที่ "Create database" แสดง FAIL | 1 |
| 6 | กรณีล้มเหลว (ไม่มี `schema.sql`) — Git Bash | `bash scripts/setup.sh --skip-tests` | ✅ หยุดที่ "Create database" แสดง FAIL | 1 |
| 7 | Line ending หลัง checkout (`core.autocrlf=true`) | `git ls-files --eol` แล้ว checkout ใหม่ | ✅ `setup.sh` เป็น LF, `setup.ps1` เป็น CRLF และยังมี BOM | — |
| 8 | ไม่มีไฟล์ชั่วคราวค้าง | ตรวจ `%TEMP%\inventory_setup_*.py` | ✅ 0 ไฟล์ | — |

**ยังไม่ได้ทดสอบ:** Linux และ macOS จริง (Git Bash ใช้ `.venv/Scripts/` แบบ Windows ส่วน Linux/macOS ใช้ `.venv/bin/` ซึ่งสคริปต์รองรับทั้งสองแบบ) ควรทดสอบบนเครื่องจริงหรือเพิ่ม job ใน GitHub Actions ที่รัน `bash scripts/setup.sh --clean --seed` บน `ubuntu-latest`

---

## ภาคผนวก: ประวัติเอกสาร (Document History)

| ฉบับ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 2026-10-04 | สร้างชุดสคริปต์ติดตั้งอัตโนมัติ และบันทึกผลทดสอบ Clean Environment Installation บน Windows และ Git Bash |
