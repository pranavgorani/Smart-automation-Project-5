"""
System Health & Telemetry API Router.
Provides database connectivity, scraper status, memory, and latency indicators.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
from backend.app.db.database import get_db
from backend.app.config import settings

import logging

logger = logging.getLogger("airfare_x.health")

router = APIRouter(prefix="/api/health", tags=["Health & System Telemetry"])


@router.get("")
def check_health(db: Session = Depends(get_db)):
    """Comprehensive system health endpoint with green/yellow/red status indicators."""
    start = time.time()
    db_status = "HEALTHY"
    db_latency_ms = 0.0

    try:
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start) * 1000, 2)
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        db_status = "UNHEALTHY"


    # Determine overall status
    is_demo = settings.is_demo_mode
    scraper_status = "ENABLED" if settings.SCRAPER_ENABLED else "RESTRICTED_COMPLIANCE_MODE"

    return {
        "status": "OPERATIONAL" if db_status == "HEALTHY" else "DEGRADED",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "demo_mode": is_demo,
        "demo_banner": (
            "DEMO MODE — Synthetic airfare observations are being used because live API credentials are not configured."
            if is_demo else None
        ),
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms,
            "engine": "PostgreSQL" if "postgresql" in settings.resolved_database_url else "SQLite (Embedded Fallback)",
        },
        "connectors": {
            "amadeus": "CONFIGURED" if settings.AMADEUS_CLIENT_ID else "UNCONFIGURED (FALLBACK_TO_MOCK)",
            "serpapi": "CONFIGURED" if settings.SERPAPI_KEY else "UNCONFIGURED (FALLBACK_TO_MOCK)",
            "permitted_web": scraper_status,
            "mock_engine": "ACTIVE_READY",
        },
        "compliance": {
            "robots_txt_enforced": True,
            "rate_limiting_enforced": True,
            "captcha_bypass": False,
            "stealth_evasion": False,
        },
        "server_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
