import pytest

from database_connection import DatabaseConnection
from logger import Logger


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    รีเซ็ต Singleton ของ DatabaseConnection และ Logger ก่อน/หลังทุกเทสต์
    ทั้งสองคลาสเก็บ instance ไว้เป็น class attribute ถ้าไม่รีเซ็ต เทสต์แต่ละเคส
    จะแชร์ connection/state เดิมข้ามกัน ทำให้ผลเทสต์ปนกันและ debug ยาก
    """
    DatabaseConnection._instance = None
    Logger._instance = None
    yield
    if DatabaseConnection._instance is not None:
        try:
            DatabaseConnection._instance.connection.close()
        except Exception:
            pass
    DatabaseConnection._instance = None
    Logger._instance = None


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """
    chdir เข้าโฟลเดอร์ชั่วคราวของ pytest (tmp_path) เพื่อให้ไฟล์ .db ที่สร้าง
    ระหว่างเทสต์ (เช่น "test_inventory.db") แยกออกจากไฟล์ .db จริงของโปรแกรม
    และไม่ค้างเกะกะหลังเทสต์จบ (pytest ลบ tmp_path ให้อัตโนมัติ)

    ไม่ต้อง copy schema.sql เข้ามาแล้ว เพราะ database_connection.py หา schema.sql
    ด้วย path แบบ absolute อิงตำแหน่งไฟล์ __file__ ของมันเอง (src/../schema.sql)
    ซึ่งไม่ขึ้นกับ working directory อีกต่อไป
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def db(isolated_cwd):
    """DatabaseConnection instance ที่ชี้ไปยัง .db ชั่วคราวสำหรับแต่ละเทสต์"""
    return DatabaseConnection.getInstance("test_inventory.db")


@pytest.fixture
def repo(db):
    """ProductRepository ผูกกับ DatabaseConnection ทดสอบ"""
    from product_repository import ProductRepository
    return ProductRepository(db)
