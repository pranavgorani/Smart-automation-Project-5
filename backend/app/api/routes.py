"""
Routes & Airlines Metadata API Router.
Provides list of monitored sectors, active status, and airlines.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.route import Route
from backend.app.models.airline import Airline

router = APIRouter(tags=["Metadata"])


@router.get("/api/routes")
def list_routes(db: Session = Depends(get_db)):
    """Returns all 13 core domestic aviation trunk routes with weights and status."""
    routes = db.query(Route).order_by(Route.route_weight.desc()).all()
    if not routes:
        # Fallback to in-memory defaults if DB hasn't been seeded yet
        from backend.app.index.weights import DEFAULT_WEIGHTS
        return [
            {
                "origin": r.split("-")[0],
                "destination": r.split("-")[1],
                "route_code": r,
                "city_pair": r.replace("-", " - "),
                "route_weight": w,
                "active": True,
            }
            for r, w in DEFAULT_WEIGHTS.items()
        ]
    return [r.to_dict() for r in routes]


@router.get("/api/airlines")
def list_airlines(db: Session = Depends(get_db)):
    """Returns monitored Indian domestic scheduled carriers."""
    airlines = db.query(Airline).all()
    if not airlines:
        return [
            {"airline_code": "6E", "name": "IndiGo", "market_share": 61.8, "active": True},
            {"airline_code": "AI", "name": "Air India", "market_share": 14.5, "active": True},
            {"airline_code": "IX", "name": "Air India Express", "market_share": 7.2, "active": True},
            {"airline_code": "QP", "name": "Akasa Air", "market_share": 5.4, "active": True},
            {"airline_code": "SG", "name": "SpiceJet", "market_share": 4.6, "active": True},
            {"airline_code": "9I", "name": "Alliance Air", "market_share": 1.5, "active": True},
        ]
    return [a.to_dict() for a in airlines]
