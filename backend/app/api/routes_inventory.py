from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import InventoryResponse, StockMovementCreate, StockMovementResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


class StockInRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    reason: str = Field(default="Stock replenishment", max_length=255)


class StockOutRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    reason: str = Field(default="Stock removal", max_length=255)


class AdjustRequest(BaseModel):
    new_quantity: int = Field(..., ge=0)
    reason: str = Field(default="Inventory adjustment", max_length=255)


@router.get("", response_model=list[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)):
    return InventoryService.get_all(db)


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)):
    return InventoryService.get_low_stock(db)


@router.get("/movements", response_model=list[StockMovementResponse])
def list_movements(
    product_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return InventoryService.get_movements(db, product_id=product_id)


@router.post("/{product_id}/stock-in", response_model=InventoryResponse)
def add_stock(product_id: int, data: StockInRequest, db: Session = Depends(get_db)):
    try:
        inv = InventoryService.add_stock(db, product_id, data.quantity, data.reason)
        product_info = InventoryService.get_all(db)
        info = next((i for i in product_info if i["product_id"] == product_id), {})
        return {**info, "inventory_id": inv.inventory_id, "quantity_available": inv.quantity_available, "last_updated": inv.last_updated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{product_id}/stock-out", response_model=InventoryResponse)
def remove_stock(product_id: int, data: StockOutRequest, db: Session = Depends(get_db)):
    try:
        inv = InventoryService.remove_stock(db, product_id, data.quantity, data.reason)
        product_info = InventoryService.get_all(db)
        info = next((i for i in product_info if i["product_id"] == product_id), {})
        return {**info, "inventory_id": inv.inventory_id, "quantity_available": inv.quantity_available, "last_updated": inv.last_updated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{product_id}/adjust", response_model=InventoryResponse)
def adjust_stock(product_id: int, data: AdjustRequest, db: Session = Depends(get_db)):
    try:
        inv = InventoryService.adjust_stock(db, product_id, data.new_quantity, data.reason)
        product_info = InventoryService.get_all(db)
        info = next((i for i in product_info if i["product_id"] == product_id), {})
        return {**info, "inventory_id": inv.inventory_id, "quantity_available": inv.quantity_available, "last_updated": inv.last_updated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movements", response_model=StockMovementResponse, status_code=201)
def create_movement(data: StockMovementCreate, db: Session = Depends(get_db)):
    try:
        return InventoryService.record_movement(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
