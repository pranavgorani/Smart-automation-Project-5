"""
Airfare Ingestion Collector Orchestrator.
Coordinates data retrieval across live APIs, permitted web portals, and synthetic mock generator.
Executes cleaning, normalization, deduplication, outlier flagging, quality scoring,
and commits records to database.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import time
import logging
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db.database import SessionLocal
from backend.app.connectors.amadeus import AmadeusConnector
from backend.app.connectors.serpapi import SerpAPIConnector
from backend.app.connectors.permitted_web import PermittedWebConnector
from backend.app.connectors.mock_connector import MockConnector
from backend.app.processing.cleaner import cleaner
from backend.app.processing.normalizer import normalizer
from backend.app.processing.deduplicator import deduplicator
from backend.app.processing.outlier import outlier_detector
from backend.app.processing.quality import quality_scorer
from backend.app.models.airfare import AirfareQuote
from backend.app.models.source import Source, CollectionRun
from backend.app.models.index import DataQualityLog
from backend.app.models.route import Route

logger = logging.getLogger("airfare_x.collector")


class IngestionCollector:
    def __init__(self):
        self.amadeus = AmadeusConnector()
        self.serpapi = SerpAPIConnector()
        self.permitted_web = PermittedWebConnector()
        self.mock = MockConnector()

    def select_connector(self):
        """Source fallback hierarchy per Section 2 and 54."""
        if self.amadeus.is_available():
            logger.info("Using authorized Amadeus Flight Offers connector (LIVE_API).")
            return self.amadeus
        elif self.serpapi.is_available():
            logger.info("Using authorized SerpAPI Google Flights connector (LIVE_API).")
            return self.serpapi
        elif self.permitted_web.is_available():
            logger.info("Using Permitted Web Scraper (PERMITTED_WEB).")
            return self.permitted_web
        else:
            logger.info("No live API credentials provided. Using deterministic Synthetic Mock Engine (MOCK).")
            return self.mock

    def run_collection(
        self,
        db: Session,
        target_date: Optional[date] = None,
        routes: Optional[List[str]] = None,
        advance_windows: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Executes a scheduled or manual collection run for specified date.
        """
        start_time = time.time()
        if target_date is None:
            target_date = date.today()

        if advance_windows is None:
            advance_windows = [1, 7, 15, 30, 45]

        # Retrieve active routes
        if routes is None:
            db_routes = db.query(Route).filter(Route.active == True).all()
            if db_routes:
                route_codes = [r.route_code for r in db_routes]
            else:
                route_codes = [
                    "DEL-BOM", "DEL-BLR", "BOM-BLR", "DEL-CCU", "BLR-HYD",
                    "MAA-DEL", "BOM-DEL", "BLR-DEL", "HYD-DEL", "CCU-DEL",
                    "BOM-GOI", "DEL-GOI", "BLR-GOI"
                ]
        else:
            route_codes = routes

        connector = self.select_connector()
        raw_quotes: List[Dict[str, Any]] = []

        logger.info(
            f"Starting collection run: target_date={target_date}, routes={len(route_codes)}, "
            f"windows={advance_windows}, source={connector.name} ({connector.source_type})"
        )

        for route_code in route_codes:
            origin, dest = route_code.split("-")
            for window in advance_windows:
                dep_date = (target_date + timedelta(days=window)).isoformat()
                try:
                    fetched = connector.fetch_quotes(origin, dest, dep_date, window)
                    raw_quotes.extend(fetched)
                except Exception as e:
                    logger.error(f"Error fetching quotes for {route_code} (T+{window}): {e}")

        # Processing Pipeline:
        # 1. Cleaner
        valid_quotes, rejected = cleaner.clean_batch(raw_quotes)

        # 2. Normalizer
        normalized = normalizer.normalize_batch(valid_quotes)

        # 3. Deduplicator
        # Query existing hashes from database to prevent duplicate insertions
        existing_hashes = set(
            h[0] for h in db.query(AirfareQuote.raw_hash).filter(AirfareQuote.raw_hash.isnot(None)).all()
        )
        unique_quotes, duplicate_count = deduplicator.deduplicate(normalized, existing_hashes)

        # 4. Outlier detection
        flagged_quotes, outlier_count = outlier_detector.flag_outliers(unique_quotes)

        # 5. Quality scoring & Quote construction
        quote_objects = []
        for q in flagged_quotes:
            q_score = quality_scorer.evaluate_quote(q)
            quote_obj = AirfareQuote(
                source=q.get("source", connector.name),
                source_type=q.get("source_type", connector.source_type),
                source_reference=q.get("source_reference"),
                origin=q["origin"],
                destination=q["destination"],
                route=q["route"],
                airline=q["airline"],
                flight_number=q.get("flight_number"),
                departure_date=datetime.strptime(q["departure_date"], "%Y-%m-%d").date(),
                departure_time=q.get("departure_time", "08:00"),
                arrival_time=q.get("arrival_time", "10:15"),
                search_timestamp=datetime.fromisoformat(q.get("search_timestamp", datetime.utcnow().isoformat())),
                advance_purchase_days=int(q.get("advance_purchase_days", 7)),
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
            quote_objects.append(quote_obj)

        # Commit to DB
        if quote_objects:
            db.bulk_save_objects(quote_objects)

        duration = round(time.time() - start_time, 2)

        # Batch quality metrics
        quality_metrics = quality_scorer.calculate_batch_metrics(
            raw_count=len(raw_quotes),
            valid_count=len(unique_quotes),
            rejected_count=len(rejected),
            duplicate_count=duplicate_count,
            outlier_count=outlier_count,
            quotes=flagged_quotes,
            source_name=connector.name,
        )

        # Record CollectionRun
        run_record = CollectionRun(
            source=connector.name,
            source_type=connector.source_type,
            status="SUCCESS" if not rejected else "PARTIAL",
            records_collected=len(raw_quotes),
            records_processed=len(quote_objects),
            records_failed=len(rejected),
            duration_seconds=duration,
            error_message=f"{len(rejected)} records rejected during validation" if rejected else None,
        )
        db.add(run_record)
        db.flush()

        # Record DataQualityLog
        dq_log = DataQualityLog(
            run_id=run_record.id,
            source=connector.name,
            records_collected=len(raw_quotes),
            records_valid=len(unique_quotes),
            records_rejected=len(rejected),
            duplicates=duplicate_count,
            missing_values=len(rejected),
            outliers=outlier_count,
            completeness_score=quality_metrics["completeness_score"],
            validity_score=quality_metrics["validity_score"],
            timeliness_score=quality_metrics["timeliness_score"],
            uniqueness_score=quality_metrics["uniqueness_score"],
            consistency_score=quality_metrics["consistency_score"],
            quality_score=quality_metrics["quality_score"],
        )
        db.add(dq_log)

        # Update Source health entry
        source_entry = db.query(Source).filter(Source.name == connector.name).first()
        if not source_entry:
            source_entry = Source(
                name=connector.name,
                type=connector.source_type,
                status="ACTIVE",
                request_count=0,
                success_rate=100.0,
                compliance_status="COMPLIANT",
                robots_checked=True,
                rate_limit_seconds=int(connector.rate_limit_seconds),
            )
            db.add(source_entry)
        source_entry.last_success = datetime.utcnow()
        source_entry.request_count += len(route_codes) * len(advance_windows)
        source_entry.updated_at = datetime.utcnow()

        db.commit()

        logger.info(
            f"Collection finished in {duration}s: {len(quote_objects)} quotes saved, "
            f"Quality Score={quality_metrics['quality_score']}%"
        )

        return {
            "status": "SUCCESS",
            "source": connector.name,
            "source_type": connector.source_type,
            "records_collected": len(raw_quotes),
            "records_inserted": len(quote_objects),
            "duplicates": duplicate_count,
            "outliers": outlier_count,
            "rejected": len(rejected),
            "duration_seconds": duration,
            "quality_metrics": quality_metrics,
        }


collector = IngestionCollector()
