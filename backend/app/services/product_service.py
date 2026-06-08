from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def create(db: Session, data: ProductCreate) -> Product:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == data.supplier_id).first()
        if not supplier:
            raise ValueError("Supplier does not exist")

        existing = db.query(Product).filter(Product.sku == data.sku).first()
        if existing:
            raise ValueError("SKU must be unique")

        product = Product(**data.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_all(
        db: Session,
        search: str | None = None,
        category: str | None = None,
        active_only: bool = True,
    ) -> list[Product]:
        query = db.query(Product)
        if active_only:
            query = query.filter(Product.active.is_(True))
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
        if category:
            query = query.filter(Product.category == category)
        return query.order_by(Product.name).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.product_id == product_id).first()

    @staticmethod
    def update(db: Session, product_id: int, data: ProductUpdate) -> Product:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError("Product does not exist")

        updates = data.model_dump(exclude_unset=True)
        if "supplier_id" in updates:
            supplier = db.query(Supplier).filter(Supplier.supplier_id == updates["supplier_id"]).first()
            if not supplier:
                raise ValueError("Supplier does not exist")

        for key, value in updates.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def deactivate(db: Session, product_id: int) -> Product:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise ValueError("Product does not exist")
        product.active = False
        db.commit()
        db.refresh(product)
        return product
