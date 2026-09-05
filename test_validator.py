"""Unit test สำหรับ Validator (SCRUM-9) — mock builtins.input เพื่อจำลองผู้ใช้กรอกข้อมูล"""
import pytest

from validator import Validator


def _mock_inputs(monkeypatch, values):
    """ให้ input() คืนค่าตามลำดับใน values ทีละครั้งที่ถูกเรียก"""
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


# ------------------------------------------------------------------
# inputNonNegativeInt
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# inputNonNegativeFloat
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# confirm
# ------------------------------------------------------------------

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
    _mock_inputs(monkeypatch, ["maybe"])
    assert Validator.confirm({}, {}) is False
