from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
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
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales-summary", response_model=SalesSummaryReport)
def sales_summary(db: Session = Depends(get_db)):
    return ReportService.sales_summary(db)


@router.get("/revenue-by-category", response_model=list[RevenueByCategoryItem])
def revenue_by_category(db: Session = Depends(get_db)):
    return ReportService.revenue_by_category(db)


@router.get("/top-products", response_model=list[TopProductItem])
def top_products(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return ReportService.top_products(db, limit=limit)


@router.get("/low-stock", response_model=list[LowStockItem])
def low_stock_report(db: Session = Depends(get_db)):
    return ReportService.low_stock(db)


@router.get("/profit-summary", response_model=ProfitSummaryReport)
def profit_summary(db: Session = Depends(get_db)):
    return ReportService.profit_summary(db)


@router.get("/monthly-sales", response_model=list[MonthlySalesItem])
def monthly_sales(db: Session = Depends(get_db)):
    return ReportService.monthly_sales(db)


@router.get("/inventory-valuation", response_model=InventoryValuationReport)
def inventory_valuation(db: Session = Depends(get_db)):
    return ReportService.inventory_valuation(db)


@router.get("/supplier-performance", response_model=list[SupplierPerformanceItem])
def supplier_performance(db: Session = Depends(get_db)):
    return ReportService.supplier_performance(db)
