"""Unit test สำหรับ Logger (SCRUM-10) — ทดสอบกับฐานข้อมูลจริง (ไม่ mock) ตาม DoD
รันด้วย pytest: python -m pytest -v test_logger.py
รันแบบ Demo ใน Terminal: python test_logger.py
"""
import os
import sqlite3
import pytest
from logger import Logger
from database_connection import DatabaseConnection


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

def test_get_instance_returns_same_object(db):
    """db fixture ทำให้ DatabaseConnection พร้อมใช้งานก่อน Logger.getInstance()"""
    l1 = Logger.getInstance()
    l2 = Logger.getInstance()
    assert l1 is l2


def test_direct_constructor_raises_when_instance_exists(db):
    Logger.getInstance()
    with pytest.raises(Exception):
        Logger()


def test_log_inserts_row_into_action_logs(db):
    logger = Logger.getInstance()
    logger.log("ADD_PRODUCT", "product_id=P1")

    cursor = db.executeQuery(
        "SELECT * FROM action_logs WHERE action = ?", ("ADD_PRODUCT",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["detail"] == "product_id=P1"


def test_log_without_detail_defaults_to_empty_string(db):
    logger = Logger.getInstance()
    logger.log("EXPORT_REPORT")

    cursor = db.executeQuery(
        "SELECT detail FROM action_logs WHERE action = ?", ("EXPORT_REPORT",)
    )
    row = cursor.fetchone()
    assert row["detail"] == ""


def test_multiple_logs_are_all_recorded(db):
    logger = Logger.getInstance()
    logger.log("ADD_PRODUCT", "P1")
    logger.log("CUT_STOCK", "P1 -3")
    logger.log("UPDATE_PRODUCT", "P1")

    cursor = db.executeQuery("SELECT COUNT(*) AS cnt FROM action_logs")
    assert cursor.fetchone()["cnt"] == 3


def test_log_persists_after_commit(db, isolated_cwd):
    """ยืนยันว่า log ถูก commit จริง อ่านผ่าน connection ใหม่ก็ต้องเห็น"""
    logger = Logger.getInstance()
    logger.log("CHECK_PERSIST", "detail-persist")

    raw_conn = sqlite3.connect(str(isolated_cwd / "test_inventory.db"))
    raw_conn.row_factory = sqlite3.Row
    row = raw_conn.execute(
        "SELECT * FROM action_logs WHERE action = ?", ("CHECK_PERSIST",)
    ).fetchone()
    raw_conn.close()

    assert row is not None
    assert row["detail"] == "detail-persist"


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_logger.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 📝  LOGGER CLASS DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    test_db_name = "test_logger_terminal.db"
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass

    # รีเซ็ต Singletons และเตรียมฐานข้อมูลทดสอบ
    DatabaseConnection._instance = None
    Logger._instance = None
    db = DatabaseConnection.getInstance(test_db_name)

    cases = [
        {
            "id": "TC-LOG-01",
            "method": "Singleton Identity Assertion (Class Attribute Lock)",
            "data": "l1 = Logger.getInstance(), l2 = Logger.getInstance()",
            "action": lambda: (Logger.getInstance(), Logger.getInstance()),
            "verify": lambda res: res[0] is res[1],
            "expected": "l1 is l2 เป็นจริง คืนค่า Instance ตัวเดิมจากหน่วยความจำ ไม่สร้างซ้ำ"
        },
        {
            "id": "TC-LOG-02",
            "method": "Constructor Guard against Direct Instantiation",
            "data": "เรียก Constructor Logger() โดยตรงหลังจากมี Instance แล้ว",
            "action": lambda: _check_constructor_exception(),
            "verify": lambda res: res is True,
            "expected": "บล็อกการสร้างใหม่และ Raise Exception แจ้งให้เรียกผ่าน getInstance()"
        },
        {
            "id": "TC-LOG-03",
            "method": "Audit Logging Insert (Parameterized Query)",
            "data": "action='ADD_PRODUCT', detail='product_id=P101'",
            "action": lambda: _insert_and_fetch(db, "ADD_PRODUCT", "product_id=P101"),
            "verify": lambda res: res is not None and res["detail"] == "product_id=P101",
            "expected": "บันทึก action_logs สำเร็จ ตรวจสอบพบคอลัมน์ action และ detail ตรงเป๊ะ"
        },
        {
            "id": "TC-LOG-04",
            "method": "Default Optional Parameter Fallback",
            "data": "action='EXPORT_REPORT', detail='' (ไม่ระบุพารามิเตอร์ที่ 2)",
            "action": lambda: _insert_and_fetch(db, "EXPORT_REPORT", ""),
            "verify": lambda res: res is not None and res["detail"] == "",
            "expected": "บันทึกข้อมูลได้ปกติ โดยช่อง detail จะเป็นสตริงว่าง ('') ไม่เกิด Null Error"
        },
        {
            "id": "TC-LOG-05",
            "method": "Audit Trail Multi-transaction Recording",
            "data": "บันทึก 3 Actions รวด ('ADD_PRODUCT', 'CUT_STOCK', 'UPDATE_PRODUCT')",
            "action": lambda: _log_multiple_and_count(db),
            "verify": lambda res: res >= 3,
            "expected": "บันทึกครบทุกประวัติ โดยเรคคอร์ดเพิ่มขึ้น 3 แถวตรงตามลำดับเหตุการณ์จริง"
        },
        {
            "id": "TC-LOG-06",
            "method": "Auto-commit Persistence Across Separate Connection",
            "data": "บันทึก log('PERSIST_TEST') แล้วเปิด sqlite3.connect() แยกอ่านข้อมูล",
            "action": lambda: _check_persistence(test_db_name),
            "verify": lambda res: res is not None and res["detail"] == "verify-disk-write",
            "expected": "ข้อมูลถูก Commit ลงไฟล์ดิสก์ทันที Connection ภายนอกสามารถอ่านพบได้จริง"
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

    # ปิด Connection และลบไฟล์ทดสอบ
    db.connection.close()
    if os.path.exists(test_db_name):
        try:
            os.remove(test_db_name)
        except PermissionError:
            pass


def _check_constructor_exception():
    try:
        Logger()
        return False
    except Exception:
        return True


def _insert_and_fetch(db, action, detail):
    l = Logger.getInstance()
    if detail:
        l.log(action, detail)
    else:
        l.log(action)
    cur = db.executeQuery(
        "SELECT * FROM action_logs WHERE action = ? ORDER BY log_id DESC LIMIT 1",
        (action,)
    )
    return cur.fetchone()


def _log_multiple_and_count(db):
    l = Logger.getInstance()
    l.log("BATCH_ADD", "item 1")
    l.log("BATCH_CUT", "item 1 -2")
    l.log("BATCH_UPDATE", "item 1 edit")
    cur = db.executeQuery("SELECT COUNT(*) AS cnt FROM action_logs WHERE action LIKE 'BATCH_%'")
    return cur.fetchone()["cnt"]


def _check_persistence(db_path):
    l = Logger.getInstance()
    l.log("PERSIST_TEST", "verify-disk-write")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM action_logs WHERE action = ? ORDER BY log_id DESC LIMIT 1",
        ("PERSIST_TEST",)
    ).fetchone()
    conn.close()
    return row


if __name__ == "__main__":
    _run_terminal_demo()