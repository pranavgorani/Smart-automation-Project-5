"""
Flight Quotes & Fares API Router.
Supports high-performance querying, multi-dimensional filtering, and pagination.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.models.airfare import AirfareQuote

router = APIRouter(tags=["Flights & Fares"])


@router.get("/api/flights")
def get_flight_quotes(
    db: Session = Depends(get_db),
    route: Optional[str] = Query(None, description="Sector code, e.g., DEL-BOM"),
    origin: Optional[str] = Query(None, description="Origin IATA code, e.g., DEL"),
    destination: Optional[str] = Query(None, description="Destination IATA code, e.g., BOM"),
    airline: Optional[str] = Query(None, description="Airline name, e.g., IndiGo"),
    advance_window: Optional[int] = Query(None, description="Advance purchase window: 1, 7, 15, 30, 45"),
    departure_date: Optional[str] = Query(None, description="Departure date in YYYY-MM-DD"),
    source_type: Optional[str] = Query(None, description="LIVE_API, PERMITTED_WEB, MOCK, CSV_IMPORT"),
    is_outlier: Optional[bool] = Query(None, description="Filter outlier records"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Retrieves paginated and filtered flight airfare observations."""
    query = db.query(AirfareQuote)

    if route and route.upper() != "ALL":
        query = query.filter(AirfareQuote.route == route.upper())
    if origin and origin.upper() != "ALL":
        query = query.filter(AirfareQuote.origin == origin.upper())
    if destination and destination.upper() != "ALL":
        query = query.filter(AirfareQuote.destination == destination.upper())
    if airline and airline != "ALL":
        query = query.filter(AirfareQuote.airline == airline)
    if advance_window:
        query = query.filter(AirfareQuote.advance_purchase_days == advance_window)
    if departure_date:
        query = query.filter(AirfareQuote.departure_date == departure_date)
    if source_type and source_type != "ALL":
        query = query.filter(AirfareQuote.source_type == source_type)
    if is_outlier is not None:
        query = query.filter(AirfareQuote.is_outlier == is_outlier)

    total_records = query.count()
    quotes = query.order_by(AirfareQuote.id.desc()).offset(offset).limit(limit).all()

    return {
        "total": total_records,
        "offset": offset,
        "limit": limit,
        "results": [q.to_dict() for q in quotes],
    }


@router.get("/api/fares")
def get_fare_summary(
    db: Session = Depends(get_db),
    route: Optional[str] = Query(None),
):
    """Aggregate statistics (min, max, median, mean) across fares."""
    from backend.app.analytics.routes import route_analytics
    return route_analytics.get_route_details(db, origin=route.split("-")[0] if route and "-" in route else None,
                                            destination=route.split("-")[1] if route and "-" in route else None)
