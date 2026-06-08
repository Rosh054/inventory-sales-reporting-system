def test_create_sale_reduces_inventory(client, seed_product):
    response = client.post("/sales", json={
        "customer_name": "Test Customer",
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 3}],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == "89.97"
    assert len(data["items"]) == 1

    inv_response = client.get("/inventory")
    inv = next(i for i in inv_response.json() if i["product_id"] == seed_product.product_id)
    assert inv["quantity_available"] == 47


def test_sale_blocked_insufficient_stock(client, seed_product):
    response = client.post("/sales", json={
        "customer_name": "Greedy Customer",
        "payment_method": "CREDIT_CARD",
        "items": [{"product_id": seed_product.product_id, "quantity": 999}],
    })
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_list_sales(client, seed_product):
    client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 1}],
    })
    response = client.get("/sales")
    assert response.status_code == 200
    assert len(response.json()) >= 1
