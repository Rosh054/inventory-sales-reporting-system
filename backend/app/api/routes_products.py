from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    try:
        return ProductService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProductResponse])
def list_products(
    search: str | None = Query(None),
    category: str | None = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    return ProductService.get_all(db, search=search, category=category, active_only=active_only)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    try:
        return ProductService.update(db, product_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", response_model=ProductResponse)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return ProductService.deactivate(db, product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
