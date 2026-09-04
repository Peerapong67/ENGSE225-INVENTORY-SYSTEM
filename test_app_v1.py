"""
Unit test สำหรับ app_v1.py (เวอร์ชันปัจจุบันของ develop ที่ยังไม่ refactor)

ไฟล์นี้วางไว้ที่ root ของ repo เดียวกับ app_v1.py ตรงๆ (ไม่มี src/ หรือ tests/)
ตามโครงสร้างที่ใช้งานจริงบน branch develop

app_v1.py ใช้ global variable (x, db) และเป็นโปรแกรมแบบ interactive (input()/print())
เทสต์นี้เลยต้อง:
  1) reset global state (x, db) ก่อนทุกเทสต์ ไม่ให้เทสต์ก่อนหน้าเหลือค้าง
  2) monkeypatch "db" ให้ชี้ไปไฟล์ json ชั่วคราว (tmp_path) แยกจาก data.json จริง
  3) monkeypatch builtins.input ด้วยลำดับค่าที่จำลองผู้ใช้พิมพ์ แล้วอ่านผลลัพธ์
     ผ่าน capsys (stdout) หรือตรวจ global x/ไฟล์ json โดยตรง
"""
import json
import pytest

import app_v1


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """รีเซ็ต global x และชี้ db ไปไฟล์ชั่วคราวก่อนทุกเทสต์"""
    monkeypatch.setattr(app_v1, "db", str(tmp_path / "test_data.json"))
    monkeypatch.setattr(app_v1, "x", {})
    yield


def run_menu(monkeypatch, inputs):
    """ป้อนลำดับ input ตามที่กำหนด แล้วรัน main() จนจบ (ต้องมี '5' ปิดท้ายเสมอ)"""
    it = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))
    app_v1.main()


def write_data_file(data: dict):
    with open(app_v1.db, "w") as f:
        json.dump(data, f)


# ------------------------------------------------------------------
# load()
# ------------------------------------------------------------------

def test_load_creates_default_data_when_file_missing():
    app_v1.load()
    assert set(app_v1.x.keys()) == {"101", "102", "103"}
    assert app_v1.x["101"]["n"] == "Mama Noodles"


def test_load_reads_existing_json_file():
    write_data_file({"999": {"n": "Custom Item", "q": 3, "p": 15.0, "c": "Snack"}})
    app_v1.load()
    assert app_v1.x == {"999": {"n": "Custom Item", "q": 3, "p": 15.0, "c": "Snack"}}


# ------------------------------------------------------------------
# save()
# ------------------------------------------------------------------

def test_save_writes_current_state_to_file():
    app_v1.x = {"1": {"n": "Item A", "q": 5, "p": 9.0, "c": "Food"}}
    app_v1.save()

    with open(app_v1.db, "r") as f:
        saved = json.load(f)
    assert saved == {"1": {"n": "Item A", "q": 5, "p": 9.0, "c": "Food"}}


def test_save_after_load_persists_default_data():
    app_v1.load()
    app_v1.save()

    with open(app_v1.db, "r") as f:
        saved = json.load(f)
    assert "101" in saved


# ------------------------------------------------------------------
# main() -> choice "1" (Show all)
# ------------------------------------------------------------------

def test_menu_show_all_prints_every_product(monkeypatch, capsys):
    write_data_file({"1": {"n": "Coffee", "q": 10, "p": 45.0, "c": "Drink"}})
    run_menu(monkeypatch, ["1", "5"])

    out = capsys.readouterr().out
    assert "Coffee" in out
    assert "45.0" in out


# ------------------------------------------------------------------
# main() -> choice "2" (Add or Update)
# ------------------------------------------------------------------

def test_menu_add_new_product_saves_to_file(monkeypatch):
    write_data_file({})
    run_menu(monkeypatch, ["2", "P1", "New Item", "10", "20.0", "Food", "5"])

    with open(app_v1.db, "r") as f:
        saved = json.load(f)
    assert saved["P1"] == {"n": "New Item", "q": 10, "p": 20.0, "c": "Food"}


