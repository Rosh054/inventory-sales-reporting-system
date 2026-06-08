from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    unit_price: Decimal = Field(..., gt=0)
    cost_price: Decimal = Field(..., ge=0)
    supplier_id: int
    reorder_level: int = Field(default=10, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    category: str | None = Field(None, min_length=1, max_length=100)
    unit_price: Decimal | None = Field(None, gt=0)
    cost_price: Decimal | None = Field(None, ge=0)
    supplier_id: int | None = None
    reorder_level: int | None = Field(None, ge=0)
    active: bool | None = None


class ProductResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    category: str
    unit_price: Decimal
    cost_price: Decimal
    supplier_id: int
    reorder_level: int
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=100)


class SupplierResponse(BaseModel):
    supplier_id: int
    name: str
    email: str
    phone: str
    region: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    inventory_id: int
    product_id: int
    quantity_available: int
    last_updated: datetime
    product_name: str | None = None
    sku: str | None = None
    reorder_level: int | None = None

    model_config = {"from_attributes": True}


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: str
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=255)

    @field_validator("movement_type")
    @classmethod
    def validate_movement_type(cls, v: str) -> str:
        allowed = {"STOCK_IN", "SALE", "ADJUSTMENT", "RETURN"}
        if v not in allowed:
            raise ValueError(f"movement_type must be one of {allowed}")
        return v


class StockMovementResponse(BaseModel):
    movement_id: int
    product_id: int
    movement_type: str
    quantity: int
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class SaleCreate(BaseModel):
    customer_name: str | None = None
    payment_method: str = Field(..., min_length=1, max_length=50)
    items: list[SaleItemCreate] = Field(..., min_length=1)


class SaleItemResponse(BaseModel):
    sale_item_id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product_name: str | None = None

    model_config = {"from_attributes": True}


class SaleResponse(BaseModel):
    sale_id: int
    customer_name: str | None
    sale_timestamp: datetime
    payment_method: str
    total_amount: Decimal
    items: list[SaleItemResponse] = []

    model_config = {"from_attributes": True}
