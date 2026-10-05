# รายงานชุดไฟล์กระจายซอฟต์แวร์ (Package Distribution Artifact Report)
**มาตรฐานอ้างอิง:** ISO/IEC/IEEE 12207 (กระบวนการส่งมอบระบบ และการจัดการโครงแบบ), ISO/IEC 14764:2006 (การบำรุงรักษาประเภทปรับให้เข้ากับสภาพแวดล้อม — Adaptive)
**รายวิชา:** ENGSE225 Software Evolution & Maintenance

## วัตถุประสงค์ของเอกสาร

เอกสารฉบับนี้บันทึกการจัดทำชุดไฟล์สำหรับกระจายซอฟต์แวร์ Inventory Management System เวอร์ชัน 2.0.1 จำนวน 3 รูปแบบ ได้แก่ ไฟล์ซอร์สสำหรับติดตั้ง (Source Distribution: sdist) ไฟล์ติดตั้งสำเร็จรูป (Wheel: .whl) และไฟล์กำหนดการสร้างคอนเทนเนอร์ (Dockerfile) พร้อมผลการทดสอบว่าแต่ละรูปแบบติดตั้งและทำงานได้จริง

## สรุปผล

| รูปแบบ | สถานะ | หลักฐาน |
| :--- | :---: | :--- |
| Source Distribution (`.tar.gz`) | ✅ สร้างและทดสอบแล้ว | ติดตั้งใน venv ใหม่และรันครบทุกเมนู, รันชุดทดสอบจากซอร์สที่แตกออกมาผ่าน 158 รายการ |
| Wheel (`.whl`) | ✅ สร้างและทดสอบแล้ว | ติดตั้งใน venv ใหม่ รันครบทุกเมนูและ `--selftest` และถอนการติดตั้งได้สมบูรณ์ |
| Dockerfile / Docker image | ✅ สร้างและทดสอบแล้ว | สร้าง image บน Docker 29.3.0 (WSL2 Ubuntu 24.04) ผ่านการตรวจ 11/11 ข้อ รวมถึงสแกน Trivy ไม่พบช่องโหว่ของแพ็กเกจ Python และไม่มีช่องโหว่ระดับระบบปฏิบัติการที่มีแพตช์แล้วค้างอยู่ |

> ข้อความ "พร้อมติดตั้งและประมวลผลบนทุกสภาพแวดล้อม" ยืนยันได้ในสภาพแวดล้อมต่อไปนี้: Windows 11 กับ Python 3.13 (wheel และ sdist) และ Linux (Debian 13) กับ Python 3.12 (Docker image) ส่วน Python 3.10–3.11 บน Linux ยืนยันผ่าน CI ของซอร์สโค้ดเท่านั้น ยังไม่ได้ติดตั้งจาก wheel โดยตรง (ดูส่วนที่ 6)

หลักฐานดิบ:
- [`reports/package_artifact_verification_2026-10-05_rebuild.txt`](../reports/package_artifact_verification_2026-10-05_rebuild.txt): wheel และ sdist ที่ build ใหม่หลังปรับโครงสร้างลด Cyclomatic Complexity (ชุดที่ใช้ส่งมอบ)
- [`reports/docker_image_verification_2026-10-05.txt`](../reports/docker_image_verification_2026-10-05.txt): ผลตรวจ Docker image และผลสแกน Trivy
- [`reports/package_artifact_verification_2026-10-05.txt`](../reports/package_artifact_verification_2026-10-05.txt): ผลทดสอบชุดแรกก่อนปรับโครงสร้าง (เก็บไว้อ้างอิง ชุดไฟล์นี้ถูกแทนที่แล้ว)

---

## ส่วนที่ 1: ข้อมูลชุดไฟล์

| ไฟล์ | ขนาด (ไบต์) | SHA-256 |
| :--- | ---: | :--- |
| `engse225_inventory_system-2.0.1.tar.gz` | 71,170 | `031b2a1c10b6d2ebb9b0328eb9059aeecaa164e45279ec8823fdb4fd825dbc6a` |
| `engse225_inventory_system-2.0.1-py3-none-any.whl` | 31,304 | `b8764a568d8f0baf9525e00e45f796ef90ec6e837c9970ea1c5dbafefe931752` |

