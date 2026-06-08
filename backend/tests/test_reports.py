def test_sales_summary_structure(client, seed_product):
    client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 2}],
    })
    response = client.get("/reports/sales-summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_sales" in data
    assert "total_revenue" in data
    assert "average_order_value" in data
    assert data["total_sales"] >= 1


def test_revenue_by_category(client, seed_product):
    client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 1}],
    })
    response = client.get("/reports/revenue-by-category")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "category" in data[0]
        assert "revenue" in data[0]


def test_top_products(client, seed_product):
    response = client.get("/reports/top-products?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_low_stock_report(client):
    response = client.get("/reports/low-stock")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_profit_summary(client, seed_product):
    client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 1}],
    })
    response = client.get("/reports/profit-summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "total_profit" in data
    assert "profit_margin_pct" in data


def test_monthly_sales(client):
    response = client.get("/reports/monthly-sales")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_inventory_valuation(client, seed_product):
    response = client.get("/reports/inventory-valuation")
    assert response.status_code == 200
    data = response.json()
    assert "total_units" in data
    assert "total_cost_value" in data
    assert "total_retail_value" in data


def test_supplier_performance(client, seed_supplier):
    response = client.get("/reports/supplier-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_csv_export_sales(client, seed_product):
    client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": seed_product.product_id, "quantity": 1}],
    })
    response = client.get("/exports/sales.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "sale_id" in response.text


def test_csv_export_inventory(client, seed_product):
    response = client.get("/exports/inventory.csv")
    assert response.status_code == 200
    assert "sku" in response.text


def test_csv_export_low_stock(client):
    response = client.get("/exports/low-stock.csv")
    assert response.status_code == 200
    assert "product_id" in response.text
