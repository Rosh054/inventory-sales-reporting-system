from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/sales.csv", response_class=PlainTextResponse)
def export_sales(db: Session = Depends(get_db)):
    csv_content = ExportService.sales_csv(db)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales.csv"},
    )


@router.get("/inventory.csv", response_class=PlainTextResponse)
def export_inventory(db: Session = Depends(get_db)):
    csv_content = ExportService.inventory_csv(db)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory.csv"},
    )


@router.get("/low-stock.csv", response_class=PlainTextResponse)
def export_low_stock(db: Session = Depends(get_db)):
    csv_content = ExportService.low_stock_csv(db)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=low-stock.csv"},
    )