ค่าข้างต้นเป็นชุดที่ build ใหม่หลังปรับโครงสร้างลด Cyclomatic Complexity ชุดแรก (sdist 68,084 ไบต์ `e70eb0ec…`, wheel 30,343 ไบต์ `770e17bd…`) ถูกแทนที่แล้ว ห้ามนำไปแนบ Release ค่า SHA-256 จะเปลี่ยนทุกครั้งที่ build ใหม่ เพราะไฟล์ที่บรรจุมีเวลาสร้างกำกับ จึงต้องคำนวณใหม่จากไฟล์ที่จะแนบจริงทุกครั้ง

- **ชื่อแพ็กเกจ:** `engse225-inventory-system` เวอร์ชัน `2.0.1` ต้องการ Python 3.10 ขึ้นไป และ **ไม่มี dependency ภายนอก** (ใช้เฉพาะไลบรารีมาตรฐาน)
- **Wheel แบบ `py3-none-any`:** ใช้ได้กับทุกระบบปฏิบัติการ เพราะเป็นโค้ด Python ล้วน
- **การจัดเก็บ:** ชุดไฟล์ไม่ถูกบันทึกเข้าคลังโค้ด (`dist/` อยู่ใน `.gitignore`) ให้แนบกับ GitHub Release `v2.0.1` ตามแผนใน [`Release_Management_and_Board_Cleanup_Plan.md`](./Release_Management_and_Board_Cleanup_Plan.md) และตรวจค่า SHA-256 ข้างต้นก่อนแนบ

---

## ส่วนที่ 2: การตั้งค่าการสร้างแพ็กเกจ

การตั้งค่าอยู่ใน [`pyproject.toml`](../pyproject.toml) ส่วน `[build-system]` และ `[project]` ใช้เครื่องมือสร้างแพ็กเกจ (build backend) **hatchling** ด้วยเหตุผลต่อไปนี้

| ข้อจำกัดของโครงการ | วิธีจัดการ |
| :--- | :--- |
| โมดูลทั้งหมดอยู่ที่โฟลเดอร์หลัก ไม่ได้อยู่ใน package (flat layout) และเรียกกันด้วยชื่อโดยตรง | ระบุรายชื่อไฟล์ใน `[tool.hatch.build.targets.wheel] only-include` ไฟล์จะถูกติดตั้งที่ระดับบนสุดของ `site-packages` |
| `DatabaseConnection` หา `schema.sql` จากโฟลเดอร์เดียวกับ `database_connection.py` และ **ข้ามการสร้างตารางโดยไม่แจ้งเตือนหากไม่พบไฟล์** | บรรจุ `schema.sql` ไว้ใน wheel ข้างโมดูล และตรวจยืนยันหลังติดตั้งว่าไฟล์อยู่ในตำแหน่งที่ถูกต้อง |
| ไม่ต้องการแก้ไขโค้ดโปรแกรมเพื่อการสร้างแพ็กเกจ | การสร้างแพ็กเกจเปลี่ยนเฉพาะไฟล์ตั้งค่า (การแก้โค้ดที่เกิดขึ้นภายหลังเป็นการปรับโครงสร้างลดความซับซ้อนตาม [`Technical_Metrics_Handover.md`](./Technical_Metrics_Handover.md) ส่วนที่ 2.2 ไม่เกี่ยวกับการสร้างแพ็กเกจ) |

### 2.1 เนื้อหาของแต่ละรูปแบบ

| รูปแบบ | ไฟล์ที่บรรจุ | ไฟล์ที่ไม่บรรจุ |
| :--- | :--- | :--- |
| Wheel | โมดูลที่ใช้รันจริง 8 ไฟล์ (`inventory_app.py`, `validator.py`, `product.py`, `product_repository.py`, `database_connection.py`, `logger.py`, `csv_report_exporter.py`, `atomic_file_writer.py`) และ `schema.sql` | `app_v1.py` (ต้นแบบเดิม), ไฟล์ทดสอบ, เอกสาร |
| sdist | โค้ดและไฟล์ทดสอบทั้งหมด, `schema.sql`, `seed_data.sql`, `README.md`, `CHANGELOG.md`, `requirements*.txt`, `.flake8`, `pyproject.toml`, `scripts/` | `documents/`, `reports/` |

---

## ส่วนที่ 3: วิธีสร้างและติดตั้ง

```bash
# สร้าง sdist และ wheel (ผลลัพธ์อยู่ใน dist/)
pip install build
python -m build

# ติดตั้งจาก wheel แล้วเปิดโปรแกรม (ฐานข้อมูลถูกสร้างในโฟลเดอร์ที่สั่งรัน)
pip install engse225_inventory_system-2.0.1-py3-none-any.whl
python -m inventory_app

# ถอนการติดตั้ง
pip uninstall engse225-inventory-system
```

