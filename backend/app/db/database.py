"""
Database engine and session management.
Supports both PostgreSQL/Supabase and local SQLite with thread safety.
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings

logger = logging.getLogger("airfare_x.db")

db_url = settings.resolved_database_url
is_sqlite = db_url.startswith("sqlite")

if is_sqlite:
    # Ensure parent directory exists for file-backed SQLite databases
    # Formats: sqlite:////tmp/airfare_x.db (4 slashes -> /tmp/...) or sqlite:///path
    try:
        # Strip sqlite:/// prefix
        db_path_str = db_url[len("sqlite:///"):] if db_url.startswith("sqlite:///") else ""
        if db_path_str and db_path_str != ":memory:":
            db_file_path = Path(db_path_str)
            db_file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not verify parent directory for SQLite DB: {e}")

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=False,
    )
else:
    # Serverless-optimized connection settings for PostgreSQL (Supabase / AWS RDS / Neon)
    # Avoids exhausting pool connections during concurrent serverless invocations
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
        pool_recycle=300,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    """FastAPI dependency for obtaining a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes all registered models into the database tables."""
    # Import all models to ensure metadata is populated
    import backend.app.models.airfare
    import backend.app.models.route
    import backend.app.models.airline
    import backend.app.models.source
    import backend.app.models.index

    Base.metadata.create_all(bind=engine)
