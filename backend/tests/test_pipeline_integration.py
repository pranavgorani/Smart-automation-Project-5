"""
End-to-end Integration Pipeline Test.
Validates the full workflow:
Mock Collection -> Validation -> Normalization -> Deduplication ->
Outlier Flagging -> Quality Scoring -> Database Storage -> Index Calculation.
"""

from datetime import date
from backend.app.db.database import SessionLocal
from backend.app.ingestion.collector import collector
from backend.app.index.calculator import index_calculator
from backend.app.models.index import IndexValue, RouteIndex


def test_full_pipeline_run():
    db = SessionLocal()
    try:
        target = date(2026, 9, 1)

        # 1. Execute collection
        collect_res = collector.run_collection(
            db, target_date=target, routes=["DEL-BOM", "DEL-BLR"], advance_windows=[7, 30]
        )
        assert collect_res["status"] == "SUCCESS"
        assert collect_res["records_collected"] > 0

        # 2. Compute index
        index_res = index_calculator.calculate_daily_index(db, target_date=target)
        assert index_res["index_code"] == "APIx"
        assert index_res["value"] > 50.0

        # 3. Verify in DB
        idx_rec = db.query(IndexValue).filter(IndexValue.index_date == target).first()
        assert idx_rec is not None
        assert idx_rec.index_value == index_res["value"]

        # Route indices check
        route_indices = db.query(RouteIndex).filter(RouteIndex.index_date == target).all()
        assert len(route_indices) >= 2

    finally:
        db.close()
