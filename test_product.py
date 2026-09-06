"""Unit test สำหรับ Product (SCRUM-8 & CR-01)
รันด้วย pytest: python -m pytest -v test_product.py
รันแบบ Demo ใน Terminal: python test_product.py
"""
import pytest
from product import Product


# ============================================================
# Test Cases สำหรับ PyTest Framework
# ============================================================

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


# ============================================================
# ส่วนแสดงผล Terminal รายละเอียดเชิงลึกเมื่อรัน python test_product.py
# ============================================================

def _run_terminal_demo():
    print("=" * 85)
    print(" 📦  PRODUCT CLASS & CR-01 DEFINITION OF DONE VERIFICATION (TERMINAL AUDIT)")
    print("=" * 85)

    cases = [
        {
            "id": "TC-PROD-01",
            "method": "Constructor Equivalence & State Assertion",
            "data": "id='P1', name='Mama Noodles', qty=50, price=6.0, cat='Food'",
            "action": lambda: Product("P1", "Mama Noodles", 50, 6.0, "Food"),
            "verify": lambda res: res.product_id == "P1" and res.name == "Mama Noodles" and res.quantity == 50,
            "expected": "สร้าง Product Object สำเร็จ ค่าแอตทริบิวต์ตรงกับที่กำหนดทุกฟิลด์"
        },
        {
            "id": "TC-PROD-02",
            "method": "Negative Constraint Check (DoD Guard)",
            "data": "id='P3', name='Bad Qty', qty=-1, price=10.0",
            "action": lambda: _check_error(lambda: Product("P3", "Bad Qty", -1, 10.0)),
            "verify": lambda res: res == "ValueError",
            "expected": "ปฏิเสธค่าติดลบ ทริกเกอร์ ValueError ทันทีในระดับ Constructor"
        },
        {
            "id": "TC-PROD-03",
            "method": "Empty Primary Key Guard",
            "data": "id='', name='No Id', qty=1, price=1.0",
            "action": lambda: _check_error(lambda: Product("", "No Id", 1, 1.0)),
            "verify": lambda res: res == "ValueError",
            "expected": "ปฏิเสธค่าว่าง ป้องกันการสร้างเรคคอร์ดขยะในฐานข้อมูล"
        },
        {
            "id": "TC-PROD-04",
            "method": "Zero Boundary Equivalence",
            "data": "id='P6', name='Free Sample', qty=0, price=0.0",
            "action": lambda: Product("P6", "Free Sample", 0, 0.0),
            "verify": lambda res: res.quantity == 0 and res.price == 0.0,
            "expected": "ยอมรับค่า 0.0 (ของแถมหรือสินค้าหมดชั่วคราว) โดยไม่ Error"
        },
        {
            "id": "TC-CR01-01",
            "method": "CR-01: Boundary Analysis (qty < reorder_point)",
            "data": "qty=3, reorder_point=5 (3 < 5)",
            "action": lambda: Product("P12", "Low Item", 3, 1.0, reorder_point=5).is_low_stock(),
            "verify": lambda res: res is True,
            "expected": "is_low_stock() คืนค่า True -> แจ้งเตือนสินค้าต่ำกว่าเกณฑ์"
        },
        {
            "id": "TC-CR01-02",
            "method": "CR-01: Boundary Edge Case (qty == reorder_point)",
            "data": "qty=5, reorder_point=5 (5 == 5)",
            "action": lambda: Product("P13", "Boundary Item", 5, 1.0, reorder_point=5).is_low_stock(),
            "verify": lambda res: res is True,
            "expected": "is_low_stock() คืนค่า True -> นับสินค้าที่แตะเส้นพอดีเข้ากลุ่มวิกฤต"
        },
        {
            "id": "TC-CR01-03",
            "method": "CR-01: Normal Condition (qty > reorder_point)",
            "data": "qty=6, reorder_point=5 (6 > 5)",
            "action": lambda: Product("P14", "Normal Item", 6, 1.0, reorder_point=5).is_low_stock(),
            "verify": lambda res: res is False,
            "expected": "is_low_stock() คืนค่า False -> สถานะสต็อกปกติ ไม่ส่งสัญญาณเตือน"
        },
        {
            "id": "TC-CR01-04",
            "method": "CR-01: Backward Compatibility (Default Fallback)",
            "data": "ละเว้นพารามิเตอร์ barcode และ reorder_point",
            "action": lambda: Product("P11", "Legacy Item", 10, 5.0),
            "verify": lambda res: res.barcode == "" and res.reorder_point == 5,
            "expected": "ตั้งค่าปริยายอัตโนมัติ (barcode='', reorder_point=5) ไม่ทำลายโค้ดเก่า"
        },
        {
            "id": "TC-PROD-05",
            "method": "Persistence Interoperability (to_dict Serialization)",
            "data": "Product(id='P15', barcode='123456', reorder_point=3)",
            "action": lambda: Product("P15", "Item", 5, 9.5, barcode="123456", reorder_point=3).to_dict(),
            "verify": lambda res: isinstance(res, dict) and res["barcode"] == "123456" and res["reorder_point"] == 3,
            "expected": "แปลงเป็น Dict ครบ 7 คีย์ พร้อมส่งต่อให้ Repository และ Logging ทันที"
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


def _check_error(fn):
    try:
        fn()
        return "No Error"
    except ValueError:
        return "ValueError"
    except Exception as e:
        return type(e).__name__


if __name__ == "__main__":
    _run_terminal_demo()
