"""
Fare Normalization & Component Decomposition Engine.
Decomposes total consumer price into official civil aviation components:
base_fare + taxes + user_development_fee + convenience_fee + other_charges = total_fare.
Normalizes airline naming conventions and currency.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger("airfare_x.normalizer")

# FX Conversion rates to INR
FX_RATES = {
    "INR": 1.0,
    "USD": 86.5,
    "EUR": 93.2,
    "GBP": 109.4,
}

AIRLINE_CANONICAL_MAP = {
    "indigo": "IndiGo",
    "6e": "IndiGo",
    "interglobe": "IndiGo",
    "air india": "Air India",
    "ai": "Air India",
    "air india express": "Air India Express",
    "ix": "Air India Express",
    "akasa": "Akasa Air",
    "akasa air": "Akasa Air",
    "qp": "Akasa Air",
    "spicejet": "SpiceJet",
    "sg": "SpiceJet",
    "alliance": "Alliance Air",
    "alliance air": "Alliance Air",
    "9i": "Alliance Air",
    "vistara": "Air India",
    "uk": "Air India",
}


class FareNormalizer:
    def normalize_quote(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes an individual quote, ensuring fare decomposition and canonical types."""
        norm = dict(quote)

        # 1. Airline Canonicalization
        raw_airline = str(norm.get("airline", "")).strip().lower()
        norm["airline"] = AIRLINE_CANONICAL_MAP.get(raw_airline, norm.get("airline", "IndiGo"))

        # 2. Currency Standardization
        currency = str(norm.get("currency", "INR")).upper()
        rate = FX_RATES.get(currency, 1.0)

        total_fare_raw = float(norm.get("total_fare", 0.0))
        total_fare_inr = round(total_fare_raw * rate, 2)
        norm["total_fare"] = total_fare_inr

        # 3. Fare Decomposition
        # If base_fare was provided in foreign currency, scale it
        base_raw = float(norm.get("base_fare", total_fare_raw * 0.78))
        base_fare = round(base_raw * rate, 2)
        norm["base_fare"] = base_fare

        # Taxes and mandatory fees
        taxes_raw = float(norm.get("taxes", 0.0))
        udf_raw = float(norm.get("user_development_fee", 0.0))
        conv_raw = float(norm.get("convenience_fee", 350.0))
        other_raw = float(norm.get("other_charges", 0.0))

        taxes = round(taxes_raw * rate, 2)
        udf = round(udf_raw * rate, 2)
        conv = round(conv_raw * rate, 2)
        other = round(other_raw * rate, 2)

        # Balance check: base + taxes + udf + conv + other = total_fare
        sum_components = base_fare + taxes + udf + conv + other
        discrepancy = round(total_fare_inr - sum_components, 2)
        if abs(discrepancy) > 0.01:
            # Adjust taxes component to balance total without silently changing total_fare
            taxes = round(max(0.0, taxes + discrepancy), 2)

        norm["taxes"] = taxes
        norm["user_development_fee"] = udf
        norm["convenience_fee"] = conv
        norm["other_charges"] = other
        norm["currency"] = "INR"

        # 4. Route code and airport codes
        origin = str(norm.get("origin", "")).upper()
        destination = str(norm.get("destination", "")).upper()
        norm["origin"] = origin
        norm["destination"] = destination
        norm["route"] = f"{origin}-{destination}"

        return norm

    def normalize_batch(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.normalize_quote(q) for q in quotes]


normalizer = FareNormalizer()
