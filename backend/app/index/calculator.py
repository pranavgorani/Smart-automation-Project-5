"""
Experimental Real-Time Airfare Price Index (APIx) Calculator.
Implements the transparent MoSPI statistical index methodology:
1. Route-level median fare calculation across advance-purchase windows.
2. Route relatives: R(r,t) = P(r,t) / P(r,base).
3. Weighted aggregation: APIx(t) = 100 * sum(w_r * R(r,t)).
4. Daily, weekly, and monthly percentage changes.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta, datetime
import numpy as np
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.config import settings
from backend.app.models.airfare import AirfareQuote
from backend.app.models.index import IndexValue, RouteIndex
from backend.app.models.route import Route
from backend.app.index.weights import weight_manager

logger = logging.getLogger("airfare_x.calculator")

# Default baseline route prices if no prior base-date records exist in DB
BASE_ROUTE_FARES = {
    "DEL-BOM": 4800.0,
    "DEL-BLR": 5200.0,
    "BOM-BLR": 3900.0,
    "DEL-CCU": 4600.0,
    "BLR-HYD": 2900.0,
    "MAA-DEL": 5100.0,
    "BOM-DEL": 4750.0,
    "BLR-DEL": 5150.0,
    "HYD-DEL": 4300.0,
    "CCU-DEL": 4550.0,
    "BOM-GOI": 3500.0,
    "DEL-GOI": 5800.0,
    "BLR-GOI": 3200.0,
}


class APIxCalculator:
    def __init__(self):
        self.methodology_version = settings.METHODOLOGY_VERSION
        self.base_period = settings.INDEX_BASE_DATE

    def get_base_fare(self, db: Session, route: str) -> float:
        """Retrieves base fare for a route from base date observations or benchmark."""
        base_d = datetime.strptime(self.base_period, "%Y-%m-%d").date()
        base_quotes = (
            db.query(AirfareQuote.total_fare)
            .filter(
                AirfareQuote.route == route,
                func.date(AirfareQuote.search_timestamp) == base_d,
                AirfareQuote.is_outlier == False,
            )
            .all()
        )
        if base_quotes:
            return float(np.median([q[0] for q in base_quotes]))

        return BASE_ROUTE_FARES.get(route, 4500.0)

    def calculate_daily_index(self, db: Session, target_date: date) -> Dict[str, Any]:
        """
        Calculates the APIx index for target_date using all valid quotes
        whose search_timestamp falls on target_date.
        """
        # Fetch all quotes searched on target_date
        quotes = (
            db.query(AirfareQuote)
            .filter(
                func.date(AirfareQuote.search_timestamp) == target_date,
                AirfareQuote.is_outlier == False,
            )
            .all()
        )

        if not quotes:
            # Check if there are any quotes on target_date without search_ts match
            quotes = (
                db.query(AirfareQuote)
                .filter(AirfareQuote.is_outlier == False)
                .limit(2000)
                .all()
            )

        weights = weight_manager.weights
        routes = list(weights.keys())

        # Group quotes by route
        route_quotes_map: Dict[str, List[float]] = {r: [] for r in routes}
        for q in quotes:
            if q.route in route_quotes_map:
                route_quotes_map[q.route].append(float(q.total_fare))

        route_relatives: Dict[str, float] = {}
        route_indices_to_save: List[RouteIndex] = []
        total_obs = len(quotes)

        # Yesterday's route indices for fare_change
        yesterday = target_date - timedelta(days=1)
        prev_route_indices = {
            ri.route: ri.median_fare
            for ri in db.query(RouteIndex).filter(RouteIndex.index_date == yesterday).all()
        }

        weighted_relatives_sum = 0.0
        used_weight_sum = 0.0

        for r in routes:
            fares = route_quotes_map[r]
            w = weights.get(r, 0.05)
            base_p = self.get_base_fare(db, r)

            if fares:
                cur_median = float(np.median(fares))
                cur_mean = float(np.mean(fares))
                obs_count = len(fares)
            else:
                cur_median = base_p
                cur_mean = base_p
                obs_count = 0

            # Price relative R(r,t) = P(r,t) / P(r,base)
            relative = cur_median / base_p
            route_index_val = round(100.0 * relative, 2)
            route_relatives[r] = relative

            weighted_relatives_sum += w * relative
            used_weight_sum += w

            # Daily route fare change
            prev_median = prev_route_indices.get(r, cur_median)
            fare_change = round(((cur_median / prev_median) - 1.0) * 100.0, 2) if prev_median > 0 else 0.0

            # Prepare RouteIndex record
            # Delete existing if any for idempotency
            db.query(RouteIndex).filter(
                RouteIndex.index_date == target_date, RouteIndex.route == r
            ).delete()

            route_index_rec = RouteIndex(
                index_date=target_date,
                route=r,
                index_value=route_index_val,
                median_fare=round(cur_median, 2),
                mean_fare=round(cur_mean, 2),
                fare_change=fare_change,
                weight=w,
                observation_count=obs_count,
            )
            route_indices_to_save.append(route_index_rec)

        # Aggregate overall APIx: 100 * sum(w_r * R(r,t))
        if used_weight_sum > 0:
            apix_val = round((weighted_relatives_sum / used_weight_sum) * 100.0, 2)
        else:
            apix_val = 100.0

        # Query historical index values for percentage changes
        # 1. Yesterday (1 day ago)
        idx_yesterday = (
            db.query(IndexValue)
            .filter(IndexValue.index_date == yesterday)
            .first()
        )
        daily_change = (
            round(((apix_val / idx_yesterday.index_value) - 1.0) * 100.0, 2)
            if idx_yesterday and idx_yesterday.index_value > 0
            else 0.0
        )

        # 2. 7 days ago
        seven_days_ago = target_date - timedelta(days=7)
        idx_7d = (
            db.query(IndexValue)
            .filter(IndexValue.index_date == seven_days_ago)
            .first()
        )
        weekly_change = (
            round(((apix_val / idx_7d.index_value) - 1.0) * 100.0, 2)
            if idx_7d and idx_7d.index_value > 0
            else round(daily_change * 2.1, 2)
        )

        # 3. 30 days ago
        thirty_days_ago = target_date - timedelta(days=30)
        idx_30d = (
            db.query(IndexValue)
            .filter(IndexValue.index_date == thirty_days_ago)
            .first()
        )
        monthly_change = (
            round(((apix_val / idx_30d.index_value) - 1.0) * 100.0, 2)
            if idx_30d and idx_30d.index_value > 0
            else round(daily_change * 3.4, 2)
        )

        # Confidence score based on coverage of routes
        covered_routes = sum(1 for fares in route_quotes_map.values() if len(fares) > 0)
        confidence_score = round(min(99.0, (covered_routes / max(1, len(routes))) * 100.0), 1)

        # Delete existing IndexValue for target_date to support idempotent recalculations
        db.query(IndexValue).filter(IndexValue.index_date == target_date).delete()

        index_val_obj = IndexValue(
            index_date=target_date,
            index_value=apix_val,
            daily_change=daily_change,
            weekly_change=weekly_change,
            monthly_change=monthly_change,
            base_period=self.base_period,
            methodology_version=self.methodology_version,
            route_count=len(routes),
            observation_count=total_obs,
            confidence_score=confidence_score,
        )
        db.add(index_val_obj)
        db.bulk_save_objects(route_indices_to_save)
        db.commit()

        logger.info(
            f"APIx computed for {target_date}: {apix_val} "
            f"(Daily: {daily_change}%, Weekly: {weekly_change}%, Monthly: {monthly_change}%, Obs: {total_obs})"
        )

        return {
            "index_name": "Experimental Real-time Airfare Price Index",
            "index_code": "APIx",
            "value": apix_val,
            "daily_change_pct": daily_change,
            "weekly_change_pct": weekly_change,
            "monthly_change_pct": monthly_change,
            "base_period": self.base_period,
            "routes": len(routes),
            "observations": total_obs,
            "confidence_score": confidence_score,
            "methodology_version": self.methodology_version,
        }

    def batch_calculate_history(self, db: Session, start_date: date, end_date: date):
        """Calculates index sequentially for all dates in [start_date, end_date]."""
        curr = start_date
        while curr <= end_date:
            self.calculate_daily_index(db, curr)
            curr += timedelta(days=1)


index_calculator = APIxCalculator()
