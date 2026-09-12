"""
Unit test สำหรับ app_v1.py (เวอร์ชันดั้งเดิมก่อน refactor)
รันด้วย pytest: python -m pytest -v test_app_v1.py
รันแบบ Demo ใน Terminal: python test_app_v1.py
"""
import io
import os
import sys
import json
import pytest

import app_v1


# ============================================================
# Fixtures สำหรับ PyTest
# ============================================================

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
    with open(app_v1.db, "w", encoding="utf-8") as f:
        json.dump(data, f)


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

def test_load_creates_default_data_when_file_missing():
    app_v1.load()
    assert set(app_v1.x.keys()) == {"101", "102", "103"}
    assert app_v1.x["101"]["n"] == "Mama Noodles"


def test_load_reads_existing_json_file():
    write_data_file({"999": {"n": "Custom Item", "q": 3, "p": 15.0, "c": "Snack"}})
    app_v1.load()
    assert app_v1.x == {"999": {"n": "Custom Item", "q": 3, "p": 15.0, "c": "Snack"}}


def test_save_writes_current_state_to_file():
    app_v1.x = {"1": {"n": "Item A", "q": 5, "p": 9.0, "c": "Food"}}
    app_v1.save()

    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == {"1": {"n": "Item A", "q": 5, "p": 9.0, "c": "Food"}}


def test_save_after_load_persists_default_data():
    app_v1.load()
    app_v1.save()

    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert "101" in saved


def test_menu_show_all_prints_every_product(monkeypatch, capsys):
    write_data_file({"1": {"n": "Coffee", "q": 10, "p": 45.0, "c": "Drink"}})
    run_menu(monkeypatch, ["1", "5"])

    out = capsys.readouterr().out
    assert "Coffee" in out
    assert "45.0" in out


def test_menu_add_new_product_saves_to_file(monkeypatch):
    write_data_file({})
    run_menu(monkeypatch, ["2", "P1", "New Item", "10", "20.0", "Food", "5"])

    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["P1"] == {"n": "New Item", "q": 10, "p": 20.0, "c": "Food"}


def test_menu_add_or_update_overwrites_existing_id(monkeypatch):
    write_data_file({"P1": {"n": "Old Name", "q": 1, "p": 1.0, "c": "Old"}})
    run_menu(monkeypatch, ["2", "P1", "New Name", "8", "25.0", "Drink", "5"])

    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["P1"] == {"n": "New Name", "q": 8, "p": 25.0, "c": "Drink"}
    assert len(saved) == 1


def test_menu_cut_stock_reduces_quantity(monkeypatch):
    write_data_file({"P1": {"n": "Item", "q": 20, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "5", "5"])

    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["P1"]["q"] == 15


def test_menu_cut_stock_insufficient_stock_shows_error_and_does_not_change(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 3, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "10", "5"])

    out = capsys.readouterr().out
    assert "Not enough stock" in out
    with open(app_v1.db, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["P1"]["q"] == 3


def test_menu_cut_stock_product_not_found_shows_error(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 10, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "NO_SUCH_ID", "5"])

    out = capsys.readouterr().out
    assert "Product not found" in out


def test_menu_cut_stock_triggers_low_stock_warning_below_5(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 6, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "2", "5"])

    out = capsys.readouterr().out
    assert "WARNING" in out


def test_menu_cut_stock_no_warning_when_stock_stays_at_or_above_5(monkeypatch, capsys):
    write_data_file({"P1": {"n": "Item", "q": 10, "p": 5.0, "c": "Food"}})
    run_menu(monkeypatch, ["3", "P1", "5", "5"])

    out = capsys.readouterr().out
    assert "WARNING" not in out


def test_menu_summary_calculates_total_items_and_value(monkeypatch, capsys):
    write_data_file({
        "P1": {"n": "Item A", "q": 10, "p": 6.0, "c": "Food"},
        "P2": {"n": "Item B", "q": 5, "p": 12.0, "c": "Drink"},
    })
    run_menu(monkeypatch, ["4", "5"])

    out = capsys.readouterr().out
    assert "Total product types: 2" in out
    assert "Total inventory value: 120.0 THB" in out