```bash
# Docker
docker build -t engse225-inventory-system:2.0.1 .
docker run -it --rm -v inventory-data:/data engse225-inventory-system:2.0.1

# ตรวจ image หลัง build (เมนู 1-8, volume, --selftest, ความปลอดภัย และสแกน Trivy)
sh scripts/verify_docker.sh
```

---

## ส่วนที่ 4: ผลการทดสอบชุดไฟล์ (5 ตุลาคม 2026)

ทุกกรณีใช้สภาพแวดล้อมเสมือน (venv) ที่สร้างใหม่ และรันโปรแกรมจากโฟลเดอร์ว่างที่ไม่มีซอร์สโค้ด เพื่อยืนยันว่าโปรแกรมไม่ได้อ่านไฟล์จากคลังโค้ด

| ลำดับ | กรณีทดสอบ | ผลลัพธ์ | ผล |
| :---: | :--- | :--- | :---: |
| 1 | ติดตั้ง wheel | `Successfully installed engse225-inventory-system-2.0.1` และพบ `schema.sql` ใน `site-packages` | ✅ |
| 2 | `python -m inventory_app` ใช้งานเมนู 1–8 ต่อเนื่อง | exit code 0 ไม่มีข้อผิดพลาด แสดงผลครบทุกเมนู และสร้าง `inventory.db` กับ `low_stock_report.csv` ในโฟลเดอร์ที่สั่งรัน | ✅ |
| 3 | `python -m inventory_app --selftest` (จาก wheel) | ผ่าน | ✅ |
| 4 | ถอนการติดตั้ง wheel | `Successfully uninstalled` | ✅ |
| 5 | ติดตั้งจาก sdist (สร้าง wheel จากซอร์สระหว่างติดตั้ง) แล้วรันกรณี 2–3 | ผ่านทั้งหมด | ✅ |
| 6 | แตก sdist แล้วติดตั้ง `requirements-dev.txt` และรัน `pytest --cov` | ผ่าน 158 รายการ ความครอบคลุมร้อยละ 98.38 | ✅ |
| 7 | `docker build` ตาม Dockerfile | สร้าง image สำเร็จ (ดูส่วนที่ 5.1) | ✅ |
| 8 | การทดสอบถดถอยในคลังโค้ด | ผ่าน 158 รายการ ความครอบคลุมร้อยละ 98.38 Flake8 และ Bandit เป็นศูนย์ | ✅ |

ตารางนี้เป็นผลของชุดไฟล์ที่ build ใหม่หลังปรับโครงสร้าง (ทดสอบซ้ำครบทุกกรณี ผ่าน 9/9 ข้อ) ชุดแรกก่อนปรับโครงสร้างผ่านทุกกรณีเช่นกัน ยกเว้นกรณีที่ 7 ซึ่งตอนนั้นทดสอบได้เพียงขั้นสร้าง wheel

---

## ส่วนที่ 5: Dockerfile

ไฟล์ [`Dockerfile`](../Dockerfile) และ [`.dockerignore`](../.dockerignore) ออกแบบดังนี้

| หัวข้อ | การออกแบบ |
| :--- | :--- |
| Image ตั้งต้น | `python:3.12-slim` (อยู่ในชุดเวอร์ชันที่ CI ทดสอบ) |
| การสร้าง | ขั้นแรกสร้าง wheel จากซอร์ส ขั้นที่สองติดตั้งเฉพาะ wheel ทำให้ image ไม่มีซอร์สโค้ดและไฟล์ทดสอบ |
| ความปลอดภัย | รันด้วยผู้ใช้ `app` (UID 1000) ที่ไม่ใช่ root, ติดตั้ง security update ของ Debian ตอน build (`apt-get upgrade`) และ **ถอน pip ออกจาก image** หลังติดตั้ง wheel เพราะโปรแกรมไม่ใช้ pip ตอนรัน (ดูส่วนที่ 5.2) |
| การเก็บข้อมูล | โปรแกรมทำงานในโฟลเดอร์ `/data` ซึ่งประกาศเป็น volume ข้อมูลจึงไม่หายเมื่อลบคอนเทนเนอร์ |
| การรัน | โปรแกรมเป็นเมนูแบบโต้ตอบ ต้องใช้ `docker run -it` |

