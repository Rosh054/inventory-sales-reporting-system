from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_exports,
    routes_health,
    routes_inventory,
    routes_products,
    routes_reports,
    routes_sales,
    routes_suppliers,
)
from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Inventory tracking, sales transactions, and SQL-backed business reporting",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_products.router)
app.include_router(routes_suppliers.router)
app.include_router(routes_inventory.router)
app.include_router(routes_sales.router)
app.include_router(routes_reports.router)
app.include_router(routes_exports.router)
