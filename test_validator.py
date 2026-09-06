"""Unit test สำหรับ Validator (SCRUM-9)
รันด้วย pytest: python -m pytest -v test_validator.py
รันแบบ Demo ใน Terminal: python test_validator.py
"""
import io
import sys
import pytest
from validator import Validator


def _mock_inputs(monkeypatch, values):
    """ให้ input() คืนค่าตามลำดับใน values ทีละครั้งที่ถูกเรียก"""
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

# ------------------------------------------------------------
# inputNonNegativeInt
# ------------------------------------------------------------

def test_input_non_negative_int_accepts_valid_value(monkeypatch):
    _mock_inputs(monkeypatch, ["10"])
    assert Validator.inputNonNegativeInt("qty: ") == 10


def test_input_non_negative_int_rejects_negative_then_accepts(monkeypatch):
    _mock_inputs(monkeypatch, ["-5", "3"])
    assert Validator.inputNonNegativeInt("qty: ") == 3


def test_input_non_negative_int_rejects_non_numeric_then_accepts(monkeypatch):
    _mock_inputs(monkeypatch, ["abc", "7"])
    assert Validator.inputNonNegativeInt("qty: ") == 7


def test_input_non_negative_int_accepts_zero(monkeypatch):
    _mock_inputs(monkeypatch, ["0"])
    assert Validator.inputNonNegativeInt("qty: ") == 0


# ------------------------------------------------------------
# inputNonNegativeFloat
# ------------------------------------------------------------

def test_input_non_negative_float_accepts_valid_value(monkeypatch):
    _mock_inputs(monkeypatch, ["12.5"])
    assert Validator.inputNonNegativeFloat("price: ") == 12.5


def test_input_non_negative_float_rejects_negative_then_accepts(monkeypatch):
    _mock_inputs(monkeypatch, ["-1.5", "2.5"])
    assert Validator.inputNonNegativeFloat("price: ") == 2.5


def test_input_non_negative_float_rejects_non_numeric_then_accepts(monkeypatch):
    _mock_inputs(monkeypatch, ["xyz", "9.9"])
    assert Validator.inputNonNegativeFloat("price: ") == 9.9


def test_input_non_negative_float_accepts_integer_looking_input(monkeypatch):
    """ผู้ใช้กรอกเลขจำนวนเต็มในช่อง float ก็ต้องแปลงเป็น float ได้"""
    _mock_inputs(monkeypatch, ["10"])
    assert Validator.inputNonNegativeFloat("price: ") == 10.0


# ------------------------------------------------------------
# confirm
# ------------------------------------------------------------

def test_confirm_returns_true_on_yes(monkeypatch):
    _mock_inputs(monkeypatch, ["y"])
    result = Validator.confirm({"name": "Old"}, {"name": "New"})
    assert result is True


def test_confirm_returns_false_on_no(monkeypatch):
    _mock_inputs(monkeypatch, ["n"])
    result = Validator.confirm({"name": "Old"}, {"name": "New"})
    assert result is False


def test_confirm_is_case_insensitive(monkeypatch):
    _mock_inputs(monkeypatch, ["Y"])
    assert Validator.confirm({}, {}) is True


