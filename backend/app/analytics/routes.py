"""
Route Analytics & Sector Heatmap Engine.
Computes origin-destination matrices, fare distributions,
and sector-level price volatility.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.airfare import AirfareQuote
from backend.app.models.index import RouteIndex
from backend.app.models.route import Route
import logging

logger = logging.getLogger("airfare_x.routes_analytics")


class RouteAnalytics:
    def get_route_details(
        self,
        db: Session,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        advance_window: Optional[int] = None,
        airline: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Detailed statistical breakdown for a selected route."""
        query = db.query(AirfareQuote).filter(AirfareQuote.is_outlier == False)

        if origin and origin != "ALL":
            query = query.filter(AirfareQuote.origin == origin.upper())
        if destination and destination != "ALL":
            query = query.filter(AirfareQuote.destination == destination.upper())
        if advance_window:
            query = query.filter(AirfareQuote.advance_purchase_days == advance_window)
        if airline and airline != "ALL":
            query = query.filter(AirfareQuote.airline == airline)

        quotes = query.all()
        fares = [float(q.total_fare) for q in quotes]

        if not fares:
            return {
                "route": f"{origin or 'ALL'}-{destination or 'ALL'}",
                "observation_count": 0,
                "median_fare": 0.0,
                "mean_fare": 0.0,
                "min_fare": 0.0,
                "max_fare": 0.0,
                "std_dev": 0.0,
                "distribution_histogram": [],
                "airline_breakdown": [],
            }

        fares_arr = np.array(fares)
        med = float(np.median(fares_arr))
        mean = float(np.mean(fares_arr))
        f_min = float(np.min(fares_arr))
        f_max = float(np.max(fares_arr))
        std = float(np.std(fares_arr))

        # Histogram (10 bins)
        counts, bin_edges = np.histogram(fares_arr, bins=10)
        hist = []
        for i in range(len(counts)):
            hist.append({
                "range": f"₹{int(bin_edges[i])} - ₹{int(bin_edges[i+1])}",
                "count": int(counts[i]),
                "bin_start": float(bin_edges[i]),
                "bin_end": float(bin_edges[i+1]),
            })

        # Airline breakdown
        airline_fares: Dict[str, List[float]] = {}
        for q in quotes:
            airline_fares.setdefault(q.airline, []).append(float(q.total_fare))

        airline_stats = []
        for a_name, a_fares in airline_fares.items():
            a_arr = np.array(a_fares)
            airline_stats.append({
                "airline": a_name,
                "median_fare": round(float(np.median(a_arr)), 2),
                "mean_fare": round(float(np.mean(a_arr)), 2),
                "min_fare": round(float(np.min(a_arr)), 2),
                "max_fare": round(float(np.max(a_arr)), 2),
                "observations": len(a_fares),
            })

        airline_stats.sort(key=lambda x: x["median_fare"])

        return {
            "route": f"{origin or 'ALL'}-{destination or 'ALL'}",
            "observation_count": len(fares),
            "median_fare": round(med, 2),
            "mean_fare": round(mean, 2),
            "min_fare": round(f_min, 2),
            "max_fare": round(f_max, 2),
            "std_dev": round(std, 2),
            "distribution_histogram": hist,
            "airline_breakdown": airline_stats,
        }

    def get_route_heatmap(self, db: Session, timeframe: str = "daily") -> Dict[str, Any]:
        """
        Builds Origin x Destination heatmap matrix with percentage changes.
        Supports daily, weekly, and monthly timeframes.
        """
        # Fetch latest route index records
        latest_date_rec = db.query(func.max(RouteIndex.index_date)).first()
        latest_date = latest_date_rec[0] if latest_date_rec and latest_date_rec[0] else date.today()

        days_offset = 1 if timeframe == "daily" else 7 if timeframe == "weekly" else 30
        prev_date = latest_date - timedelta(days=days_offset)

        latest_route_indices = {
            ri.route: ri for ri in db.query(RouteIndex).filter(RouteIndex.index_date == latest_date).all()
        }
        prev_route_indices = {
            ri.route: ri for ri in db.query(RouteIndex).filter(RouteIndex.index_date == prev_date).all()
        }

        origins = ["DEL", "BOM", "BLR", "CCU", "HYD", "MAA"]
        destinations = ["DEL", "BOM", "BLR", "CCU", "HYD", "GOI"]

        matrix = []
        for orig in origins:
            row = {"origin": orig, "destinations": {}}
            for dest in destinations:
                if orig == dest:
                    row["destinations"][dest] = {"change_pct": 0.0, "active": False, "median_fare": None}
                    continue

                route_code = f"{orig}-{dest}"
                ri_curr = latest_route_indices.get(route_code)
                ri_prev = prev_route_indices.get(route_code)

                if ri_curr:
                    curr_median = ri_curr.median_fare
                    prev_median = ri_prev.median_fare if ri_prev else curr_median
                    change_pct = (
                        round(((curr_median / prev_median) - 1.0) * 100.0, 2)
                        if prev_median > 0
                        else 0.0
                    )
                    row["destinations"][dest] = {
                        "route": route_code,
                        "change_pct": change_pct,
                        "median_fare": round(curr_median, 2),
                        "index_value": round(ri_curr.index_value, 2),
                        "active": True,
                    }
                else:
                    # Sector not in primary monitored trunk
                    row["destinations"][dest] = {
                        "route": route_code,
                        "change_pct": None,
                        "median_fare": None,
                        "active": False,
                    }

            matrix.append(row)

        return {
            "timeframe": timeframe,
            "as_of_date": latest_date.isoformat(),
            "comparison_date": prev_date.isoformat(),
            "origins": origins,
            "destinations": destinations,
            "matrix": matrix,
        }


route_analytics = RouteAnalytics()
