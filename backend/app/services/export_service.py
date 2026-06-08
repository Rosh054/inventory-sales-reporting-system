import io

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


class ExportService:
    @staticmethod
    def sales_csv(db: Session) -> str:
        rows = db.execute(
            text("""
                SELECT
                    s.sale_id,
                    s.customer_name,
                    s.sale_timestamp,
                    s.payment_method,
                    s.total_amount,
                    si.sale_item_id,
                    p.sku,
                    p.name AS product_name,
                    si.quantity,
                    si.unit_price,
                    si.line_total
                FROM sales s
                JOIN sale_items si ON s.sale_id = si.sale_id
                JOIN products p ON si.product_id = p.product_id
                ORDER BY s.sale_timestamp DESC, s.sale_id
            """)
        ).mappings().all()

        df = pd.DataFrame([dict(row) for row in rows])
        if df.empty:
            df = pd.DataFrame(
                columns=[
                    "sale_id", "customer_name", "sale_timestamp", "payment_method",
                    "total_amount", "sale_item_id", "sku", "product_name",
                    "quantity", "unit_price", "line_total",
                ]
            )
        return df.to_csv(index=False)

    @staticmethod
    def inventory_csv(db: Session) -> str:
        rows = db.execute(
            text("""
                SELECT
                    i.inventory_id,
                    p.sku,
                    p.name AS product_name,
                    p.category,
                    i.quantity_available,
                    p.reorder_level,
                    p.unit_price,
                    p.cost_price,
                    i.last_updated
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                ORDER BY p.name
            """)
        ).mappings().all()

        df = pd.DataFrame([dict(row) for row in rows])
        if df.empty:
            df = pd.DataFrame(
                columns=[
                    "inventory_id", "sku", "product_name", "category",
                    "quantity_available", "reorder_level", "unit_price",
                    "cost_price", "last_updated",
                ]
            )
        return df.to_csv(index=False)

    @staticmethod
    def low_stock_csv(db: Session) -> str:
        rows = db.execute(
            text("""
                SELECT
                    p.product_id,
                    p.sku,
                    p.name AS product_name,
                    p.category,
                    i.quantity_available,
                    p.reorder_level,
                    s.name AS supplier_name
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE i.quantity_available <= p.reorder_level
                  AND p.active = TRUE
                ORDER BY i.quantity_available ASC
            """)
        ).mappings().all()

        df = pd.DataFrame([dict(row) for row in rows])
        if df.empty:
            df = pd.DataFrame(
                columns=[
                    "product_id", "sku", "product_name", "category",
                    "quantity_available", "reorder_level", "supplier_name",
                ]
            )
        return df.to_csv(index=False)
