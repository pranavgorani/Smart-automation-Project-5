"""
Database Seeder and Demo Initializer.
Initializes tables, populates 13 Indian routes, 6 airlines, DGCA reference data,
generates 10,000+ realistic synthetic airfare quotes across 30 days,
and calculates historical daily APIx indices.
"""

from typing import Dict, Any
from datetime import date, datetime, timedelta
import logging
from sqlalchemy.orm import Session
import pandas as pd

from backend.app.config import ROOT_DIR
from backend.app.db.database import Base, engine, SessionLocal, init_db
from backend.app.models.route import Route
from backend.app.models.airline import Airline
from backend.app.models.airfare import AirfareQuote
from backend.app.models.index import IndexValue, RouteIndex, DataQualityLog, DGCAReferenceRecord
from backend.app.models.source import Source, CollectionRun
from backend.app.connectors.mock_connector import MockConnector
from backend.app.processing.cleaner import cleaner
from backend.app.processing.normalizer import normalizer
from backend.app.processing.deduplicator import deduplicator
from backend.app.processing.outlier import outlier_detector
from backend.app.processing.quality import quality_scorer
from backend.app.index.calculator import index_calculator
from backend.app.index.weights import weight_manager

logger = logging.getLogger("airfare_x.seed")


def seed_routes(db: Session):
    """Seeds the 13 core domestic aviation trunk routes."""
    csv_path = ROOT_DIR / "data" / "routes.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            r_code = str(row["route_code"]).strip()
            existing = db.query(Route).filter(Route.route_code == r_code).first()
            if not existing:
                r = Route(
                    origin=str(row["origin"]).strip(),
                    destination=str(row["destination"]).strip(),
                    route_code=r_code,
                    city_pair=str(row["city_pair"]).strip(),
                    passenger_weight=float(row["passenger_weight"]),
                    route_weight=float(row["route_weight"]),
                    active=bool(row["active"]),
                )
                db.add(r)
    db.commit()


def seed_airlines(db: Session):
    """Seeds monitored Indian domestic carriers."""
    airlines_data = [
        {"code": "6E", "name": "IndiGo", "market_share": 61.8},
        {"code": "AI", "name": "Air India", "market_share": 14.5},
        {"code": "IX", "name": "Air India Express", "market_share": 7.2},
        {"code": "QP", "name": "Akasa Air", "market_share": 5.4},
        {"code": "SG", "name": "SpiceJet", "market_share": 4.6},
        {"code": "9I", "name": "Alliance Air", "market_share": 1.5},
    ]
    for a in airlines_data:
        existing = db.query(Airline).filter(Airline.airline_code == a["code"]).first()
        if not existing:
            db.add(
                Airline(
                    airline_code=a["code"],
                    name=a["name"],
                    market_share=a["market_share"],
                    active=True,
                )
            )
    db.commit()


def seed_dgca_reference(db: Session):
    """Loads historical DGCA monthly route benchmarks from CSV."""
    csv_path = ROOT_DIR / "data" / "dgca_reference.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            m = str(row["month"]).strip()
            r = str(row["route"]).strip()
            a = str(row["airline"]).strip()
            existing = (
                db.query(DGCAReferenceRecord)
                .filter(
                    DGCAReferenceRecord.month == m,
                    DGCAReferenceRecord.route == r,
                    DGCAReferenceRecord.airline == a,
                )
                .first()
            )
            if not existing:
                rec = DGCAReferenceRecord(
                    month=m,
                    route=r,
                    airline=a,
                    passengers=int(row["passengers"]),
                    average_fare=float(row["average_fare"]),
                    fuel_surcharge=float(row.get("fuel_surcharge", 0.0)),
                    source=str(row.get("source", "DGCA_REPORT")),
                )
                db.add(rec)
        db.commit()


def seed_sources(db: Session):
    """Registers standard data sources."""
    sources_data = [
        {"name": "Amadeus Flight Offers Search", "type": "LIVE_API", "rate_limit": 5},
        {"name": "SerpAPI Google Flights", "type": "LIVE_API", "rate_limit": 5},
        {"name": "Permitted Web Portal Scraper", "type": "PERMITTED_WEB", "rate_limit": 5},
        {"name": "AIRFARE-X Synthetic Generator", "type": "MOCK", "rate_limit": 0},
        {"name": "CSV Ingestion Fallback", "type": "CSV_IMPORT", "rate_limit": 0},
    ]
    for s in sources_data:
        existing = db.query(Source).filter(Source.name == s["name"]).first()
        if not existing:
            db.add(
                Source(
                    name=s["name"],
                    type=s["type"],
                    status="ACTIVE",
                    rate_limit_seconds=s["rate_limit"],
                    success_rate=100.0,
                    compliance_status="COMPLIANT",
                    robots_checked=True,
                )
            )
    db.commit()


