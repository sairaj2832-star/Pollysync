import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "PolliSync API"
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pollisync.db")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
