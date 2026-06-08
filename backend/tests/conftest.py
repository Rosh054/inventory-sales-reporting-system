import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_supplier(db_session):
    from app.models.supplier import Supplier

    s = Supplier(name="Test Supplier", email="test@supplier.com", phone="555-0000", region="North")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s


@pytest.fixture
def seed_product(db_session, seed_supplier):
    from app.models.inventory import Inventory
    from app.models.product import Product

    p = Product(
        sku="TEST-001",
        name="Test Widget",
        category="Electronics",
        unit_price=29.99,
        cost_price=15.00,
        supplier_id=seed_supplier.supplier_id,
        reorder_level=10,
        active=True,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    inv = Inventory(product_id=p.product_id, quantity_available=50)
    db_session.add(inv)
    db_session.commit()
    return p
