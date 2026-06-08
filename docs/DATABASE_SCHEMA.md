# Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    SUPPLIERS ||--o{ PRODUCTS : supplies
    PRODUCTS ||--o| INVENTORY : has
    PRODUCTS ||--o{ STOCK_MOVEMENTS : tracks
    PRODUCTS ||--o{ SALE_ITEMS : sold_in
    SALES ||--|{ SALE_ITEMS : contains

    SUPPLIERS {
        int supplier_id PK
        string name
        string email
        string phone
        string region
        datetime created_at
    }

    PRODUCTS {
        int product_id PK
        string sku UK
        string name
        string category
        decimal unit_price
        decimal cost_price
        int supplier_id FK
        int reorder_level
        boolean active
        datetime created_at
    }

    INVENTORY {
        int inventory_id PK
        int product_id FK UK
        int quantity_available
        datetime last_updated
    }

    STOCK_MOVEMENTS {
        int movement_id PK
        int product_id FK
        string movement_type
        int quantity
        string reason
        datetime created_at
    }

    SALES {
        int sale_id PK
        string customer_name
        datetime sale_timestamp
        string payment_method
        decimal total_amount
    }

    SALE_ITEMS {
        int sale_item_id PK
        int sale_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal line_total
    }
```

## Table Descriptions

### suppliers
Stores vendor information. Each supplier can provide multiple products.

### products
Core product catalog with SKU, pricing, category, and supplier link. The `active` flag supports soft deactivation.

### inventory
One-to-one with products. Tracks current `quantity_available` and `last_updated` timestamp.

### stock_movements
Audit log of all inventory changes. Movement types: `STOCK_IN`, `SALE`, `ADJUSTMENT`, `RETURN`.

### sales
Sale transaction header with customer, timestamp, payment method, and computed total.

### sale_items
Line items within a sale. Stores quantity, unit price at time of sale, and line total.

## Relationships

| Parent | Child | Type | On Delete |
|--------|-------|------|-----------|
| suppliers | products | 1:N | RESTRICT |
| products | inventory | 1:1 | CASCADE |
| products | stock_movements | 1:N | RESTRICT |
| sales | sale_items | 1:N | CASCADE |
| products | sale_items | 1:N | RESTRICT |

## Indexing Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| products | `sku` (unique) | Fast SKU lookup, uniqueness enforcement |
| products | `category` | Category filter queries |
| stock_movements | `product_id` | Movement history per product |
| stock_movements | `created_at` | Time-range queries |
| sales | `sale_timestamp` | Date-range reporting |
| sale_items | `sale_id`, `product_id` | Join performance for reports |

## Constraints

- `products.sku` — UNIQUE, not null
- `products.unit_price` — must be > 0 (enforced at API layer)
- `products.cost_price` — must be >= 0 (enforced at API layer)
- `inventory.quantity_available` — must be >= 0 (enforced at service layer)
- `inventory.product_id` — UNIQUE (one inventory record per product)
- Sales blocked when `quantity_available < requested quantity`
