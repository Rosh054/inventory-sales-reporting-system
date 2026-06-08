from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://inventory:inventory@localhost:5432/inventory_db"
    app_name: str = "Inventory & Sales Reporting System"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
