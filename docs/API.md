# API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |

## Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products` | Create product |
| GET | `/products` | List products (`?search=`, `?category=`) |
| GET | `/products/{id}` | Get product by ID |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Deactivate product |

## Suppliers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/suppliers` | Create supplier |
| GET | `/suppliers` | List suppliers |
| GET | `/suppliers/{id}` | Get supplier by ID |

## Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List all inventory |
| GET | `/inventory/low-stock` | Low-stock products |
| GET | `/inventory/movements` | Stock movement history |
| POST | `/inventory/{id}/stock-in` | Add stock |
| POST | `/inventory/{id}/stock-out` | Remove stock |
| POST | `/inventory/{id}/adjust` | Set exact quantity |
| POST | `/inventory/movements` | Record custom movement |

## Sales

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sales` | Create sale (auto-reduces inventory) |
| GET | `/sales` | List sales history |
| GET | `/sales/{id}` | Get sale by ID |

## Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/sales-summary` | Total sales, revenue, AOV |
| GET | `/reports/revenue-by-category` | Revenue grouped by category |
| GET | `/reports/top-products` | Best sellers by revenue |
| GET | `/reports/low-stock` | Products at/below reorder level |
| GET | `/reports/profit-summary` | Revenue, cost, profit, margin |
| GET | `/reports/monthly-sales` | Monthly sales trend |
| GET | `/reports/inventory-valuation` | Total inventory value |
| GET | `/reports/supplier-performance` | Supplier sales metrics |

## Exports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exports/sales.csv` | Download sales CSV |
| GET | `/exports/inventory.csv` | Download inventory CSV |
| GET | `/exports/low-stock.csv` | Download low-stock CSV |

## Example Requests

### Create a product

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU-NEW01",
    "name": "Wireless Mouse",
    "category": "Electronics",
    "unit_price": 29.99,
    "cost_price": 12.50,
    "supplier_id": 1,
    "reorder_level": 15
  }'
```

### Create a sale

```bash
curl -X POST http://localhost:8000/sales \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jane Doe",
    "payment_method": "CREDIT_CARD",
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 5, "quantity": 1}
    ]
  }'
```

### Get sales summary report

```bash
curl http://localhost:8000/reports/sales-summary
```

### Export sales CSV

```bash
curl -o sales.csv http://localhost:8000/exports/sales.csv
```
