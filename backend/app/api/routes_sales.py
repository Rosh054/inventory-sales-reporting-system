from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import SaleCreate, SaleResponse
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    try:
        sale = SalesService.create_sale(db, data)
        return SalesService.format_sale(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SaleResponse])
def list_sales(db: Session = Depends(get_db)):
    sales = SalesService.get_all(db)
    return [SalesService.format_sale(s) for s in sales]


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = SalesService.get_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return SalesService.format_sale(sale)
