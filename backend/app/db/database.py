"""
Database engine and session management.
Supports both PostgreSQL/Supabase and local SQLite with thread safety.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings

db_url = settings.resolved_database_url

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
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
