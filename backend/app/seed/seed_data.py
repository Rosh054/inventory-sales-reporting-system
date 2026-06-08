"""
Deterministic seed data generator.
Uses fixed random seed for reproducible results.
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import SessionLocal, init_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.stock_movement import MovementType, StockMovement
from app.models.supplier import Supplier

RNG = random.Random(42)

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", "Food", "Health"]
REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["CASH", "CREDIT_CARD", "DEBIT_CARD", "ONLINE"]
CUSTOMER_NAMES = [
    "Alice Johnson", "Bob Smith", "Carol White", "David Brown", "Eva Davis",
    "Frank Miller", "Grace Wilson", "Henry Moore", "Ivy Taylor", "Jack Anderson",
    None, None, None,
]

SUPPLIER_DATA = [
    ("Acme Supplies", "acme@supplies.com", "555-0101", "North"),
    ("Global Trade Co", "global@trade.com", "555-0102", "South"),
    ("Prime Distributors", "prime@dist.com", "555-0103", "East"),
    ("Metro Wholesale", "metro@whole.com", "555-0104", "West"),
    ("Pacific Goods", "pacific@goods.com", "555-0105", "Central"),
    ("Summit Trading", "summit@trade.com", "555-0106", "North"),
    ("Valley Imports", "valley@import.com", "555-0107", "South"),
    ("Coastal Merchants", "coastal@merch.com", "555-0108", "East"),
    ("Highland Supply", "highland@supply.com", "555-0109", "West"),
    ("Urban Logistics", "urban@logistics.com", "555-0110", "Central"),
]


def clear_data(db):
    db.query(StockMovement).delete()
    db.query(SaleItem).delete()
    db.query(Sale).delete()
    db.query(Inventory).delete()
    db.query(Product).delete()
    db.query(Supplier).delete()
    db.commit()


def seed_suppliers(db) -> list[Supplier]:
    suppliers = []
    for name, email, phone, region in SUPPLIER_DATA:
        s = Supplier(name=name, email=email, phone=phone, region=region)
        db.add(s)
        suppliers.append(s)
    db.commit()
    for s in suppliers:
        db.refresh(s)
    return suppliers


def seed_products(db, suppliers: list[Supplier]) -> list[Product]:
    products = []
    for i in range(1, 101):
        category = CATEGORIES[i % len(CATEGORIES)]
        supplier = suppliers[i % len(suppliers)]
        cost = Decimal(str(RNG.randint(5, 200)))
        markup = Decimal(str(RNG.uniform(1.2, 2.5))).quantize(Decimal("0.01"))
        unit_price = (cost * markup).quantize(Decimal("0.01"))

        product = Product(
            sku=f"SKU-{i:04d}",
            name=f"{category} Product {i}",
            category=category,
            unit_price=unit_price,
            cost_price=cost,
            supplier_id=supplier.supplier_id,
            reorder_level=RNG.randint(5, 25),
            active=True,
            created_at=datetime(2024, 1, 1) + timedelta(days=i),
        )
        db.add(product)
        products.append(product)

    db.commit()
    for p in products:
        db.refresh(p)
    return products


def seed_inventory(db, products: list[Product]) -> list[Inventory]:
    inventories = []
    for product in products:
        qty = RNG.randint(0, 150)
        inv = Inventory(
            product_id=product.product_id,
            quantity_available=qty,
            last_updated=datetime.utcnow(),
        )
        db.add(inv)
        inventories.append(inv)

        if qty > 0:
            movement = StockMovement(
                product_id=product.product_id,
                movement_type=MovementType.STOCK_IN.value,
                quantity=qty,
                reason="Initial stock",
                created_at=product.created_at,
            )
            db.add(movement)

    db.commit()
    return inventories


def seed_sales(db, products: list[Product], count: int = 500):
    base_date = datetime(2024, 6, 1)
    stock_map = {
        inv.product_id: inv.quantity_available
        for inv in db.query(Inventory).all()
    }
    products_with_stock = [p for p in products if stock_map.get(p.product_id, 0) > 0]

    for sale_num in range(1, count + 1):
        sale_date = base_date + timedelta(
            days=RNG.randint(0, 180),
            hours=RNG.randint(8, 20),
            minutes=RNG.randint(0, 59),
        )

        num_items = RNG.randint(1, 4)
        selected = RNG.sample(products_with_stock, min(num_items, len(products_with_stock)))

        total = Decimal("0.00")
        items_data = []

        for product in selected:
            inv = db.query(Inventory).filter(Inventory.product_id == product.product_id).first()
            if not inv or inv.quantity_available <= 0:
                continue
            qty = RNG.randint(1, min(5, inv.quantity_available))
            line_total = product.unit_price * qty
            total += line_total
            items_data.append((product, qty, line_total))

        if not items_data:
            continue

        sale = Sale(
            customer_name=RNG.choice(CUSTOMER_NAMES),
            sale_timestamp=sale_date,
            payment_method=RNG.choice(PAYMENT_METHODS),
            total_amount=total,
        )
        db.add(sale)
        db.flush()

        for product, qty, line_total in items_data:
            db.add(SaleItem(
                sale_id=sale.sale_id,
                product_id=product.product_id,
                quantity=qty,
                unit_price=product.unit_price,
                line_total=line_total,
            ))

            inv = db.query(Inventory).filter(Inventory.product_id == product.product_id).first()
            if inv:
                inv.quantity_available = max(0, inv.quantity_available - qty)
                inv.last_updated = sale_date

            db.add(StockMovement(
                product_id=product.product_id,
                movement_type=MovementType.SALE.value,
                quantity=qty,
                reason=f"Sale #{sale.sale_id}",
                created_at=sale_date,
            ))

    db.commit()


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        clear_data(db)

        print("Seeding 10 suppliers...")
        suppliers = seed_suppliers(db)

        print("Seeding 100 products...")
        products = seed_products(db, suppliers)

        print("Seeding inventory records...")
        seed_inventory(db, products)

        print("Seeding 500 sales transactions...")
        seed_sales(db, products, count=500)

        print("Seed complete!")
        print(f"  Suppliers: {db.query(Supplier).count()}")
        print(f"  Products:  {db.query(Product).count()}")
        print(f"  Inventory: {db.query(Inventory).count()}")
        print(f"  Sales:     {db.query(Sale).count()}")
        print(f"  Sale Items:{db.query(SaleItem).count()}")
        print(f"  Movements: {db.query(StockMovement).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
