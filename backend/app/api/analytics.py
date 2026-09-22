"""
Analytics & Economic Intelligence API Router.
Delivers lead-time curves, airline comparisons, route heatmap,
grounded AI anomaly explanations, and executive natural-language briefings.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.db.database import get_db
from backend.app.analytics.elasticity import elasticity_analyzer
from backend.app.analytics.routes import route_analytics
from backend.app.analytics.trends import trend_analyzer
from backend.app.analytics.anomalies import anomaly_detector

router = APIRouter(prefix="/api/analytics", tags=["Airfare Analytics & Intelligence"])


@router.get("/lead-time")
def get_lead_time_analytics(
    db: Session = Depends(get_db),
    route: Optional[str] = Query(None, description="Optional route code, e.g. DEL-BOM"),
):
    """Calculates lead-time fare progression across T+1, T+7, T+15, T+30, T+45 and empirical elasticity."""
    return elasticity_analyzer.analyze_lead_time(db, route=route)


@router.get("/airlines")
def get_airline_analytics(db: Session = Depends(get_db)):
    """Neutral comparative statistics (median fare, volatility, routes, observations) across carriers."""
    return trend_analyzer.get_airline_analytics(db)


@router.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db),
    threshold_pct: float = Query(25.0, ge=5.0, le=100.0),
):
    """Identifies sudden price spikes or drops with grounded AI-assisted econometric explanations."""
    return anomaly_detector.detect_route_anomalies(db, threshold_pct=threshold_pct)


@router.get("/summary")
def get_executive_summary(db: Session = Depends(get_db)):
    """AI natural-language briefing tailored for MoSPI / DIID leadership grounded strictly in observed data."""
    return anomaly_detector.generate_mospi_executive_summary(db)


@router.get("/forecast")
def get_forecast(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=14),
):
    """Experimental forward scenario forecast using Holt's double exponential smoothing."""
    return trend_analyzer.get_experimental_forecast(db, days_ahead=days)


@router.get("/heatmap")
def get_route_heatmap(
    db: Session = Depends(get_db),
    timeframe: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
):
    """Origin x Destination price movement heatmap matrix."""
    return route_analytics.get_route_heatmap(db, timeframe=timeframe)
