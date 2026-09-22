"""
Realistic Deterministic Synthetic Airfare Generator.
Crucial for reproducible hackathon demonstrations, statistical back-testing,
and MoSPI/DIID algorithmic validation without external API dependency.
"""

from typing import List, Dict, Any
import numpy as np
from datetime import datetime, timedelta, date
import logging
from backend.app.connectors.base import BaseConnector

logger = logging.getLogger("airfare_x.mock_connector")


class MockConnector(BaseConnector):
    def __init__(self, seed: int = 42):
        super().__init__(
            name="AIRFARE-X Synthetic Generator",
            source_type="MOCK",
            rate_limit_seconds=0.0
        )
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # Baseline distance and economy price reference (INR)
        self.route_benchmarks = {
            "DEL-BOM": {"base": 4200, "dist_km": 1148, "type": "Metro"},
            "DEL-BLR": {"base": 4600, "dist_km": 1740, "type": "Metro"},
            "BOM-BLR": {"base": 3400, "dist_km": 842, "type": "Metro"},
            "DEL-CCU": {"base": 4100, "dist_km": 1305, "type": "Metro"},
            "BLR-HYD": {"base": 2600, "dist_km": 500, "type": "Metro"},
            "MAA-DEL": {"base": 4500, "dist_km": 1760, "type": "Metro"},
            "BOM-DEL": {"base": 4150, "dist_km": 1148, "type": "Metro"},
            "BLR-DEL": {"base": 4550, "dist_km": 1740, "type": "Metro"},
            "HYD-DEL": {"base": 3800, "dist_km": 1253, "type": "Metro"},
            "CCU-DEL": {"base": 4050, "dist_km": 1305, "type": "Metro"},
            "BOM-GOI": {"base": 2900, "dist_km": 435, "type": "Leisure"},
            "DEL-GOI": {"base": 5100, "dist_km": 1515, "type": "Leisure"},
            "BLR-GOI": {"base": 2700, "dist_km": 480, "type": "Leisure"},
        }

        # Airline positioning & price factor
        self.airline_profiles = {
            "IndiGo": {"multiplier": 1.00, "flights_per_day": 5, "code": "6E"},
            "Air India": {"multiplier": 1.10, "flights_per_day": 4, "code": "AI"},
            "Air India Express": {"multiplier": 0.94, "flights_per_day": 2, "code": "IX"},
            "Akasa Air": {"multiplier": 0.95, "flights_per_day": 3, "code": "QP"},
            "SpiceJet": {"multiplier": 0.92, "flights_per_day": 2, "code": "SG"},
            "Alliance Air": {"multiplier": 1.05, "flights_per_day": 1, "code": "9I"},
        }

        # Advance booking windows and price multiplier (T+1 highest, T+45 lowest)
        self.advance_windows = {
            1: {"multiplier": 1.55, "volatility": 0.15},
            7: {"multiplier": 1.25, "volatility": 0.10},
            15: {"multiplier": 1.05, "volatility": 0.08},
            30: {"multiplier": 0.90, "volatility": 0.05},
            45: {"multiplier": 0.82, "volatility": 0.04},
        }

    def is_available(self) -> bool:
        return True

    def _get_festival_multiplier(self, dt: date) -> float:
        """Simulates national holiday / festival season travel surges (Diwali, Holi, New Year, etc.)."""
        # Holi (mid-March), Republic Day (Jan 26), Independence (Aug 15), Diwali/Oct peak
        month, day = dt.month, dt.day
        if month == 1 and 24 <= day <= 28:
            return 1.22
        if month == 3 and 10 <= day <= 16:
            return 1.28
        if month == 8 and 13 <= day <= 17:
            return 1.18
        if month == 10 and 15 <= day <= 26:
            return 1.35
        if month == 12 and 22 <= day <= 31:
            return 1.38
        return 1.0

    def generate_quote(
        self,
        route: str,
        airline: str,
        search_date: date,
        advance_days: int,
        flight_idx: int = 1,
    ) -> Dict[str, Any]:
        """Generates an individual realistic airfare quote."""
        dep_date = search_date + timedelta(days=advance_days)
        origin, dest = route.split("-")
        bench = self.route_benchmarks.get(route, {"base": 4000, "type": "Metro"})
        profile = self.airline_profiles[airline]
        adv_info = self.advance_windows.get(advance_days, {"multiplier": 1.0, "volatility": 0.08})

        # Multipliers
        base_route_price = bench["base"]
        advance_mult = adv_info["multiplier"]
        
        # Day of week multiplier (Friday & Sunday are higher; Tuesday & Wednesday are lower)
        weekday = dep_date.weekday()
        if weekday in (4, 6):  # Fri, Sun
            weekday_mult = 1.18 if bench["type"] == "Leisure" else 1.12
        elif weekday in (1, 2):  # Tue, Wed
            weekday_mult = 0.92
        else:
            weekday_mult = 1.00

        fest_mult = self._get_festival_multiplier(dep_date)
        airline_mult = profile["multiplier"]

        # Random noise (standard log-normal variation around 1.0)
        noise = self.rng.normal(1.0, adv_info["volatility"])

        # Rare outlier injection (0.5% chance of sudden fare spike or price error)
        is_outlier = False
        outlier_reason = None
        if self.rng.random() < 0.008:
            spike_factor = self.rng.choice([2.4, 2.8, 0.45])
            noise *= spike_factor
            is_outlier = True
            outlier_reason = "Spike" if spike_factor > 1 else "FloorDrop"

        # Calculate consumer total fare
        total_fare_val = (
            base_route_price
            * advance_mult
            * weekday_mult
            * airline_mult
            * fest_mult
            * noise
        )
        total_fare = max(1800.0, round(float(total_fare_val), 2))

        # Civil Aviation Fare Breakdown Decomposition
        base_fare = round(total_fare * 0.78, 2)
        taxes_total = round(total_fare - base_fare, 2)
        udf = round(min(850.0, max(280.0, bench.get("dist_km", 1000) * 0.22)), 2)
        conv = 350.0
        other_taxes = max(0.0, round(taxes_total - udf - conv, 2))

        dep_hour = 6 + (flight_idx * 3) % 16
        dep_min = self.rng.choice([0, 15, 30, 45])
        dep_time = f"{dep_hour:02d}:{dep_min:02d}"
        arr_hour = (dep_hour + 2) % 24
        arr_time = f"{arr_hour:02d}:{(dep_min + 15) % 60:02d}"

        flight_number = f"{profile['code']}-{100 + flight_idx * 15 + (weekday * 3)}"

        # Search timestamp
        search_ts = datetime.combine(search_date, datetime.min.time()) + timedelta(
            hours=int(self.rng.integers(6, 22)),
            minutes=int(self.rng.integers(0, 59)),
        )

        return {
            "source": self.name,
            "source_type": self.source_type,
            "source_reference": f"mock_{route}_{airline}_{dep_date}_{flight_number}_{advance_days}",
            "origin": origin,
            "destination": dest,
            "route": route,
            "airline": airline,
            "flight_number": flight_number,
            "departure_date": dep_date.isoformat(),
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "search_timestamp": search_ts.isoformat(),
            "advance_purchase_days": advance_days,
            "fare_class": "Economy",
            "fare_family": "Standard",
            "base_fare": base_fare,
            "taxes": other_taxes,
            "user_development_fee": udf,
            "convenience_fee": conv,
            "other_charges": 0.0,
            "total_fare": total_fare,
            "currency": "INR",
            "availability": int(self.rng.integers(1, 12)),
            "stops": 0,
            "refundability": "Non-refundable",
            "is_outlier": is_outlier,
            "outlier_method": "Synthetic_Outlier" if is_outlier else None,
            "outlier_score": round(noise, 2) if is_outlier else 1.0,
        }

    def generate_full_dataset(
        self, days: int = 30, end_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Generates 10,000+ realistic quotes across 30 days, 13 routes,
        5 advance windows, and 6 domestic airlines.
        """
        if end_date is None:
            end_date = date(2026, 3, 22)
        start_date = end_date - timedelta(days=days - 1)

        quotes: List[Dict[str, Any]] = []
        routes = list(self.route_benchmarks.keys())
        airlines = list(self.airline_profiles.keys())
        windows = [1, 7, 15, 30, 45]

        logger.info(
            f"Generating synthetic dataset: {days} days from {start_date} to {end_date} across {len(routes)} routes..."
        )

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)

            for route in routes:
                for window in windows:
                    # Select airlines serving this route
                    for airline in airlines:
                        # Regional airlines do not fly every route
                        if airline == "Alliance Air" and "GOI" not in route:
                            continue
                        
                        num_flights = 1
                        if airline in ("IndiGo", "Air India"):
                            num_flights = 2 if window in (1, 7) else 1

                        for f_idx in range(num_flights):
                            # 2% chance flight is fully sold out / unavailable
                            if self.rng.random() < 0.02:
                                continue

                            q = self.generate_quote(
                                route=route,
                                airline=airline,
                                search_date=current_date,
                                advance_days=window,
                                flight_idx=f_idx + 1,
                            )
                            quotes.append(q)

        logger.info(f"Generated {len(quotes)} synthetic airfare observations.")
        return quotes

    def fetch_quotes(
        self, origin: str, destination: str, departure_date: str, advance_days: int
    ) -> List[Dict[str, Any]]:
        route = f"{origin}-{destination}"
        dep_d = datetime.strptime(departure_date, "%Y-%m-%d").date()
        search_d = dep_d - timedelta(days=advance_days)
        quotes = []
        for airline in self.airline_profiles.keys():
            if airline == "Alliance Air" and "GOI" not in route:
                continue
            quotes.append(
                self.generate_quote(route, airline, search_d, advance_days, flight_idx=1)
            )
        return quotes
