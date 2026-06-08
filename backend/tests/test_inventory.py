def test_list_inventory(client, seed_product):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["quantity_available"] == 50


def test_add_stock(client, seed_product):
    response = client.post(f"/inventory/{seed_product.product_id}/stock-in", json={
        "quantity": 20,
        "reason": "Restock",
    })
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 70


def test_remove_stock(client, seed_product):
    response = client.post(f"/inventory/{seed_product.product_id}/stock-out", json={
        "quantity": 10,
        "reason": "Damaged goods",
    })
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 40


def test_adjust_stock(client, seed_product):
    response = client.post(f"/inventory/{seed_product.product_id}/adjust", json={
        "new_quantity": 100,
        "reason": "Cycle count",
    })
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 100


def test_insufficient_stock_blocked(client, seed_product):
    response = client.post(f"/inventory/{seed_product.product_id}/stock-out", json={
        "quantity": 999,
        "reason": "Over-removal",
    })
    assert response.status_code == 400


def test_low_stock_detection(client, db_session, seed_product):
    from app.models.inventory import Inventory

    inv = db_session.query(Inventory).filter(Inventory.product_id == seed_product.product_id).first()
    inv.quantity_available = 5
    db_session.commit()

    response = client.get("/inventory/low-stock")
    assert response.status_code == 200
    data = response.json()
    assert any(item["product_id"] == seed_product.product_id for item in data)
