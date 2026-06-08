from decimal import Decimal

from pydantic import BaseModel


class SalesSummaryReport(BaseModel):
    total_sales: int
    total_revenue: Decimal
    average_order_value: Decimal


class RevenueByCategoryItem(BaseModel):
    category: str
    revenue: Decimal
    units_sold: int


class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    units_sold: int
    revenue: Decimal


class LowStockItem(BaseModel):
    product_id: int
    sku: str
    product_name: str
    quantity_available: int
    reorder_level: int


class ProfitSummaryReport(BaseModel):
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    profit_margin_pct: Decimal


class MonthlySalesItem(BaseModel):
    month: str
    sales_count: int
    revenue: Decimal


class InventoryValuationReport(BaseModel):
    total_units: int
    total_cost_value: Decimal
    total_retail_value: Decimal


class SupplierPerformanceItem(BaseModel):
    supplier_id: int
    supplier_name: str
    product_count: int
    units_sold: int
    revenue: Decimal
