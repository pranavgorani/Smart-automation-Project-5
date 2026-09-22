"""
CSV / Manual Ingestion Connector.
Supports uploading CSV files for fallback airfare data or DGCA reference data.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import io
import logging
from datetime import datetime
from backend.app.connectors.base import BaseConnector

logger = logging.getLogger("airfare_x.csv_connector")


class CSVConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="CSV Ingestion Fallback",
            source_type="CSV_IMPORT",
            rate_limit_seconds=0.0
        )

    def is_available(self) -> bool:
        return True

    def fetch_quotes(
        self, origin: str, destination: str, departure_date: str, advance_days: int
    ) -> List[Dict[str, Any]]:
        # Not applicable for live query
        return []

    def parse_quotes_csv(self, file_content: bytes, filename: str = "upload.csv") -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parses an uploaded CSV file containing flight quotes.
        Returns (valid_quotes, errors).
        """
        quotes: List[Dict[str, Any]] = []
        errors: List[str] = []

        try:
            df = pd.read_csv(io.BytesIO(file_content))
            required_cols = {"origin", "destination", "airline", "departure_date", "total_fare"}
            missing = required_cols - set(df.columns)
            if missing:
                errors.append(f"Missing required columns: {missing}")
                return quotes, errors

            for idx, row in df.iterrows():
                try:
                    origin = str(row["origin"]).strip().upper()
                    dest = str(row["destination"]).strip().upper()
                    airline = str(row["airline"]).strip()
                    dep_date = str(row["departure_date"]).strip()
                    total_fare = float(row["total_fare"])
                    
                    base_fare = float(row.get("base_fare", total_fare * 0.82))
                    taxes = float(row.get("taxes", total_fare - base_fare))
                    udf = float(row.get("user_development_fee", taxes * 0.35))
                    conv = float(row.get("convenience_fee", 350.0))
                    adv_days = int(row.get("advance_purchase_days", 7))
                    flight_num = str(row.get("flight_number", f"{origin[:2]}{idx+100}"))

                    quotes.append({
                        "source": f"CSV_IMPORT ({filename})",
                        "source_type": self.source_type,
                        "source_reference": f"csv_{filename}_{idx}",
                        "origin": origin,
                        "destination": dest,
                        "route": f"{origin}-{dest}",
                        "airline": airline,
                        "flight_number": flight_num,
                        "departure_date": dep_date,
                        "departure_time": str(row.get("departure_time", "09:00")),
                        "arrival_time": str(row.get("arrival_time", "11:15")),
                        "search_timestamp": datetime.utcnow().isoformat(),
                        "advance_purchase_days": adv_days,
                        "fare_class": str(row.get("fare_class", "Economy")),
                        "fare_family": str(row.get("fare_family", "Standard")),
                        "base_fare": base_fare,
                        "taxes": taxes,
                        "user_development_fee": udf,
                        "convenience_fee": conv,
                        "other_charges": 0.0,
                        "total_fare": total_fare,
                        "currency": str(row.get("currency", "INR")),
                        "availability": int(row.get("availability", 9)),
                        "stops": int(row.get("stops", 0)),
                        "refundability": str(row.get("refundability", "Non-refundable")),
                    })
                except Exception as row_err:
                    errors.append(f"Row {idx+1} error: {row_err}")

        except Exception as e:
            errors.append(f"CSV read error: {e}")

        return quotes, errors

    def parse_dgca_csv(self, file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parses DGCA monthly benchmark data CSV."""
        records: List[Dict[str, Any]] = []
        errors: List[str] = []

        try:
            df = pd.read_csv(io.BytesIO(file_content))
            required = {"month", "route", "airline", "passengers", "average_fare"}
            missing = required - set(df.columns)
            if missing:
                errors.append(f"Missing DGCA columns: {missing}")
                return records, errors

            for idx, row in df.iterrows():
                try:
                    records.append({
                        "month": str(row["month"]).strip(),
                        "route": str(row["route"]).strip().upper(),
                        "airline": str(row["airline"]).strip(),
                        "passengers": int(row["passengers"]),
                        "average_fare": float(row["average_fare"]),
                        "fuel_surcharge": float(row.get("fuel_surcharge", 0.0)),
                        "source": str(row.get("source", "DGCA_UPLOAD")),
                    })
                except Exception as rerr:
                    errors.append(f"Row {idx+1} invalid: {rerr}")

        except Exception as e:
            errors.append(f"DGCA CSV read error: {e}")

        return records, errors
