"""Unit test สำหรับ ProductRepository (SCRUM-7) — ทดสอบกับฐานข้อมูลจริง (ไม่ mock) ตาม DoD"""
import pytest

from product import Product


# ------------------------------------------------------------------
# upsertProduct
# ------------------------------------------------------------------

def test_upsert_product_inserts_new_record(repo):
    p = Product(product_id="P1", name="Mama Noodles", quantity=50, price=6.0, category="Food")
    repo.upsertProduct(p)

    found = repo.findById("P1")
    assert found == p


def test_upsert_product_with_existing_id_updates_not_duplicates(repo):
    repo.upsertProduct(Product("P1", "Old Name", 5, 20.0, "Food"))
    repo.upsertProduct(Product("P1", "New Name", 8, 25.0, "Drink"))

    all_products = repo.findAll()
    matching = [p for p in all_products if p.product_id == "P1"]
    assert len(matching) == 1
    assert matching[0].name == "New Name"
    assert matching[0].quantity == 8


# ------------------------------------------------------------------
# findById
# ------------------------------------------------------------------

def test_find_by_id_returns_none_when_not_found(repo):
    assert repo.findById("NO_SUCH_ID") is None


def test_find_by_id_returns_correct_product(repo):
    repo.upsertProduct(Product("P2", "Lactasoy Milk", 20, 12.0, "Drink"))
    found = repo.findById("P2")
    assert found.name == "Lactasoy Milk"
    assert found.quantity == 20


# ------------------------------------------------------------------
# findAll
# ------------------------------------------------------------------

def test_find_all_returns_empty_list_when_no_products(repo):
    assert repo.findAll() == []


def test_find_all_returns_every_product_sorted_by_name(repo):
    repo.upsertProduct(Product("P1", "Zebra Snack", 1, 1.0))
    repo.upsertProduct(Product("P2", "Apple Juice", 1, 1.0))

    names = [p.name for p in repo.findAll()]
    assert names == ["Apple Juice", "Zebra Snack"]


# ------------------------------------------------------------------
# search
# ------------------------------------------------------------------

def test_search_matches_by_name(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    results = repo.search("Mama")
    assert len(results) == 1
    assert results[0].product_id == "P1"


def test_search_matches_by_category(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    repo.upsertProduct(Product("P2", "Singha Water", 10, 10.0, "Drink"))

    results = repo.search("Drink")
    assert len(results) == 1
    assert results[0].product_id == "P2"


def test_search_returns_empty_list_when_no_match(repo):
    repo.upsertProduct(Product("P1", "Mama Noodles", 10, 6.0, "Food"))
    assert repo.search("NotExist") == []


# ------------------------------------------------------------------
# updateStock
# ------------------------------------------------------------------

def test_update_stock_increases_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", 5, reason="restock")
    assert repo.findById("P1").quantity == 15


def test_update_stock_decreases_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", -4, reason="sale")
    assert repo.findById("P1").quantity == 6


def test_update_stock_records_stock_movement_history(repo, db):
    repo.upsertProduct(Product("P1", "Item", 10, 5.0))
    repo.updateStock("P1", -3, reason="cut stock test")

    cursor = db.executeQuery(
        "SELECT * FROM stock_movements WHERE product_id = ?", ("P1",)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["change_qty"] == -3
    assert row["reason"] == "cut stock test"


def test_update_stock_below_zero_raises_and_does_not_change_quantity(repo):
    repo.upsertProduct(Product("P1", "Item", 5, 5.0))
    with pytest.raises(ValueError):
        repo.updateStock("P1", -10)
    assert repo.findById("P1").quantity == 5  # ไม่ถูกแก้เมื่อ raise


def test_update_stock_on_missing_product_raises(repo):
    with pytest.raises(ValueError):
        repo.updateStock("NO_SUCH_ID", 5)


# ------------------------------------------------------------------
# getSummary
# ------------------------------------------------------------------

def test_get_summary_on_empty_repository(repo):
    summary = repo.getSummary()
    assert summary["total_products"] == 0
    assert summary["total_units"] == 0
    assert summary["total_value"] == 0
    assert summary["low_stock_items"] == 0


def test_get_summary_calculates_totals_correctly(repo):
    repo.upsertProduct(Product("P1", "Item A", quantity=10, price=6.0))
    repo.upsertProduct(Product("P2", "Item B", quantity=20, price=12.0))

    summary = repo.getSummary()
    assert summary["total_products"] == 2
    assert summary["total_units"] == 30
    assert summary["total_value"] == 10 * 6.0 + 20 * 12.0


def test_get_summary_counts_low_stock_items(repo):
    """threshold ต่ำสุดหรือเท่ากับ 5 ตาม query ตัวอย่างใน schema.sql"""
    repo.upsertProduct(Product("P1", "Low Stock Item", quantity=3, price=1.0))
    repo.upsertProduct(Product("P2", "Boundary Item", quantity=5, price=1.0))
    repo.upsertProduct(Product("P3", "Plenty Item", quantity=100, price=1.0))

    summary = repo.getSummary()
    assert summary["low_stock_items"] == 2  # P1 กับ P2 (<=5), P3 ไม่นับ
