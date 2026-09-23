"""
Tests for Vercel deployment configuration, database URL normalization,
environment awareness, and health endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.config import normalize_database_url, is_running_on_vercel, Settings
from backend.app.main import app

client = TestClient(app)


def test_normalize_database_url():
    """Validates URL normalization rules."""
    # 1. postgres:// -> postgresql://
    assert (
        normalize_database_url("postgres://user:secret@db.supabase.co:5432/airfarex")
        == "postgresql://user:secret@db.supabase.co:5432/airfarex"
    )

    # 2. postgresql:// is preserved
    assert (
        normalize_database_url("postgresql://user:secret@localhost:5432/airfarex")
        == "postgresql://user:secret@localhost:5432/airfarex"
    )

    # 3. postgresql+psycopg:// is preserved
    assert (
        normalize_database_url("postgresql+psycopg://user:secret@localhost:5432/airfarex")
        == "postgresql+psycopg://user:secret@localhost:5432/airfarex"
    )

    # 4. sqlite:/// is preserved
    assert normalize_database_url("sqlite:///local.db") == "sqlite:///local.db"
    assert normalize_database_url("sqlite:////tmp/airfare_x.db") == "sqlite:////tmp/airfare_x.db"

    # 5. Whitespace is stripped
    assert (
        normalize_database_url("  postgres://user:secret@host:5432/db  ")
        == "postgresql://user:secret@host:5432/db"
    )

    # 6. Empty / None handled safely
    assert normalize_database_url("") == ""
    assert normalize_database_url(None) == ""


def test_simulation_database_url_unset_vercel_unset(monkeypatch):
    """Scenario 1: Local development with no DATABASE_URL -> local airfare_x.db."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("VERCEL_ENV", raising=False)

    s = Settings(DATABASE_URL="")
    assert not is_running_on_vercel()
    assert not s.is_vercel
    resolved = s.resolved_database_url
    assert resolved.startswith("sqlite:///")
    assert resolved.endswith("airfare_x.db")
    assert "/tmp/" not in resolved


def test_simulation_database_url_unset_vercel_set(monkeypatch):
    """Scenario 2: Vercel deployment with no DATABASE_URL -> emergency /tmp fallback."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("VERCEL", "1")

    s = Settings(DATABASE_URL="")
    assert is_running_on_vercel()
    assert s.is_vercel
    assert s.resolved_database_url == "sqlite:////tmp/airfare_x.db"
    # Verify exactly 4 slashes, never 3 (which would be relative tmp/airfare_x.db)
    assert s.resolved_database_url != "sqlite:///tmp/airfare_x.db"


def test_simulation_database_url_postgres_legacy(monkeypatch):
    """Scenario 3: DATABASE_URL=postgres://... -> normalized to postgresql://."""
    monkeypatch.setenv("DATABASE_URL", "postgres://admin:pass123@aws.rds.com:5432/db")
    s = Settings()
    assert s.resolved_database_url == "postgresql://admin:pass123@aws.rds.com:5432/db"


def test_simulation_database_url_postgresql(monkeypatch):
    """Scenario 4: DATABASE_URL=postgresql://... -> preserved."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://admin:pass123@aws.rds.com:5432/db")
    s = Settings()
    assert s.resolved_database_url == "postgresql://admin:pass123@aws.rds.com:5432/db"


def test_simulation_database_url_postgresql_psycopg(monkeypatch):
    """Scenario 5: DATABASE_URL=postgresql+psycopg://... -> preserved."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://admin:pass123@supabase.co:5432/db")
    s = Settings()
    assert s.resolved_database_url == "postgresql+psycopg://admin:pass123@supabase.co:5432/db"


def test_simulation_vercel_with_database_url(monkeypatch):
    """Scenario 6: Vercel environment with production DATABASE_URL -> always uses DATABASE_URL."""
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("DATABASE_URL", "postgres://prod_user:secret@supabase.co:5432/production")

    s = Settings()
    assert is_running_on_vercel()
    # Production PostgreSQL MUST take precedence over /tmp fallback
    assert s.resolved_database_url == "postgresql://prod_user:secret@supabase.co:5432/production"


def test_root_health_endpoint():
    """Verify GET /health returns standard 200 with status and service."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("healthy", "ok", "degraded")
    assert data.get("service") == "airindex-api"
    assert "database" in data
    assert data["database"] in ("connected", "disconnected")


def test_api_health_endpoint():
    """Verify GET /api/health does not leak credentials in response."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "engine" in data["database"]
    # Check that database status string never leaks raw credentials
    assert "@" not in str(data["database"]["status"])
    assert "password" not in str(data["database"]["status"]).lower()


def test_fastapi_direct_import():
    """Verify 'from backend.app.main import app' works cleanly."""
    from backend.app.main import app as imported_app
    assert imported_app is not None
    assert imported_app.title == "AIRINDEX INDIA API"