### 5.1 ผลการทดสอบ Docker image (5 ตุลาคม 2026)

สร้างและทดสอบบน Docker Engine 29.3.0 ใน WSL2 (Ubuntu 24.04) ด้วยสคริปต์ [`scripts/verify_docker.sh`](../scripts/verify_docker.sh) ขนาด image 46.7 MB (`sha256:f1c281ec9b77…`)

| ลำดับ | กรณีทดสอบ | ผลลัพธ์ | ผล |
| :---: | :--- | :--- | :---: |
| D1 | ใช้งานเมนู 1–8 ต่อเนื่องใน `docker run -i` | exit code 0 ไม่มี Traceback แสดงผลครบทุกเมนู | ✅ |
| D2 | ลบคอนเทนเนอร์แล้วเปิดคอนเทนเนอร์ใหม่ด้วย volume เดิม | อ่านสินค้าที่บันทึกไว้ได้ จำนวนคงเหลือถูกต้องหลังตัดสต็อก | ✅ |
| D3 | ไฟล์ `inventory.db` และ CSV อยู่ใน `/data` | พบทั้งสองไฟล์ใน volume | ✅ |
| D4 | CSV มี UTF-8 BOM (BUG-106) | 3 ไบต์แรกเป็น `EF BB BF` | ✅ |
| D5 | `python -m inventory_app --selftest` | ผ่าน | ✅ |
| D6 | ผู้ใช้ที่รันโปรแกรม | UID 1000 (ไม่ใช่ root) | ✅ |
| D7 | ไม่มีไฟล์ทดสอบ, `app_v1.py`, `/src` หรือไฟล์ wheel ค้างใน image | ไม่พบ | ✅ |
| D8 | `schema.sql` อยู่ข้าง `database_connection.py` | พบ | ✅ |
| D9 | ไม่มี pip ใน image | `importlib.util.find_spec("pip")` เป็น `None` | ✅ |
| D10 | Trivy: ช่องโหว่ของแพ็กเกจ Python | 0 รายการ | ✅ |
| D11 | Trivy: ช่องโหว่ระบบปฏิบัติการที่มีแพตช์แล้ว (`--ignore-unfixed`) | 0 รายการ | ✅ |

**ข้อสังเกตจากการทดสอบ**
- บนเครื่องที่ทดสอบ คอนเทนเนอร์บน network ปกติ (bridge) ค้นหา DNS ไม่ได้ จึงต้องสั่ง `docker build --network=host` ปัญหานี้เกิดจากการตั้งค่า DNS ของ WSL บนเครื่องนี้ ไม่ใช่จาก Dockerfile เครื่องที่ตั้งค่า Docker ปกติใช้คำสั่งในส่วนที่ 3 ได้ทันที
- ไฟล์ CSV ที่ส่งออกมีสิทธิ์ `-rw-------` (อ่านได้เฉพาะเจ้าของ) เพราะ `AtomicFileWriter` สร้างไฟล์ชั่วคราวด้วย `tempfile.mkstemp()` ซึ่งกำหนดสิทธิ์ 0600 แล้ว `os.replace()` คงสิทธิ์นั้นไว้ บน Linux ผู้ใช้อื่นที่ไม่ใช่ UID 1000 จึงเปิดไฟล์จาก volume ไม่ได้ ส่วน `inventory.db` เป็น `-rw-r--r--` ตามปกติ บน Windows ไม่มีผล ดูส่วนที่ 6

### 5.2 การแก้ไขจากผลสแกน Trivy

การสแกน image รุ่นแรกด้วย Trivy 0.67.2 พบช่องโหว่ที่ pip-audit ตรวจไม่พบ จึงแก้ Dockerfile แล้วสร้างและทดสอบ image ใหม่ทั้งหมด

