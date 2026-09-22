"""
Historical Trends & Comparative Airline Analytics Engine.
Provides neutral comparative statistics across Indian carriers
and experimental short-term forecasting.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.airfare import AirfareQuote
from backend.app.models.index import IndexValue
from backend.app.models.airline import Airline
import logging

logger = logging.getLogger("airfare_x.trends")


class TrendAnalyzer:
    def get_airline_analytics(self, db: Session) -> List[Dict[str, Any]]:
        """
        Computes neutral statistical comparison across monitored airlines:
        median fare, mean fare, volatility (CV %), routes covered, observations, and quality.
        Does NOT rank airlines as 'best' or 'worst' per Section 28.
        """
        quotes = db.query(AirfareQuote).filter(AirfareQuote.is_outlier == False).all()

        airline_data: Dict[str, Dict[str, Any]] = {}
        for q in quotes:
            name = q.airline
            if name not in airline_data:
                airline_data[name] = {
                    "fares": [],
                    "routes": set(),
                    "quality_scores": [],
                }
            airline_data[name]["fares"].append(float(q.total_fare))
            airline_data[name]["routes"].add(q.route)
            airline_data[name]["quality_scores"].append(float(q.data_quality_score or 100.0))

        results = []
        for name, data in airline_data.items():
            fares_arr = np.array(data["fares"])
            med = float(np.median(fares_arr))
            mean = float(np.mean(fares_arr))
            std = float(np.std(fares_arr))
            cv = float((std / mean) * 100.0) if mean > 0 else 0.0  # Volatility / Coefficient of variation
            avg_qual = float(np.mean(data["quality_scores"]))

            results.append({
                "airline": name,
                "median_fare": round(med, 2),
                "average_fare": round(mean, 2),
                "fare_volatility_pct": round(cv, 1),
                "routes_covered": len(data["routes"]),
                "observations": len(data["fares"]),
                "data_quality_score": round(avg_qual, 1),
            })

        results.sort(key=lambda x: x["observations"], reverse=True)
        return results

    def get_experimental_forecast(self, db: Session, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Generates an experimental 7-day forecast using double exponential smoothing.
        Clearly labeled as an analytical prototype per Section 58.
        """
        records = (
            db.query(IndexValue)
            .order_by(IndexValue.index_date.asc())
            .all()
        )
        if not records:
            return {"status": "NO_DATA", "forecast": []}

        series = [float(r.index_value) for r in records]
        last_date = records[-1].index_date

        # Holt's Double Exponential Smoothing (level and trend)
        alpha = 0.35
        beta = 0.15
        level = series[0]
        trend = series[1] - series[0] if len(series) > 1 else 0.0

        for val in series:
            prev_level = level
            level = alpha * val + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend

        forecast_points = []
        for h in range(1, days_ahead + 1):
            f_val = level + (h * trend)
            # Add reasonable confidence interval bands (+- 1.5% * sqrt(h))
            margin = f_val * (0.015 * np.sqrt(h))
            target_d = last_date + timedelta(days=h)
            forecast_points.append({
                "date": target_d.isoformat(),
                "forecast_value": round(f_val, 2),
                "confidence_lower": round(f_val - margin, 2),
                "confidence_upper": round(f_val + margin, 2),
            })

        return {
            "forecast_label": "Experimental Short-Term Forecast (Double Exponential Smoothing)",
            "disclaimer": (
                "Experimental forecast only. Intended for analytical scenario planning; "
                "not an official MoSPI forward projection or price expectation."
            ),
            "method": "Holt_Double_Exponential_Smoothing",
            "as_of_date": last_date.isoformat(),
            "forecast_points": forecast_points,
        }


trend_analyzer = TrendAnalyzer()
