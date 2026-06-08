from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.stock_movement import MovementType, StockMovement
from app.schemas.product import SaleCreate


class SalesService:
    @staticmethod
    def create_sale(db: Session, data: SaleCreate) -> Sale:
        total_amount = Decimal("0.00")
        line_items: list[tuple[Product, int, Decimal]] = []

        for item in data.items:
            product = db.query(Product).filter(Product.product_id == item.product_id).first()
            if not product:
                raise ValueError(f"Product {item.product_id} does not exist")
            if not product.active:
                raise ValueError(f"Product {product.name} is inactive")

            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            available = inv.quantity_available if inv else 0
            if available < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}: requested {item.quantity}, available {available}"
                )

            line_total = product.unit_price * item.quantity
            total_amount += line_total
            line_items.append((product, item.quantity, line_total))

        sale = Sale(
            customer_name=data.customer_name,
            payment_method=data.payment_method,
            total_amount=total_amount,
            sale_timestamp=datetime.utcnow(),
        )
        db.add(sale)
        db.flush()

        for product, quantity, line_total in line_items:
            sale_item = SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=product.unit_price,
                line_total=line_total,
            )
            db.add(sale_item)

            inv = db.query(Inventory).filter(Inventory.product_id == product.product_id).first()
            if not inv:
                inv = Inventory(product_id=product.product_id, quantity_available=0)
                db.add(inv)
                db.flush()

            inv.quantity_available -= quantity
            inv.last_updated = datetime.utcnow()

            movement = StockMovement(
                product_id=product.product_id,
                movement_type=MovementType.SALE.value,
                quantity=quantity,
                reason=f"Sale #{sale.sale_id}",
            )
            db.add(movement)

        db.commit()
        db.refresh(sale)
        return sale

    @staticmethod
    def get_all(db: Session, limit: int = 100) -> list[Sale]:
        return (
            db.query(Sale)
            .options(joinedload(Sale.items).joinedload(SaleItem.product))
            .order_by(Sale.sale_timestamp.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, sale_id: int) -> Sale | None:
        return (
            db.query(Sale)
            .options(joinedload(Sale.items).joinedload(SaleItem.product))
            .filter(Sale.sale_id == sale_id)
            .first()
        )

    @staticmethod
    def format_sale(sale: Sale) -> dict:
        items = []
        for item in sale.items:
            items.append(
                {
                    "sale_item_id": item.sale_item_id,
                    "sale_id": item.sale_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                    "product_name": item.product.name if item.product else None,
                }
            )
        return {
            "sale_id": sale.sale_id,
            "customer_name": sale.customer_name,
            "sale_timestamp": sale.sale_timestamp,
            "payment_method": sale.payment_method,
            "total_amount": sale.total_amount,
            "items": items,
        }