| ผลสแกนรุ่นแรก | สาเหตุ | การแก้ไข | ผลหลังแก้ |
| :--- | :--- | :--- | :--- |
| แพ็กเกจ Python 6 รายการ (HIGH 4, MEDIUM 2) ใน `urllib3` 2.7.0, `msgpack` 1.1.2 และ `setuptools` 70.3.0 | ไลบรารีเหล่านี้ pip ฝังมาเองใน `pip/_vendor/` (Trivy อ่านจาก `vendor.txt`) ไม่ได้ติดตั้งแยก pip-audit จึงไม่รายงาน | ถอน pip ออกจาก image หลังติดตั้ง wheel (`pip uninstall -y pip`) ซึ่งตัดความเสี่ยง CVE-2026-13346 ของ pip เองออกไปด้วย | 0 รายการ |
| แพ็กเกจระบบปฏิบัติการ (Debian 13.7) 167 รายการ: มีแพตช์แล้ว 1 รายการ (`libpcre2-8-0`, CVE-2026-103111 ระดับ HIGH), ผู้ดูแล Debian เลื่อนการแก้ 2 รายการ และยังไม่มีแพตช์ 164 รายการ | base image `python:3.12-slim` สร้างก่อนแพตช์ libpcre2 ออก | เพิ่ม `apt-get upgrade` ใน Dockerfile | ที่มีแพตช์แล้วเหลือ 0 รายการ ส่วนที่ยังไม่มีแพตช์เหลือ 166 รายการ (ดูส่วนที่ 6) |

---

## ส่วนที่ 6: ข้อจำกัดและงานที่ต้องดำเนินการต่อ

| ประเด็น | ผลกระทบ | แนวทาง |
| :--- | :--- | :--- |
| Docker image มีช่องโหว่ระดับระบบปฏิบัติการที่ Debian ยังไม่ออกแพตช์ 166 รายการ (ส่วนใหญ่อยู่ใน `util-linux` และไลบรารีที่เกี่ยวข้อง) | แก้เองไม่ได้จนกว่า Debian จะออกแพตช์ โปรแกรมไม่ได้เรียกใช้คำสั่งเหล่านี้ และคอนเทนเนอร์รันด้วยผู้ใช้ที่ไม่ใช่ root | สร้าง image ใหม่และรัน `scripts/verify_docker.sh` ทุกเดือน และทุกครั้งที่ base image ออกรุ่นใหม่ หรือเพิ่มงานนี้ใน GitHub Actions |
| ไฟล์ CSV ที่ส่งออกบน Linux มีสิทธิ์ 0600 | ผู้ใช้อื่นบนเครื่องเดียวกันหรือบน host ที่ UID ไม่ตรงเปิดไฟล์ไม่ได้ | เสนอเปิดเป็นข้อบกพร่องใหม่ ให้ `AtomicFileWriter` ตั้งสิทธิ์ไฟล์ตาม umask (หรือคงสิทธิ์ของไฟล์เดิม) ก่อน `os.replace()` ต้องผ่านกระบวนการ ISO/IEC 14764 ก่อนแก้ไข |
| ทดสอบ wheel และ sdist เฉพาะ Windows กับ Python 3.13 | Python 3.12 บน Linux ยืนยันผ่าน Docker image แล้ว แต่ Python 3.10–3.11 บน Linux ยังไม่ได้ติดตั้งจาก wheel โดยตรง | เพิ่มงานใน CI ที่ติดตั้ง wheel แล้วรัน `python -m inventory_app --selftest` ในทุกเวอร์ชันของ matrix |
| โมดูลถูกติดตั้งที่ระดับบนสุดของ `site-packages` ด้วยชื่อทั่วไป เช่น `logger`, `product`, `validator` | อาจชนกับแพ็กเกจอื่นที่ใช้ชื่อเดียวกันในสภาพแวดล้อมเดียวกัน | ติดตั้งใน venv แยกเสมอ และพิจารณาย้ายโค้ดเข้า package เดียว (เช่น `inventory_system/`) เป็นคำขอเปลี่ยนแปลงประเภท Adaptive ในเวอร์ชัน 3.0 |
| ไม่มีคำสั่งสำหรับเรียกโปรแกรมโดยตรง (console script) | ต้องเรียกด้วย `python -m inventory_app` | เพิ่มฟังก์ชัน `main()` และ `[project.scripts]` ในเวอร์ชัน 3.0 |

---

## ภาคผนวก: ประวัติการแก้ไขเอกสาร

| ฉบับที่ | วันที่ | รายละเอียด |
| :---: | :--- | :--- |
| 1.0 | 5 ตุลาคม 2026 | จัดทำชุดไฟล์กระจายซอฟต์แวร์เวอร์ชัน 2.0.1 และบันทึกผลการทดสอบ |
| 1.1 | 5 ตุลาคม 2026 | สร้างและทดสอบ Docker image (11/11), แก้ Dockerfile ตามผลสแกน Trivy (ถอน pip, ติดตั้ง security update) และ build sdist/wheel ใหม่หลังปรับโครงสร้างลดความซับซ้อน |