def test_confirm_rejects_anything_other_than_y(monkeypatch):
    _mock_inputs(monkeypatch, ["maybe", "n"])
    assert Validator.confirm({}, {}) is False


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_validator.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 🛡️   VALIDATOR CLASS DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    cases = [
        {
            "id": "TC-VAL-01",
            "method": "Valid Integer Equivalence Parsing",
            "stream": "10\n",
            "data": "กรอกค่า '10'",
            "action": lambda: Validator.inputNonNegativeInt("qty: "),
            "verify": lambda res: res == 10 and isinstance(res, int),
            "expected": "รับค่า '10' และแปลงเป็น int = 10 สำเร็จทันทีในรอบแรก"
        },
        {
            "id": "TC-VAL-02",
            "method": "Negative Integer Rejection Loop Guard",
            "stream": "-5\n3\n",
            "data": "กรอกค่าติดลบ '-5' แล้วตามด้วย '3'",
            "action": lambda: Validator.inputNonNegativeInt("qty: "),
            "verify": lambda res: res == 3,
            "expected": "ดักจับ '-5' ปฏิเสธค่าติดลบ วนลูปถามใหม่จนได้ค่าถูกต้อง int = 3"
        },
        {
            "id": "TC-VAL-03",
            "method": "Non-numeric String Exception Suppression",
            "stream": "abc\n7\n",
            "data": "กรอกตัวอักษร 'abc' แล้วตามด้วย '7'",
            "action": lambda: Validator.inputNonNegativeInt("qty: "),
            "verify": lambda res: res == 7,
            "expected": "ดักจับ ValueError ไม่ทำให้โปรแกรม Crash และวนถามจนได้ int = 7"
        },
        {
            "id": "TC-VAL-04",
            "method": "Zero Boundary Value Assertion",
            "stream": "0\n",
            "data": "กรอกค่า '0'",
            "action": lambda: Validator.inputNonNegativeInt("qty: "),
            "verify": lambda res: res == 0,
            "expected": "ยอมรับค่า 0 (ไม่ติดลบตามเกณฑ์ non-negative) เป็น int = 0 ถูกต้อง"
        },
        {
            "id": "TC-VAL-05",
            "method": "Float Boundary & Decimal Type Parsing",
            "stream": "-1.5\n2.5\n",
            "data": "กรอกทศนิยมติดลบ '-1.5' แล้วตามด้วย '2.5'",
            "action": lambda: Validator.inputNonNegativeFloat("price: "),
            "verify": lambda res: res == 2.5 and isinstance(res, float),
            "expected": "ปฏิเสธ -1.5 และแปลงค่า 2.5 เป็น float สำเร็จ"
        },
        {
            "id": "TC-VAL-06",
            "method": "Implicit Float Cast from Integer Representation",
            "stream": "10\n",
            "data": "กรอกเลข '10' ในฟังก์ชันรับ Float",
            "action": lambda: Validator.inputNonNegativeFloat("price: "),
            "verify": lambda res: res == 10.0 and isinstance(res, float),
            "expected": "แปลงจำนวนเต็มเป็นทศนิยม float = 10.0 รองรับการกรอกราคายืดหยุ่น"
        },
        {
            "id": "TC-VAL-07",
            "method": "Interactive State Confirmation (Positive Affirmation)",
            "stream": "y\n",
            "data": "old={'name': 'A'}, new={'name': 'B'}, input='y'",
            "action": lambda: Validator.confirm({"name": "A"}, {"name": "B"}),
            "verify": lambda res: res is True,
            "expected": "แสดง Diff ข้อมูลเดิม-ใหม่ และคืนค่า True เมื่อกดยืนยัน 'y'"
        },
        {
            "id": "TC-VAL-08",
            "method": "Interactive State Rejection (Negative Cancellation)",
            "stream": "n\n",
            "data": "old={'name': 'A'}, new={'name': 'B'}, input='n'",
            "action": lambda: Validator.confirm({"name": "A"}, {"name": "B"}),
            "verify": lambda res: res is False,
            "expected": "ยกเลิกการบันทึกทับและคืนค่า False เมื่อกด 'n' อย่างปลอดภัย"
        }
    ]

    passed_count = 0
    orig_stdin = sys.stdin
    orig_stdout = sys.stdout

    for idx, c in enumerate(cases, 1):
        # จำลอง input ผ่าน StringIO
        sys.stdin = io.StringIO(c["stream"])
        # ซ่อน stdout ของฟังก์ชันเพื่อไม่ให้แสดงผลกวนตารางสรุป
        sys.stdout = io.StringIO()
        try:
            res = c["action"]()
            is_ok = c["verify"](res)
        except Exception as e:
            res = f"Exception: {e}"
            is_ok = False
        finally:
            sys.stdin = orig_stdin
            sys.stdout = orig_stdout

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