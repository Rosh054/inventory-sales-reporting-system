# SQL Reports

Each report endpoint answers a specific business question using SQL aggregation.

---

## Sales Summary — `GET /reports/sales-summary`

**Business question:** How many sales have we made and what is our total revenue?

```sql
SELECT
    COUNT(*) AS total_sales,
    COALESCE(SUM(total_amount), 0) AS total_revenue,
    COALESCE(AVG(total_amount), 0) AS average_order_value
FROM sales;
```

---

## Revenue by Category — `GET /reports/revenue-by-category`

**Business question:** Which product categories generate the most revenue?

```sql
SELECT
    p.category,
    COALESCE(SUM(si.line_total), 0) AS revenue,
    COALESCE(SUM(si.quantity), 0) AS units_sold
FROM sale_items si
JOIN products p ON si.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

---

## Top Products — `GET /reports/top-products`

**Business question:** What are our best-selling products by revenue?

```sql
SELECT
    p.product_id,
    p.name AS product_name,
    p.sku,
    COALESCE(SUM(si.quantity), 0) AS units_sold,
    COALESCE(SUM(si.line_total), 0) AS revenue
FROM products p
LEFT JOIN sale_items si ON p.product_id = si.product_id
GROUP BY p.product_id, p.name, p.sku
ORDER BY revenue DESC
LIMIT 10;
```

---

## Low Stock — `GET /reports/low-stock`

**Business question:** Which products need to be reordered?

```sql
SELECT
    p.product_id,
    p.sku,
    p.name AS product_name,
    i.quantity_available,
    p.reorder_level
FROM inventory i
JOIN products p ON i.product_id = p.product_id
WHERE i.quantity_available <= p.reorder_level
  AND p.active = TRUE
ORDER BY i.quantity_available ASC;
```

---

## Profit Summary — `GET /reports/profit-summary`

**Business question:** What is our overall profitability?

```sql
SELECT
    COALESCE(SUM(si.line_total), 0) AS total_revenue,
    COALESCE(SUM(si.quantity * p.cost_price), 0) AS total_cost
FROM sale_items si
JOIN products p ON si.product_id = p.product_id;
-- total_profit = total_revenue - total_cost
-- profit_margin_pct = (total_profit / total_revenue) * 100
```

---

## Monthly Sales — `GET /reports/monthly-sales`

**Business question:** How are sales trending month over month?

```sql
SELECT
    TO_CHAR(sale_timestamp, 'YYYY-MM') AS month,
    COUNT(*) AS sales_count,
    COALESCE(SUM(total_amount), 0) AS revenue
FROM sales
GROUP BY TO_CHAR(sale_timestamp, 'YYYY-MM')
ORDER BY month ASC;
```

---

## Inventory Valuation — `GET /reports/inventory-valuation`

**Business question:** What is the total value of inventory on hand?

```sql
SELECT
    COALESCE(SUM(i.quantity_available), 0) AS total_units,
    COALESCE(SUM(i.quantity_available * p.cost_price), 0) AS total_cost_value,
    COALESCE(SUM(i.quantity_available * p.unit_price), 0) AS total_retail_value
FROM inventory i
JOIN products p ON i.product_id = p.product_id
WHERE p.active = TRUE;
```

---

## Supplier Performance — `GET /reports/supplier-performance`

**Business question:** Which suppliers' products sell the most?

```sql
SELECT
    s.supplier_id,
    s.name AS supplier_name,
    COUNT(DISTINCT p.product_id) AS product_count,
    COALESCE(SUM(si.quantity), 0) AS units_sold,
    COALESCE(SUM(si.line_total), 0) AS revenue
FROM suppliers s
LEFT JOIN products p ON s.supplier_id = p.supplier_id
LEFT JOIN sale_items si ON p.product_id = si.product_id
GROUP BY s.supplier_id, s.name
ORDER BY revenue DESC;
```
