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
