"""
AIRFARE-X INDIA: Main FastAPI Application Entrypoint.
Organization: Ministry of Statistics and Programme Implementation (MoSPI)
Department: Data Informatics & Innovation Division (DIID)
Theme: Smart Automation - Real-Time Airfare Price Index (APIx)
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Ensure project root is prepended to sys.path so 'backend...' imports work reliably
# across Vercel serverless environments and local dev regardless of CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings, ROOT_DIR, is_running_on_vercel
from backend.app.db.database import init_db, SessionLocal
from backend.app.ingestion.scheduler import start_scheduler, shutdown_scheduler

# Import routers
from backend.app.api.health import router as health_router
from backend.app.api.flights import router as flights_router
from backend.app.api.routes import router as routes_router
from backend.app.api.index import router as index_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.sources import router as sources_router
from backend.app.api.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("airfare_x.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management:
    - Creates database schema safely via init_db() (Base.metadata.create_all).
    - In Vercel serverless mode: cold starts are kept lightweight (<100ms) by seeding
      essential reference metadata (routes, airlines, sources, dgca) only if empty.
    - In local development: auto-seeds 10,000 synthetic quotes if database is unseeded.
    - Starts the background ingestion scheduler only in non-serverless persistent environments.
    """
    logger.info("Initializing AIRFARE-X INDIA Application...")
    init_db()

    # Database bootstrap check
    db = SessionLocal()
    try:
        if is_running_on_vercel():
            # Fast serverless cold start: ensure reference tables exist without heavy generation
            from backend.app.models.route import Route
            from backend.app.db.seed import seed_routes, seed_airlines, seed_sources, seed_dgca_reference
            if db.query(Route).count() == 0:
                logger.info("Vercel cold start: seeding basic reference metadata...")
                seed_routes(db)
                seed_airlines(db)
                seed_sources(db)
                seed_dgca_reference(db)
        else:
            # Local development: auto-seed full dataset if empty
            from backend.app.models.airfare import AirfareQuote
            from backend.app.db.seed import run_full_seed
            count = db.query(AirfareQuote).count()
            if count < 1000:
                logger.info("Database is empty or unseeded. Triggering automatic initial bootstrap...")
                run_full_seed(db)
    except Exception as e:
        logger.error(f"Startup initialization notice: {e}")
    finally:
        db.close()

    # Launch background scheduler if not in serverless environment
    if not is_running_on_vercel():
        try:
            start_scheduler()
        except Exception as e:
            logger.warning(f"Could not start background scheduler: {e}")

    logger.info("AIRFARE-X INDIA is ready.")
    yield
    logger.info("Shutting down AIRFARE-X INDIA...")
    if not is_running_on_vercel():
        try:
            shutdown_scheduler()
        except Exception as e:
            logger.warning(f"Scheduler shutdown notice: {e}")


app = FastAPI(
    title="AIRINDEX INDIA API",
    description=(
        "AIRINDEX INDIA: Real-Time Airfare Price Intelligence & Index Platform for MoSPI / DIID. "
        "Augments the Consumer Price Index (CPI) Transport/Airfare subgroup through "
        "transparent, automated data ingestion and Laspeyres-type route price relatives."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
# Supports local React, Vite, Streamlit, and Vercel preview/production domains
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8501",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
]
if settings.CORS_ORIGINS:
    for origin in settings.CORS_ORIGINS.split(","):
        stripped = origin.strip()
        if stripped and stripped not in allowed_origins:
            allowed_origins.append(stripped)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)
app.include_router(flights_router)
app.include_router(routes_router)
app.include_router(index_router)
app.include_router(analytics_router)
app.include_router(sources_router)
app.include_router(admin_router)


@app.get("/health", tags=["Root"])
def root_health():
    """Simple health check endpoint returning status and service name."""
    from backend.app.db.database import engine
    from sqlalchemy import text
    db_connected = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_connected = True
    except Exception as e:
        logger.error(f"Root health check DB connectivity failure: {e}")

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "airindex-api",
        "database": "connected" if db_connected else "disconnected",
    }



@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "service": "AIRFARE-X INDIA API",
    }


@app.get("/api/info", tags=["Root"])
def api_info():
    return {
        "platform": "AIRFARE-X INDIA",
        "tagline": "Real-Time Airfare Intelligence for Smarter Price Measurement",
        "organization": "MoSPI / DIID",
        "documentation_url": "/docs",
        "health_url": "/api/health",
        "current_index_url": "/api/index/current",
        "demo_mode": settings.is_demo_mode,
    }


# Serve built React frontend if available
frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    from fastapi.responses import FileResponse
    from fastapi import Request

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Let API and docs routes pass through
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return None

        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")