def test_menu_summary_lists_low_stock_items_below_10(monkeypatch, capsys):
    write_data_file({
        "P1": {"n": "Low Item", "q": 3, "p": 6.0, "c": "Food"},
        "P2": {"n": "Plenty Item", "q": 100, "p": 12.0, "c": "Drink"},
    })
    run_menu(monkeypatch, ["4", "5"])

    out = capsys.readouterr().out
    assert "Low Item" in out
    assert "Plenty Item" not in out.split("Alert low stock")[-1]


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


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_app_v1.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 📜  LEGACY CODE REGRESSION SUITE (APP_V1.PY) VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    temp_json = "temp_terminal_test_data.json"
    app_v1.db = temp_json

    cases = [
        {
            "id": "TC-LEGACY-01",
            "method": "Default Seed Generation on Missing File",
            "data": "ไม่พบไฟล์ JSON ในระบบ",
            "action": lambda: _test_legacy_load_default(temp_json),
            "verify": lambda res: "101" in res and res["101"]["n"] == "Mama Noodles",
            "expected": "โหลดข้อมูลเริ่มต้น 3 รายการ (Mama, Lactasoy, Singha) สำเร็จ"
        },
        {
            "id": "TC-LEGACY-02",
            "method": "JSON File Deserialization Verification",
            "data": "อ่านไฟล์ที่มี ID='999', Name='Custom Item'",
            "action": lambda: _test_legacy_load_file(temp_json),
            "verify": lambda res: "999" in res and res["999"]["n"] == "Custom Item",
            "expected": "อ่านและแปลง JSON ลงตัวแปร Dictionary x ได้ตรงตามไฟล์เป๊ะ"
        },
        {
            "id": "TC-LEGACY-03",
            "method": "Legacy JSON Serialization & Write",
            "data": "บันทึก Dictionary x={'1': {'n': 'Item A', 'q': 5, 'p': 9.0}}",
            "action": lambda: _test_legacy_save(temp_json),
            "verify": lambda res: res.get("1", {}).get("n") == "Item A",
            "expected": "เขียนข้อมูลลงดิสก์สำเร็จ ไฟล์ JSON อัปเดตข้อมูลตรงกัน 100%"
        },
        {
            "id": "TC-LEGACY-04",
            "method": "Legacy Flow: Add Product via CLI Menu",
            "data": "เมนู 2 -> ID='P1', Name='New Item', Qty=10, Price=20.0, Cat='Food'",
            "action": lambda: _test_legacy_add(temp_json),
            "verify": lambda out: "Done." in out and app_v1.x.get("P1", {}).get("q") == 10,
            "expected": "เพิ่มสินค้าใหม่ลงตัวแปร x และเซฟลง JSON สำเร็จ แสดงผล 'Done.'"
        },
        {
            "id": "TC-LEGACY-05",
            "method": "Legacy Flow: Overwrite Existing Record",
            "data": "เมนู 2 ซ้ำ ID เดิม -> ID='P1', Name='New Name', Qty=8, Price=25.0",
            "action": lambda: _test_legacy_overwrite(temp_json),
            "verify": lambda out: app_v1.x.get("P1", {}).get("n") == "New Name" and len(app_v1.x) == 1,
            "expected": "เขียนทับข้อมูล ID เดิมสำเร็จ ไม่เกิดข้อมูลซ้ำซ้อน"
        },
        {
            "id": "TC-LEGACY-06",
            "method": "Legacy Flow: Stock Deduction & Calculation",
            "data": "เมนู 3 -> ตัดสต็อกสินค้า 'P1' ออก 3 ชิ้น (เดิมมี 8 เหลือ 5)",
            "action": lambda: _run_legacy_cli(["3", "P1", "3", "5"]),
            "verify": lambda out: "Stock updated." in out and app_v1.x["P1"]["q"] == 5,
            "expected": "ลดจำนวนสต็อกลงเหลือ 5 ชิ้นถูกต้อง และแสดงผล 'Stock updated.'"
        },
        {
            "id": "TC-LEGACY-07",
            "method": "Legacy Flow: Insufficient Stock Protection",
            "data": "เมนู 3 -> ตัดสต็อกเกินจำนวน (มี 5 ชิ้น แต่สั่งตัด 10 ชิ้น)",
            "action": lambda: _run_legacy_cli(["3", "P1", "10", "5"]),
            "verify": lambda out: "Error: Not enough stock!" in out and app_v1.x["P1"]["q"] == 5,
            "expected": "ปฏิเสธการตัดสต็อก ยอดคงเหลือไม่เปลี่ยนแปลง และเตือนข้อผิดพลาด"
        },
        {
            "id": "TC-LEGACY-08",
            "method": "Legacy Flow: Critical Stock Warning (< 5 Threshold)",
            "data": "เมนู 3 -> ตัดสต็อก 'P1' ออก 2 ชิ้น (เหลือ 3 ชิ้น ซึ่ง < 5)",
            "action": lambda: _run_legacy_cli(["3", "P1", "2", "5"]),
            "verify": lambda out: "WARNING: ITEM IS RUNNING VERY LOW IN STOCK" in out,
            "expected": "ส่งเสียงแจ้งเตือนข้อความ WARNING เมื่อสต็อกคงเหลือต่ำกว่า 5"
        },
        {
            "id": "TC-LEGACY-09",
            "method": "Legacy Flow: Inventory Aggregation Report",
            "data": "เมนู 4 (Check Check) สรุปยอดคลังสินค้า",
            "action": lambda: _run_legacy_cli(["4", "5"]),
            "verify": lambda out: "Total product types:" in out and "Total inventory value:" in out,
            "expected": "คำนวณจำนวนชนิดสินค้า และมูลค่าสต็อกรวมได้อย่างถูกต้อง"
        }
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

    if os.path.exists(temp_json):
        try:
            os.remove(temp_json)
        except PermissionError:
            pass


def _test_legacy_load_default(temp_json):
    if os.path.exists(temp_json):
        os.remove(temp_json)
    app_v1.x = {}
    app_v1.load()
    return app_v1.x


def _test_legacy_load_file(temp_json):
    data = {"999": {"n": "Custom Item", "q": 3, "p": 15.0, "c": "Snack"}}
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(data, f)
    app_v1.x = {}
    app_v1.load()
    return app_v1.x


def _test_legacy_save(temp_json):
    app_v1.x = {"1": {"n": "Item A", "q": 5, "p": 9.0, "c": "Food"}}
    app_v1.save()
    with open(temp_json, "r", encoding="utf-8") as f:
        return json.load(f)


def _test_legacy_add(temp_json):
    app_v1.x = {}
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump({}, f)
    return _run_legacy_cli(["2", "P1", "New Item", "10", "20.0", "Food", "5"])


def _test_legacy_overwrite(temp_json):
    app_v1.x = {"P1": {"n": "Old Name", "q": 1, "p": 1.0, "c": "Old"}}
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(app_v1.x, f)
    return _run_legacy_cli(["2", "P1", "New Name", "8", "25.0", "Drink", "5"])


def _run_legacy_cli(inputs):
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO("\n".join(inputs) + "\n")
    captured = io.StringIO()
    sys.stdout = captured
    try:
        app_v1.main()
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
    return captured.getvalue()


if __name__ == "__main__":
    _run_terminal_demo()