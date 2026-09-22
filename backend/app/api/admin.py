"""
Admin & Ingestion Control API Router.
Enables triggering manual data collection, uploading fallback CSV datasets,
updating route weights, and running the one-click Hackathon Demo workflow.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import date
import logging

from backend.app.db.database import get_db
from backend.app.ingestion.collector import collector
from backend.app.index.calculator import index_calculator
from backend.app.connectors.csv_connector import CSVConnector
from backend.app.models.route import Route
from backend.app.models.airfare import AirfareQuote
from backend.app.models.index import DGCAReferenceRecord
from backend.app.index.weights import weight_manager

logger = logging.getLogger("airfare_x.admin")
csv_connector = CSVConnector()

router = APIRouter(tags=["Admin & Orchestration"])


@router.post("/api/collect/run")
def trigger_collection(
    db: Session = Depends(get_db),
    target_date_str: Optional[str] = Form(None),
):
    """Triggers an on-demand airfare data collection and index update pipeline."""
    target_d = date.fromisoformat(target_date_str) if target_date_str else date.today()
    collect_res = collector.run_collection(db, target_date=target_d)
    index_res = index_calculator.calculate_daily_index(db, target_date=target_d)
    return {
        "status": "COMPLETED",
        "target_date": target_d.isoformat(),
        "collection": collect_res,
        "index": index_res,
    }


@router.post("/api/data/upload")
async def upload_data_csv(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    dataset_type: str = Form("QUOTES"),  # QUOTES or DGCA
):
    """Handles manual CSV ingestion fallback for airfare quotes or DGCA reference data."""
    content = await file.read()

    if dataset_type == "DGCA":
        records, errors = csv_connector.parse_dgca_csv(content)
        if errors and not records:
            raise HTTPException(status_code=400, detail={"errors": errors})

        saved_count = 0
        for r in records:
            # Upsert
            existing = (
                db.query(DGCAReferenceRecord)
                .filter(
                    DGCAReferenceRecord.month == r["month"],
                    DGCAReferenceRecord.route == r["route"],
                    DGCAReferenceRecord.airline == r["airline"],
                )
                .first()
            )
            if not existing:
                db.add(DGCAReferenceRecord(**r))
                saved_count += 1
        db.commit()
        return {"status": "SUCCESS", "records_parsed": len(records), "records_saved": saved_count, "errors": errors}

    else:
        # Airfare quotes CSV
        quotes, errors = csv_connector.parse_quotes_csv(content, filename=file.filename)
        if errors and not quotes:
            raise HTTPException(status_code=400, detail={"errors": errors})

        from backend.app.processing.cleaner import cleaner
        from backend.app.processing.normalizer import normalizer
        from backend.app.processing.deduplicator import deduplicator
        from backend.app.processing.outlier import outlier_detector
        from backend.app.processing.quality import quality_scorer
        from datetime import datetime

        valid_quotes, rejected = cleaner.clean_batch(quotes)
        normalized = normalizer.normalize_batch(valid_quotes)
        unique_quotes, _ = deduplicator.deduplicate(normalized)
        flagged, _ = outlier_detector.flag_outliers(unique_quotes)

        quote_objs = []
        for q in flagged:
            q_score = quality_scorer.evaluate_quote(q)
            quote_objs.append(
                AirfareQuote(
                    source=q["source"],
                    source_type="CSV_IMPORT",
                    origin=q["origin"],
                    destination=q["destination"],
                    route=q["route"],
                    airline=q["airline"],
                    flight_number=q.get("flight_number"),
                    departure_date=datetime.strptime(q["departure_date"], "%Y-%m-%d").date(),
                    departure_time=q.get("departure_time", "09:00"),
                    arrival_time=q.get("arrival_time", "11:15"),
                    search_timestamp=datetime.utcnow(),
                    advance_purchase_days=int(q.get("advance_purchase_days", 7)),
                    fare_class=q.get("fare_class", "Economy"),
                    fare_family=q.get("fare_family", "Standard"),
                    base_fare=float(q["base_fare"]),
                    taxes=float(q["taxes"]),
                    user_development_fee=float(q["user_development_fee"]),
                    convenience_fee=float(q["convenience_fee"]),
                    total_fare=float(q["total_fare"]),
                    currency=q.get("currency", "INR"),
                    raw_hash=q.get("raw_hash"),
                    data_quality_score=q_score,
                    is_outlier=q.get("is_outlier", False),
                )
            )

        if quote_objs:
            db.bulk_save_objects(quote_objs)
            db.commit()

        return {
            "status": "SUCCESS",
            "quotes_parsed": len(quotes),
            "quotes_accepted": len(quote_objs),
            "errors": errors,
        }


@router.post("/api/admin/weights")
def update_route_weights(
    db: Session = Depends(get_db),
    weights: Dict[str, float] = Body(...),
):
    """Configures route weights dynamically. Ensures weights normalize to 1.0."""
    normalized = weight_manager.normalize(weights)
    for route_code, w in normalized.items():
        r_obj = db.query(Route).filter(Route.route_code == route_code).first()
        if r_obj:
            r_obj.route_weight = w
    db.commit()
    weight_manager.weights = normalized
    return {"status": "SUCCESS", "updated_weights": normalized}


@router.post("/api/admin/demo/seed")
def trigger_demo_seed(db: Session = Depends(get_db)):
    """
    One-click Hackathon Demo workflow per Section 60:
    Generates synthetic quotes -> Cleans & Normalizes -> Computes 30-day APIx -> Generates DGCA benchmark -> Backtests.
    """
    from backend.app.db.seed import run_full_seed
    result = run_full_seed(db)
    return {"status": "SUCCESS", "message": "Demo environment fully seeded and refreshed.", "result": result}
