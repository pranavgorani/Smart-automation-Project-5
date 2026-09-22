"""
Configuration settings for AIRFARE-X INDIA.
Uses pydantic-settings to validate environment variables.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

# Locate root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App Information
    APP_NAME: str = "AIRFARE-X INDIA"
    APP_TITLE: str = "AIRFARE-X INDIA: Real-Time Airfare Price Intelligence & Index Platform"
    APP_DESCRIPTION: str = "Experimental Real-time Airfare Price Index (APIx) for MoSPI/DIID CPI Augmentation"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_SECRET_KEY: str = "mo_spi_diid_airfare_x_super_secret_key_2026"

    # API Credentials
    AMADEUS_CLIENT_ID: Optional[str] = ""
    AMADEUS_CLIENT_SECRET: Optional[str] = ""
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"
    SERPAPI_KEY: Optional[str] = ""

    # Database Settings
    DATABASE_URL: Optional[str] = ""
    SUPABASE_URL: Optional[str] = ""
    SUPABASE_KEY: Optional[str] = ""

    # Scraper & Ingestion
    SCRAPER_ENABLED: bool = False
    DEFAULT_RATE_LIMIT_SECONDS: int = 5
    MAX_RETRIES: int = 3

    # Statistical & Index Parameters
    INDEX_BASE_DATE: str = "2026-01-01"
    BASE_INDEX_VALUE: float = 100.0
    METHODOLOGY_VERSION: str = "1.0"
    OUTLIER_METHOD: str = "IQR"
    OUTLIER_IQR_MULTIPLIER: float = 1.5

    # Sentry & Telemetry
    SENTRY_DSN: Optional[str] = ""

    @property
    def is_demo_mode(self) -> bool:
        """Determines if the platform is in DEMO mode due to lack of production API keys."""
        return not (bool(self.AMADEUS_CLIENT_ID and self.AMADEUS_CLIENT_SECRET) or bool(self.SERPAPI_KEY))

    @property
    def resolved_database_url(self) -> str:
        """
        Returns DATABASE_URL if provided, else falls back to local SQLite.
        On Vercel serverless environments where root is read-only, uses /tmp/airfare_x.db.
        """
        if self.DATABASE_URL and len(self.DATABASE_URL.strip()) > 0:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url

        if os.environ.get("VERCEL"):
            return "sqlite:////tmp/airfare_x.db"

        sqlite_path = ROOT_DIR / "airfare_x.db"
        return f"sqlite:///{sqlite_path.as_posix()}"


settings = Settings()

