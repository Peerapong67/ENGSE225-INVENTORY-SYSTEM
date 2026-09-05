"""Unit test สำหรับ Logger (SCRUM-10) — ทดสอบกับฐานข้อมูลจริง (ไม่ mock) ตาม DoD"""
import pytest

from logger import Logger


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
    import sqlite3
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
