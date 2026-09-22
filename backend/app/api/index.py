"""
Airfare Price Index (APIx) API Router.
Delivers current index snapshot, historical time series, and sector indices.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.models.index import IndexValue, RouteIndex
from backend.app.index.methodology import get_methodology_spec
from backend.app.config import settings

router = APIRouter(tags=["Airfare Price Index (APIx)"])


@router.get("/api/index/current")
def get_current_index(db: Session = Depends(get_db)):
    """
    Returns the latest published Experimental Real-time Airfare Price Index (APIx).
    Response matches Section 33 specification.
    """
    latest = (
        db.query(IndexValue)
        .order_by(IndexValue.index_date.desc())
        .first()
    )
    if not latest:
        # Fallback baseline response if no calculations performed yet
        return {
            "index_name": "Experimental Real-time Airfare Price Index",
            "index_code": "APIx",
            "value": 100.0,
            "daily_change_pct": 0.0,
            "weekly_change_pct": 0.0,
            "monthly_change_pct": 0.0,
            "base_period": settings.INDEX_BASE_DATE,
            "routes": 13,
            "observations": 0,
            "quality_score": 100.0,
            "methodology_version": settings.METHODOLOGY_VERSION,
        }

    return {
        "index_name": "Experimental Real-time Airfare Price Index",
        "index_code": "APIx",
        "value": round(latest.index_value, 2),
        "daily_change_pct": round(latest.daily_change, 2),
        "weekly_change_pct": round(latest.weekly_change, 2),
        "monthly_change_pct": round(latest.monthly_change, 2),
        "base_period": latest.base_period,
        "routes": latest.route_count,
        "observations": latest.observation_count,
        "quality_score": round(latest.confidence_score, 1),
        "methodology_version": latest.methodology_version,
        "as_of_date": latest.index_date.isoformat(),
    }


@router.get("/api/index/history")
def get_index_history(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of historical days to retrieve"),
):
    """Retrieves chronological historical APIx index series for charts and trendlines."""
    records = (
        db.query(IndexValue)
        .order_by(IndexValue.index_date.desc())
        .limit(days)
        .all()
    )
    records = sorted(records, key=lambda r: r.index_date)
    return [r.to_dict() for r in records]


@router.get("/api/index/route/{route}")
def get_route_index_history(
    route: str,
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """Retrieves historical index series and median fares for a specific route."""
    clean_route = route.upper().strip()
    records = (
        db.query(RouteIndex)
        .filter(RouteIndex.route == clean_route)
        .order_by(RouteIndex.index_date.desc())
        .limit(days)
        .all()
    )
    if not records:
        raise HTTPException(status_code=404, detail=f"No index records found for route '{clean_route}'")

    records = sorted(records, key=lambda r: r.index_date)
    return [r.to_dict() for r in records]


@router.get("/api/methodology")
def get_methodology():
    """Returns official MoSPI/DIID transparent index methodology specification."""
    return get_methodology_spec()
