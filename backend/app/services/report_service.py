from decimal import Decimal

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.schemas.report import (
    InventoryValuationReport,
    LowStockItem,
    MonthlySalesItem,
    ProfitSummaryReport,
    RevenueByCategoryItem,
    SalesSummaryReport,
    SupplierPerformanceItem,
    TopProductItem,
)


class ReportService:
    @staticmethod
    def sales_summary(db: Session) -> SalesSummaryReport:
        result = db.execute(
            text("""
                SELECT
                    COUNT(*) AS total_sales,
                    COALESCE(SUM(total_amount), 0) AS total_revenue,
                    COALESCE(AVG(total_amount), 0) AS average_order_value
                FROM sales
            """)
        ).mappings().first()

        return SalesSummaryReport(
            total_sales=result["total_sales"],
            total_revenue=Decimal(str(result["total_revenue"])),
            average_order_value=Decimal(str(result["average_order_value"])).quantize(Decimal("0.01")),
        )

    @staticmethod
    def revenue_by_category(db: Session) -> list[RevenueByCategoryItem]:
        rows = db.execute(
            text("""
                SELECT
                    p.category,
                    COALESCE(SUM(si.line_total), 0) AS revenue,
                    COALESCE(SUM(si.quantity), 0) AS units_sold
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                GROUP BY p.category
                ORDER BY revenue DESC
            """)
        ).mappings().all()

        return [
            RevenueByCategoryItem(
                category=row["category"],
                revenue=Decimal(str(row["revenue"])),
                units_sold=row["units_sold"],
            )
            for row in rows
        ]

    @staticmethod
    def top_products(db: Session, limit: int = 10) -> list[TopProductItem]:
        rows = db.execute(
            text("""
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
                LIMIT :limit
            """),
            {"limit": limit},
        ).mappings().all()

        return [
            TopProductItem(
                product_id=row["product_id"],
                product_name=row["product_name"],
                sku=row["sku"],
                units_sold=row["units_sold"],
                revenue=Decimal(str(row["revenue"])),
            )
            for row in rows
        ]

    @staticmethod
    def low_stock(db: Session) -> list[LowStockItem]:
        rows = db.execute(
            text("""
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
                ORDER BY i.quantity_available ASC
            """)
        ).mappings().all()

        return [LowStockItem(**row) for row in rows]

    @staticmethod
    def profit_summary(db: Session) -> ProfitSummaryReport:
        result = db.execute(
            text("""
                SELECT
                    COALESCE(SUM(si.line_total), 0) AS total_revenue,
                    COALESCE(SUM(si.quantity * p.cost_price), 0) AS total_cost
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
            """)
        ).mappings().first()

        revenue = Decimal(str(result["total_revenue"]))
        cost = Decimal(str(result["total_cost"]))
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue > 0 else Decimal("0")

        return ProfitSummaryReport(
            total_revenue=revenue,
            total_cost=cost,
            total_profit=profit,
            profit_margin_pct=margin.quantize(Decimal("0.01")),
        )

    @staticmethod
    def monthly_sales(db: Session) -> list[MonthlySalesItem]:
        from app.models.sale import Sale

        dialect = db.bind.dialect.name
        if dialect == "postgresql":
            month_expr = func.to_char(Sale.sale_timestamp, "YYYY-MM")
        else:
            month_expr = func.strftime("%Y-%m", Sale.sale_timestamp)

        rows = (
            db.query(
                month_expr.label("month"),
                func.count().label("sales_count"),
                func.coalesce(func.sum(Sale.total_amount), 0).label("revenue"),
            )
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )

        return [
            MonthlySalesItem(
                month=row.month,
                sales_count=row.sales_count,
                revenue=Decimal(str(row.revenue)),
            )
            for row in rows
        ]

    @staticmethod
    def inventory_valuation(db: Session) -> InventoryValuationReport:
        result = db.execute(
            text("""
                SELECT
                    COALESCE(SUM(i.quantity_available), 0) AS total_units,
                    COALESCE(SUM(i.quantity_available * p.cost_price), 0) AS total_cost_value,
                    COALESCE(SUM(i.quantity_available * p.unit_price), 0) AS total_retail_value
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                WHERE p.active = TRUE
            """)
        ).mappings().first()

        return InventoryValuationReport(
            total_units=result["total_units"],
            total_cost_value=Decimal(str(result["total_cost_value"])),
            total_retail_value=Decimal(str(result["total_retail_value"])),
        )

    @staticmethod
    def supplier_performance(db: Session) -> list[SupplierPerformanceItem]:
        rows = db.execute(
            text("""
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
                ORDER BY revenue DESC
            """)
        ).mappings().all()

        return [
            SupplierPerformanceItem(
                supplier_id=row["supplier_id"],
                supplier_name=row["supplier_name"],
                product_count=row["product_count"],
                units_sold=row["units_sold"],
                revenue=Decimal(str(row["revenue"])),
            )
            for row in rows
        ]
