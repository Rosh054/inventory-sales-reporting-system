# Architecture

## System Overview

```mermaid
graph TB
    subgraph Client
        FE[React Dashboard<br/>Vite + Recharts]
    end

    subgraph Backend
        API[FastAPI Application]
        SVC[Service Layer]
        API --> SVC
    end

    subgraph Data
        PG[(PostgreSQL 16)]
        SVC --> PG
    end

    FE -->|REST JSON| API
    FE -->|CSV Download| API
```

## Backend Layers

| Layer | Responsibility |
|-------|---------------|
| **API Routes** | HTTP endpoints, request validation, error responses |
| **Services** | Business logic, transactions, stock enforcement |
| **Models** | SQLAlchemy ORM table definitions |
| **Schemas** | Pydantic request/response validation |

## Backend Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant R as API Route
    participant S as Service
    participant D as Database

    C->>R: HTTP Request
    R->>R: Validate (Pydantic)
    R->>S: Call service method
    S->>D: SQL query / transaction
    D-->>S: Result
    S-->>R: Domain object
    R-->>C: JSON response
```

## Inventory Update Transaction Flow

```mermaid
sequenceDiagram
    participant API as Sales API
    participant SS as SalesService
    participant DB as PostgreSQL

    API->>SS: create_sale(items)
    SS->>DB: BEGIN transaction
    loop For each item
        SS->>DB: Check product exists & active
        SS->>DB: Lock inventory row
        SS->>DB: Verify quantity_available >= requested
    end
    alt Insufficient stock
        SS->>DB: ROLLBACK
        SS-->>API: ValueError
    else Stock OK
        SS->>DB: INSERT sale + sale_items
        SS->>DB: UPDATE inventory (decrement)
        SS->>DB: INSERT stock_movement (SALE)
        SS->>DB: COMMIT
        SS-->>API: Sale record
    end
```

## Sales Reporting Flow

```mermaid
sequenceDiagram
    participant FE as Dashboard
    participant API as Reports API
    participant RS as ReportService
    participant DB as PostgreSQL

    FE->>API: GET /reports/sales-summary
    API->>RS: sales_summary(db)
    RS->>DB: SQL aggregation query
    DB-->>RS: Aggregated rows
    RS-->>API: Pydantic report model
    API-->>FE: JSON
    FE->>FE: Render chart/table
```

## Key Design Decisions

1. **Transactional sales** — All sale creation happens in a single database transaction. Stock is checked and decremented atomically to prevent overselling.

2. **Stock movement audit trail** — Every inventory change (stock-in, sale, adjustment, return) creates a `stock_movements` record for traceability.

3. **SQL-backed reports** — Analytics endpoints use raw SQL aggregation queries against PostgreSQL, demonstrating SQL developer skills.

4. **Deterministic seed data** — Fixed random seed (42) ensures reproducible demo data across environments.

5. **Zero-cost stack** — All components run locally via Docker Compose with open-source tools only.
