"""
AIRFARE-X INDIA: Main FastAPI Application Entrypoint.
Organization: Ministry of Statistics and Programme Implementation (MoSPI)
Department: Data Informatics & Innovation Division (DIID)
Theme: Smart Automation - Real-Time Airfare Price Index (APIx)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from backend.app.config import settings, ROOT_DIR
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

app = FastAPI(
    title="AIRFARE-X INDIA API",
    description=(
        "Real-Time Airfare Price Intelligence & Index Platform for MoSPI / DIID. "
        "Augments the Consumer Price Index (CPI) Transport/Airfare subgroup through "
        "transparent, automated data ingestion and Laspeyres-type route price relatives."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local React dev, Vite, Streamlit, and preview hosts
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


@app.on_event("startup")
def on_startup():
    logger.info("Initializing AIRFARE-X INDIA Application...")
    init_db()

    # Auto-seed if database is fresh
    db = SessionLocal()
    try:
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

    # Launch background scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.warning(f"Could not start background scheduler: {e}")

    logger.info("AIRFARE-X INDIA is ready.")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Shutting down AIRFARE-X INDIA...")
    shutdown_scheduler()


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
        
        # If client explicitly requests application/json for root, return API info
        if full_path == "" and "application/json" in request.headers.get("accept", ""):
            return api_info()

        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/", tags=["Root"])
    def root():
        return api_info()
