def test_create_product(client, seed_supplier):
    response = client.post("/products", json={
        "sku": "NEW-001",
        "name": "New Gadget",
        "category": "Electronics",
        "unit_price": 49.99,
        "cost_price": 25.00,
        "supplier_id": seed_supplier.supplier_id,
        "reorder_level": 15,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "NEW-001"
    assert data["active"] is True


def test_list_products(client, seed_product):
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["sku"] == "TEST-001"


def test_search_products(client, seed_product):
    response = client.get("/products?search=Widget")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_by_category(client, seed_product):
    response = client.get("/products?category=Electronics")
    assert response.status_code == 200
    assert all(p["category"] == "Electronics" for p in response.json())


def test_update_product(client, seed_product):
    response = client.put(f"/products/{seed_product.product_id}", json={
        "name": "Updated Widget",
        "unit_price": 34.99,
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Widget"


def test_deactivate_product(client, seed_product):
    response = client.delete(f"/products/{seed_product.product_id}")
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_duplicate_sku_rejected(client, seed_supplier, seed_product):
    response = client.post("/products", json={
        "sku": "TEST-001",
        "name": "Duplicate",
        "category": "Electronics",
        "unit_price": 10.00,
        "cost_price": 5.00,
        "supplier_id": seed_supplier.supplier_id,
    })
    assert response.status_code == 400


def test_invalid_price_rejected(client, seed_supplier):
    response = client.post("/products", json={
        "sku": "BAD-001",
        "name": "Bad Price",
        "category": "Electronics",
        "unit_price": -5.00,
        "cost_price": 5.00,
        "supplier_id": seed_supplier.supplier_id,
    })
    assert response.status_code == 422