def test_menu_add_or_update_overwrites_existing_id(monkeypatch):
    write_data_file({"P1": {"n": "Old Name", "q": 1, "p": 1.0, "c": "Old"}})
    run_menu(monkeypatch, ["2", "P1", "New Name", "8", "25.0", "Drink", "5"])

    with open(app_v1.db, "r") as f:
        saved = json.load(f)
    assert saved["P1"] == {"n": "New Name", "q": 8, "p": 25.0, "c": "Drink"}
    assert len(saved) == 1  # ต้องไม่มีแถวซ้ำ (ยืนยันเคสที่ risk register เตือนไว้)


# ------------------------------------------------------------------
# main() -> choice "3" (Cut stock / Out)
# ------------------------------------------------------------------

def test_menu_cut_stock_reduces_quantity(monkeypatch):
    write_data_file({"P1": {"n": "Item", "q": 20, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "5", "5"])

    with open(app_v1.db, "r") as f:
        saved = json.load(f)
    assert saved["P1"]["q"] == 15


def test_menu_cut_stock_insufficient_stock_shows_error_and_does_not_change(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 3, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "10", "5"])

    out = capsys.readouterr().out
    assert "Not enough stock" in out
    with open(app_v1.db, "r") as f:
        # save() ไม่ควรถูกเรียกตอน error ไฟล์ควรยังเป็นค่าดั้งเดิม
        saved = json.load(f)
    assert saved["P1"]["q"] == 3


def test_menu_cut_stock_product_not_found_shows_error(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 10, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "NO_SUCH_ID", "5"])

    out = capsys.readouterr().out
    assert "Product not found" in out


def test_menu_cut_stock_triggers_low_stock_warning_below_5(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 6, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "2", "5"])  # เหลือ 4 -> ต้องเตือน (< 5)

    out = capsys.readouterr().out
    assert "WARNING" in out


def test_menu_cut_stock_no_warning_when_stock_stays_at_or_above_5(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 10, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "5", "5"])  # เหลือ 5 -> ยังไม่ต้องเตือน (ไม่ < 5)

    out = capsys.readouterr().out
    assert "WARNING" not in out


# ------------------------------------------------------------------
# main() -> choice "4" (Check Check / Summary)
# ------------------------------------------------------------------

def test_menu_summary_calculates_total_items_and_value(monkeypatch, capsys):
    write_data_file({
        "P1": {"n": "Item A", "q": 10, "p": 6.0, "c": "Food"},
        "P2": {"n": "Item B", "q": 5, "p": 12.0, "c": "Drink"},
    })
    run_menu(monkeypatch, ["4", "5"])

    out = capsys.readouterr().out
    assert "Total product types: 2" in out
    assert "Total inventory value: 120.0 THB" in out  # 10*6 + 5*12 = 120


def test_menu_summary_lists_low_stock_items_below_10(monkeypatch, capsys):
    write_data_file({
        "P1": {"n": "Low Item", "q": 3, "p": 6.0, "c": "Food"},
        "P2": {"n": "Plenty Item", "q": 100, "p": 12.0, "c": "Drink"},
    })
    run_menu(monkeypatch, ["4", "5"])

    out = capsys.readouterr().out
    assert "Low Item" in out
    assert "Plenty Item" not in out.split("Alert low stock")[-1]


# ------------------------------------------------------------------
# main() -> choice "5" (Exit) / invalid choice
# ------------------------------------------------------------------

def test_menu_exit_stops_the_loop(monkeypatch, capsys):
    write_data_file({})
    run_menu(monkeypatch, ["5"])
    out = capsys.readouterr().out
    assert "Bye" in out


def test_menu_invalid_choice_shows_message_then_can_still_exit(monkeypatch, capsys):
    write_data_file({})
    run_menu(monkeypatch, ["9", "5"])
    out = capsys.readouterr().out
    assert "Invalid choice" in out
