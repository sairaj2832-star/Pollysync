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
    cors_origins: str = os.getenv("CORS_ORIGINS", "")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    algorithm: str = "HS256"
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "14"))
    oauth_google_client_id: str = os.getenv("OAUTH_GOOGLE_CLIENT_ID", "")
    oauth_google_client_secret: str = os.getenv("OAUTH_GOOGLE_CLIENT_SECRET", "")
    oauth_google_redirect_uri: str = os.getenv("OAUTH_GOOGLE_REDIRECT_URI", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    @property
    def allowed_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if self.frontend_origin and self.frontend_origin not in origins:
            origins.append(self.frontend_origin)
        return origins

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}

    def validate_security(self) -> None:
        if self.is_production and self.secret_key == "change-me-in-production":
            raise RuntimeError("SECRET_KEY must be set to a strong random value in production.")


settings = Settings()