def run_full_seed(db: Session, target_date: date = date(2026, 3, 22), days: int = 30) -> Dict[str, Any]:
    """
    Executes full bootstrapping workflow:
    1. Initialize schema
    2. Seed routes, airlines, sources, DGCA data
    3. Generate 10,000+ realistic synthetic quotes across 30 days
    4. Compute daily APIx index for all 30 days
    5. Log data quality records
    """
    logger.info("Initializing database schema...")
    init_db()

    logger.info("Seeding metadata (routes, airlines, sources, DGCA reference)...")
    seed_routes(db)
    seed_airlines(db)
    seed_sources(db)
    seed_dgca_reference(db)

    # Check if quotes already exist
    quote_count = db.query(AirfareQuote).count()
    if quote_count < 5000:
        logger.info(f"Generating 30-day synthetic airfare observations (Target: 10,000+)...")
        mock = MockConnector(seed=42)
        raw_quotes = mock.generate_full_dataset(days=days, end_date=target_date)

        logger.info("Cleaning raw observations...")
        valid_quotes, rejected = cleaner.clean_batch(raw_quotes)

        logger.info("Normalizing fares and civil aviation tax decomposition...")
        normalized = normalizer.normalize_batch(valid_quotes)

        logger.info("Deduplicating quotes via SHA-256 fingerprinting...")
        unique_quotes, duplicate_count = deduplicator.deduplicate(normalized)

        logger.info("Detecting statistical outliers (IQR)...")
        flagged_quotes, outlier_count = outlier_detector.flag_outliers(unique_quotes)

        logger.info(f"Persisting {len(flagged_quotes)} airfare quotes to database...")
        quote_objects = []
        for q in flagged_quotes:
            q_score = quality_scorer.evaluate_quote(q)
            q_obj = AirfareQuote(
                source=q["source"],
                source_type=q["source_type"],
                source_reference=q.get("source_reference"),
                origin=q["origin"],
                destination=q["destination"],
                route=q["route"],
                airline=q["airline"],
                flight_number=q.get("flight_number"),
                departure_date=datetime.strptime(q["departure_date"], "%Y-%m-%d").date(),
                departure_time=q.get("departure_time", "08:00"),
                arrival_time=q.get("arrival_time", "10:15"),
                search_timestamp=datetime.fromisoformat(q["search_timestamp"]),
                advance_purchase_days=int(q["advance_purchase_days"]),
                fare_class=q.get("fare_class", "Economy"),
                fare_family=q.get("fare_family", "Standard"),
                base_fare=float(q["base_fare"]),
                taxes=float(q.get("taxes", 0.0)),
                user_development_fee=float(q.get("user_development_fee", 0.0)),
                convenience_fee=float(q.get("convenience_fee", 350.0)),
                other_charges=float(q.get("other_charges", 0.0)),
                total_fare=float(q["total_fare"]),
                currency=q.get("currency", "INR"),
                availability=int(q.get("availability", 9)),
                stops=int(q.get("stops", 0)),
                refundability=q.get("refundability", "Non-refundable"),
                raw_hash=q.get("raw_hash"),
                data_quality_score=q_score,
                is_outlier=q.get("is_outlier", False),
                outlier_method=q.get("outlier_method"),
                outlier_score=q.get("outlier_score"),
            )
            quote_objects.append(q_obj)

        # Bulk save in batches of 2000
        batch_size = 2000
        for i in range(0, len(quote_objects), batch_size):
            db.bulk_save_objects(quote_objects[i : i + batch_size])
            db.commit()

        quote_count = len(quote_objects)
        logger.info(f"Successfully committed {quote_count} quotes to database.")

        # Log Data Quality
        dq_metrics = quality_scorer.calculate_batch_metrics(
            raw_count=len(raw_quotes),
            valid_count=len(unique_quotes),
            rejected_count=len(rejected),
            duplicate_count=duplicate_count,
            outlier_count=outlier_count,
            quotes=flagged_quotes,
            source_name="AIRFARE-X Synthetic Generator",
        )
        dq_log = DataQualityLog(
            source="AIRFARE-X Synthetic Generator",
            records_collected=len(raw_quotes),
            records_valid=len(unique_quotes),
            records_rejected=len(rejected),
            duplicates=duplicate_count,
            missing_values=len(rejected),
            outliers=outlier_count,
            completeness_score=dq_metrics["completeness_score"],
            validity_score=dq_metrics["validity_score"],
            timeliness_score=dq_metrics["timeliness_score"],
            uniqueness_score=dq_metrics["uniqueness_score"],
            consistency_score=dq_metrics["consistency_score"],
            quality_score=dq_metrics["quality_score"],
        )
        db.add(dq_log)
        db.commit()

    # Calculate 30-day chronological index series
    logger.info(f"Calculating chronological daily APIx index for {days} days ending {target_date}...")
    start_d = target_date - timedelta(days=days - 1)
    index_calculator.batch_calculate_history(db, start_d, target_date)

    latest_idx = (
        db.query(IndexValue).order_by(IndexValue.index_date.desc()).first()
    )

    logger.info("Database bootstrap & demo seed complete.")
    return {
        "status": "INITIALIZED",
        "total_quotes": quote_count,
        "routes_seeded": 13,
        "airlines_seeded": 6,
        "days_indexed": days,
        "latest_apix": latest_idx.index_value if latest_idx else 100.0,
        "daily_change_pct": latest_idx.daily_change if latest_idx else 0.0,
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_full_seed(db)
    finally:
        db.close()
