"""Unit test สำหรับ Product (SCRUM-8) — ไม่ต้องพึ่งฐานข้อมูล เทสต์ตัว object เพียวๆ"""
import pytest

from product import Product


def test_create_product_with_valid_data():
    p = Product(product_id="P1", name="Mama Noodles", quantity=50, price=6.0, category="Food")
    assert p.product_id == "P1"
    assert p.name == "Mama Noodles"
    assert p.quantity == 50
    assert p.price == 6.0
    assert p.category == "Food"


def test_create_product_uses_default_category_when_omitted():
    p = Product(product_id="P2", name="No Category Item", quantity=1, price=1.0)
    assert p.category == "Uncategorized"


def test_create_product_with_negative_quantity_raises():
    with pytest.raises(ValueError):
        Product(product_id="P3", name="Bad Qty", quantity=-1, price=10.0)


def test_create_product_with_negative_price_raises():
    with pytest.raises(ValueError):
        Product(product_id="P4", name="Bad Price", quantity=1, price=-5.0)


def test_create_product_with_empty_id_raises():
    with pytest.raises(ValueError):
        Product(product_id="", name="No Id", quantity=1, price=1.0)


def test_create_product_with_empty_name_raises():
    with pytest.raises(ValueError):
        Product(product_id="P5", name="", quantity=1, price=1.0)


def test_create_product_allows_zero_quantity_and_price():
    """ค่าเท่ากับ 0 ต้องผ่าน (ไม่ใช่แค่ค่าติดลบเท่านั้นที่ห้าม)"""
    p = Product(product_id="P6", name="Free Sample", quantity=0, price=0.0)
    assert p.quantity == 0
    assert p.price == 0.0


def test_to_dict_returns_all_fields():
    p = Product(product_id="P7", name="Item", quantity=5, price=9.5, category="Drink")
    assert p.to_dict() == {
        "product_id": "P7",
        "name": "Item",
        "quantity": 5,
        "price": 9.5,
        "category": "Drink",
        "barcode": "",
        "reorder_point": 5,
    }


def test_from_row_builds_equivalent_product():
    """from_row ต้องสร้าง Product ที่ค่าตรงกับที่ ProductRepository จะอ่านจาก sqlite3.Row"""
    row = {"product_id": "P8", "name": "Row Item", "quantity": 3, "price": 4.5, "category": "Food"}
    p = Product.from_row(row)
    assert p == Product(product_id="P8", name="Row Item", quantity=3, price=4.5, category="Food")


def test_equality_compares_by_value():
    a = Product(product_id="P9", name="A", quantity=1, price=1.0, category="X")
    b = Product(product_id="P9", name="A", quantity=1, price=1.0, category="X")
    c = Product(product_id="P9", name="A", quantity=2, price=1.0, category="X")
    assert a == b
    assert a != c


# ============================================================
# CR-01: Barcode & Reorder Point Alert (SCRUM-CR01)
# ============================================================

def test_create_product_with_barcode_and_reorder_point():
    p = Product(product_id="P10", name="Scanned Item", quantity=20, price=15.0,
                category="Food", barcode="8850999327015", reorder_point=8)
    assert p.barcode == "8850999327015"
    assert p.reorder_point == 8


def test_create_product_uses_default_barcode_and_reorder_point_when_omitted():
    """Backward Compatibility: โค้ดเก่าที่สร้าง Product โดยไม่ส่ง barcode/reorder_point
    ต้องยังทำงานได้เหมือนเดิม ไม่พัง (ตามที่สไลด์ Week 9 กำหนด)"""
    p = Product(product_id="P11", name="Legacy Item", quantity=10, price=5.0)
    assert p.barcode == ""
    assert p.reorder_point == 5


def test_is_low_stock_true_when_quantity_below_reorder_point():
    p = Product(product_id="P12", name="Low Item", quantity=3, price=1.0, reorder_point=5)
    assert p.is_low_stock() is True


def test_is_low_stock_true_when_quantity_equals_reorder_point():
    """Boundary Case (TC-CR01-02 ในสไลด์): quantity == reorder_point ต้องนับว่าต่ำแล้ว"""
    p = Product(product_id="P13", name="Boundary Item", quantity=5, price=1.0, reorder_point=5)
    assert p.is_low_stock() is True


def test_is_low_stock_false_when_quantity_above_reorder_point():
    p = Product(product_id="P14", name="Normal Item", quantity=6, price=1.0, reorder_point=5)
    assert p.is_low_stock() is False


def test_to_dict_includes_barcode_and_reorder_point():
    p = Product(product_id="P15", name="Item", quantity=5, price=9.5, category="Drink",
                barcode="123456", reorder_point=3)
    assert p.to_dict() == {
        "product_id": "P15",
        "name": "Item",
        "quantity": 5,
        "price": 9.5,
        "category": "Drink",
        "barcode": "123456",
        "reorder_point": 3,
    }


def test_from_row_builds_product_with_barcode_and_reorder_point():
    row = {"product_id": "P16", "name": "Row Item", "quantity": 3, "price": 4.5,
           "category": "Food", "barcode": "999888", "reorder_point": 4}
    p = Product.from_row(row)
    assert p.barcode == "999888"
    assert p.reorder_point == 4
