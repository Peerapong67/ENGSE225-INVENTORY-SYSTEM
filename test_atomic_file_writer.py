"""
Unit Tests สำหรับ AtomicFileWriter
รันด้วย: pytest test_atomic_file_writer.py -v
รันแบบ Demo ใน Terminal: python test_atomic_file_writer.py
"""

import os
import tempfile

import pytest

from atomic_file_writer import AtomicFileWriter


def _leftover_tmp_files(directory):
    return [name for name in os.listdir(directory) if name.endswith(".tmp")]


def _write_text(text):
    return lambda f: f.write(text)


def _fail_midway(f):
    f.write("ข้อมูลครึ่งเดียว")
    raise RuntimeError("จำลองโปรแกรมพังระหว่างเขียน")


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

def test_write_creates_new_file(tmp_path):
    path = tmp_path / "new.txt"

    AtomicFileWriter.write(str(path), _write_text("สวัสดี"))

    assert path.read_text(encoding="utf-8") == "สวัสดี"
    assert _leftover_tmp_files(tmp_path) == []


def test_write_replaces_existing_file_completely(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("old content that is longer", encoding="utf-8")

    AtomicFileWriter.write(str(path), _write_text("new"))

    assert path.read_text(encoding="utf-8") == "new"


def test_failure_keeps_original_file_intact(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("ข้อมูลเดิม", encoding="utf-8")

    with pytest.raises(RuntimeError):
        AtomicFileWriter.write(str(path), _fail_midway)

    assert path.read_text(encoding="utf-8") == "ข้อมูลเดิม"
    assert _leftover_tmp_files(tmp_path) == []


def test_failure_on_new_path_creates_no_file(tmp_path):
    path = tmp_path / "never.txt"

    with pytest.raises(RuntimeError):
        AtomicFileWriter.write(str(path), _fail_midway)

    assert not path.exists()
    assert _leftover_tmp_files(tmp_path) == []


def test_relative_path_writes_into_cwd(isolated_cwd):
    AtomicFileWriter.write("relative.txt", _write_text("ok"))

    assert (isolated_cwd / "relative.txt").read_text(encoding="utf-8") == "ok"


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_atomic_file_writer.py
# ============================================================

def _demo_new_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "new.txt")
        AtomicFileWriter.write(path, _write_text("สวัสดี"))
        with open(path, encoding="utf-8") as f:
            return f.read(), _leftover_tmp_files(tmp_dir)


def _demo_failure_keeps_original():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "data.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("ข้อมูลเดิม")
        try:
            AtomicFileWriter.write(path, _fail_midway)
        except RuntimeError:
            pass
        with open(path, encoding="utf-8") as f:
            return f.read(), _leftover_tmp_files(tmp_dir)


def _demo_failure_on_new_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = os.path.join(tmp_dir, "never.txt")
        try:
            AtomicFileWriter.write(path, _fail_midway)
        except RuntimeError:
            pass
        return os.path.exists(path), _leftover_tmp_files(tmp_dir)


def _run_terminal_demo():
    print("=" * 85)
    print(" 🛡️  ATOMICFILEWRITER DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    cases = [
        {
            "id": "TC-ATOMIC-01",
            "method": "Successful Atomic Write (UTF-8)",
            "data": "เขียนข้อความ 'สวัสดี' ลงไฟล์ใหม่",
            "action": _demo_new_file,
            "verify": lambda res: res == ("สวัสดี", []),
            "expected": "ไฟล์ถูกสร้างพร้อมเนื้อหาครบ ภาษาไทยถูกต้อง ไม่มีไฟล์ .tmp ค้าง"
        },
        {
            "id": "TC-ATOMIC-02",
            "method": "Crash During Write Fault Tolerance",
            "data": "ไฟล์เดิม='ข้อมูลเดิม' แล้วจำลอง exception กลางการเขียน",
            "action": _demo_failure_keeps_original,
            "verify": lambda res: res == ("ข้อมูลเดิม", []),
            "expected": "ไฟล์เดิมยังอยู่ครบไม่ถูกเขียนทับครึ่งๆ กลางๆ และลบไฟล์ .tmp ทิ้ง"
        },
        {
            "id": "TC-ATOMIC-03",
            "method": "Crash On New File (No Partial File)",
            "data": "เขียนไฟล์ใหม่แล้วจำลอง exception กลางการเขียน",
            "action": _demo_failure_on_new_path,
            "verify": lambda res: res == (False, []),
            "expected": "ไม่มีไฟล์ปลายทางที่ข้อมูลไม่ครบเกิดขึ้น และไม่มีไฟล์ .tmp ค้าง"
        },
    ]

    passed_count = 0
    for idx, c in enumerate(cases, 1):
        try:
            res = c["action"]()
            is_ok = c["verify"](res)
        except Exception as e:
            res = f"Exception: {e}"
            is_ok = False

        status_tag = "[ PASSED ] ✓" if is_ok else "[ FAILED ] ✗"
        if is_ok:
            passed_count += 1

        print(f"\n{idx}. Case ID: {c['id']}  {status_tag}")
        print(f"   • วิธีการทดสอบ  : {c['method']}")
        print(f"   • ชุดข้อมูลทดสอบ: {c['data']}")
        print(f"   • ผลลัพธ์ที่ได้  : {c['expected']}")

    print("\n" + "-" * 85)
    print(f"สรุปภาพรวม: ผ่านการทดสอบ {passed_count}/{len(cases)} เคส (Pass Rate: {(passed_count/len(cases))*100:.1f}%)")
    print("=" * 85)


if __name__ == "__main__":
    _run_terminal_demo()
