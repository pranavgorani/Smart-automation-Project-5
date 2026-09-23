"""
Configuration settings for AIRFARE-X INDIA.
Uses pydantic-settings to validate environment variables.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

# Locate root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def normalize_database_url(raw_url: Optional[str]) -> str:
    """
    Normalizes database connection strings for SQLAlchemy compatibility:
    - postgres:// -> postgresql://
    - Preserves postgresql:// and postgresql+psycopg://
    - Preserves sqlite:/// paths
    - Strips surrounding whitespace
    """
    if not raw_url:
        return ""
    url = raw_url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def is_running_on_vercel() -> bool:
    """Detects whether the app is executing inside the Vercel serverless environment."""
    return bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))


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
    # Reads directly from environment variable if present
    DATABASE_URL: Optional[str] = os.environ.get("DATABASE_URL", "")
    SUPABASE_URL: Optional[str] = ""
    SUPABASE_KEY: Optional[str] = ""

    # CORS Settings
    CORS_ORIGINS: str = ""

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
    def is_vercel(self) -> bool:
        """Helper property to check Vercel environment."""
        return is_running_on_vercel()

    @property
    def resolved_database_url(self) -> str:
        """
        Database resolution logic:
        1. If DATABASE_URL is set (environment or settings):
           Normalize (e.g. postgres:// -> postgresql://) and use it.
           Supports PostgreSQL (postgresql://, postgresql+psycopg://, postgres://).
        2. If running on Vercel and DATABASE_URL is not set:
           Emergency demo fallback: sqlite:////tmp/airfare_x.db.
           NOTE: /tmp is ephemeral in serverless environments and must NOT be considered
           persistent storage. For persistent production data on Vercel, configure DATABASE_URL.
        3. Local development fallback:
           SQLite in project directory: ./airfare_x.db.
        """
        # Always check os.environ directly as well as self.DATABASE_URL
        env_db_url = os.environ.get("DATABASE_URL") or self.DATABASE_URL
        if env_db_url and env_db_url.strip():
            return normalize_database_url(env_db_url)

        if is_running_on_vercel():
            # Exact 4 slashes: sqlite:////tmp/airfare_x.db resolves to absolute path /tmp/airfare_x.db
            # Never use sqlite:///tmp/airfare_x.db (which resolves to relative path in read-only project dir)
            return "sqlite:////tmp/airfare_x.db"

        # Local development fallback: project root airfare_x.db
        sqlite_path = ROOT_DIR / "airfare_x.db"
        return f"sqlite:///{sqlite_path.as_posix()}"


settings = Settings()


