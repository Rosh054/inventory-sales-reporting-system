from datetime import datetime

from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.stock_movement import MovementType, StockMovement
from app.schemas.product import StockMovementCreate


class InventoryService:
    @staticmethod
    def get_all(db: Session) -> list[dict]:
        rows = (
            db.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.product_id)
            .order_by(Product.name)
            .all()
        )
        result = []
        for inv, product in rows:
            result.append(
                {
                    "inventory_id": inv.inventory_id,
                    "product_id": inv.product_id,
                    "quantity_available": inv.quantity_available,
                    "last_updated": inv.last_updated,
                    "product_name": product.name,
                    "sku": product.sku,
                    "reorder_level": product.reorder_level,
                }
            )
        return result

    @staticmethod
    def get_by_product(db: Session, product_id: int) -> Inventory | None:
        return db.query(Inventory).filter(Inventory.product_id == product_id).first()

    @staticmethod
    def _ensure_inventory(db: Session, product_id: int) -> Inventory:
        inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inv:
            inv = Inventory(product_id=product_id, quantity_available=0)
            db.add(inv)
            db.flush()
        return inv

    @staticmethod
    def add_stock(db: Session, product_id: int, quantity: int, reason: str) -> Inventory:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError("Product does not exist")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        inv = InventoryService._ensure_inventory(db, product_id)
        inv.quantity_available += quantity
        inv.last_updated = datetime.utcnow()

        movement = StockMovement(
            product_id=product_id,
            movement_type=MovementType.STOCK_IN.value,
            quantity=quantity,
            reason=reason,
        )
        db.add(movement)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def remove_stock(db: Session, product_id: int, quantity: int, reason: str) -> Inventory:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError("Product does not exist")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        inv = InventoryService._ensure_inventory(db, product_id)
        if inv.quantity_available < quantity:
            raise ValueError("Insufficient stock available")

        inv.quantity_available -= quantity
        inv.last_updated = datetime.utcnow()

        movement = StockMovement(
            product_id=product_id,
            movement_type=MovementType.ADJUSTMENT.value,
            quantity=quantity,
            reason=reason,
        )
        db.add(movement)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def adjust_stock(db: Session, product_id: int, new_quantity: int, reason: str) -> Inventory:
        if new_quantity < 0:
            raise ValueError("Quantity must be >= 0")

        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError("Product does not exist")

        inv = InventoryService._ensure_inventory(db, product_id)
        diff = new_quantity - inv.quantity_available
        inv.quantity_available = new_quantity
        inv.last_updated = datetime.utcnow()

        if diff != 0:
            movement = StockMovement(
                product_id=product_id,
                movement_type=MovementType.ADJUSTMENT.value,
                quantity=abs(diff),
                reason=reason,
            )
            db.add(movement)

        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def record_movement(db: Session, data: StockMovementCreate) -> StockMovement:
        product = db.query(Product).filter(Product.product_id == data.product_id).first()
        if not product:
            raise ValueError("Product does not exist")

        inv = InventoryService._ensure_inventory(db, data.product_id)

        if data.movement_type in (MovementType.SALE.value, MovementType.ADJUSTMENT.value):
            if inv.quantity_available < data.quantity:
                raise ValueError("Insufficient stock available")
            inv.quantity_available -= data.quantity
        else:
            inv.quantity_available += data.quantity

        inv.last_updated = datetime.utcnow()
        movement = StockMovement(**data.model_dump())
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    @staticmethod
    def get_movements(db: Session, product_id: int | None = None) -> list[StockMovement]:
        query = db.query(StockMovement)
        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        return query.order_by(StockMovement.created_at.desc()).all()

    @staticmethod
    def get_low_stock(db: Session) -> list[dict]:
        rows = (
            db.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.product_id)
            .filter(Inventory.quantity_available <= Product.reorder_level)
            .filter(Product.active.is_(True))
            .order_by(Inventory.quantity_available)
            .all()
        )
        return [
            {
                "product_id": product.product_id,
                "sku": product.sku,
                "product_name": product.name,
                "quantity_available": inv.quantity_available,
                "reorder_level": product.reorder_level,
            }
            for inv, product in rows
        ]
