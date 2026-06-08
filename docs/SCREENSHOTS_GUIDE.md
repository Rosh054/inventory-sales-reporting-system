# Screenshots Guide

Capture these screenshots for your portfolio README and resume.

## 1. Dashboard (`http://localhost:5173/`)

Shows:
- Total revenue, average order value, low-stock count, inventory valuation stat cards
- Revenue by category pie chart
- Top 5 products bar chart
- Recent sales table

**Tip:** Run `make seed` first so charts have data.

## 2. Products Page (`http://localhost:5173/products`)

Shows:
- Product table with SKU, name, category, pricing
- Search and category filter
- "Add Product" modal

## 3. Inventory Page (`http://localhost:5173/inventory`)

Shows:
- Stock levels with OK/Low status badges
- Stock-in and adjust action buttons

## 4. Sales Creation (`http://localhost:5173/sales`)

Shows:
- Sales history table
- "New Sale" modal with line items and payment method

## 5. Reports Page (`http://localhost:5173/reports`)

Shows:
- Profit summary stat cards
- Monthly sales trend bar chart
- Supplier performance table
- Low-stock alert table
- CSV export buttons

## 6. CSV Export Response

Open `http://localhost:8000/exports/sales.csv` in browser or terminal:

```bash
curl http://localhost:8000/exports/sales.csv | head -5
```

Screenshot the CSV output in terminal.

## 7. Swagger API Docs (`http://localhost:8000/docs`)

Shows:
- Full interactive API documentation
- All endpoint groups (products, inventory, sales, reports, exports)

## 8. Test Results

```bash
make test
```

Screenshot the pytest output showing all tests passing.

## 9. Docker Containers

```bash
docker compose ps
```

Screenshot showing postgres, backend, and frontend containers running and healthy.
