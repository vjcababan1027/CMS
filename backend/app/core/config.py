from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets

class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "Intelligent Decision Support System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    ENV: str = "development"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@cms.edu"
    EMAILS_FROM_NAME: str = "CMS System"
    SMTP_MOCK_MODE: bool = True

    # Notification scheduler settings
    NOTIFICATIONS_ENABLED: bool = True
    BIWEEKLY_REPORT_INTERVAL_DAYS: int = 14
    HIGH_RISK_SCAN_INTERVAL_MINUTES: int = 30

    # ML settings
    MODEL_PATH: str = "app/ml/models"
    RETRAIN_SCHEDULE_HOURS: int = 24  # Retrain daily

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

if settings.ENV.lower() == "production" and (not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32):
    raise ValueError("SECRET_KEY must be set and at least 32 characters in production.")
