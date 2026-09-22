"""
SerpAPI Google Flights Connector.
Retrieves real-time Google Flights search results via SerpAPI's official engine.
"""

from typing import List, Dict, Any, Optional
import httpx
import time
import logging
from datetime import datetime
from backend.app.config import settings
from backend.app.connectors.base import BaseConnector

logger = logging.getLogger("airfare_x.serpapi")


class SerpAPIConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="SerpAPI Google Flights",
            source_type="LIVE_API",
            rate_limit_seconds=float(settings.DEFAULT_RATE_LIMIT_SECONDS)
        )
        self.api_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search.json"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    def search_google_flights(
        self, origin: str, destination: str, departure_date: str
    ) -> List[Dict[str, Any]]:
        """Queries SerpAPI with engine=google_flights."""
        if not self.is_available():
            return []

        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "currency": "INR",
            "hl": "en",
            "api_key": self.api_key,
        }

        for attempt in range(settings.MAX_RETRIES):
            try:
                self.enforce_rate_limit()
                response = httpx.get(self.base_url, params=params, timeout=15.0)
                if response.status_code == 200:
                    data = response.json()
                    best_flights = data.get("best_flights", [])
                    other_flights = data.get("other_flights", [])
                    return best_flights + other_flights
                elif response.status_code == 429:
                    sleep_time = 2 ** attempt
                    logger.warning(f"SerpAPI rate limit (429). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"SerpAPI returned status {response.status_code}: {response.text}")
                    break
            except Exception as e:
                logger.warning(f"SerpAPI search error (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)

        return []

    def normalize_serpapi_result(
        self, raw_flight: Dict[str, Any], origin: str, destination: str, departure_date: str, advance_days: int
    ) -> Optional[Dict[str, Any]]:
        """Maps a SerpAPI Google Flights entry to the standardized schema."""
        try:
            flights = raw_flight.get("flights", [])
            if not flights:
                return None

            first_leg = flights[0]
            airline_name = first_leg.get("airline", "IndiGo")
            flight_num = first_leg.get("flight_number", "6E-101")
            
            # Extract price
            price = raw_flight.get("price", 0.0)
            if isinstance(price, str):
                price = float(price.replace("₹", "").replace(",", "").strip())
            else:
                price = float(price)

            if price <= 0:
                return None

            base_fare = round(price * 0.82, 2)
            taxes_total = round(price - base_fare, 2)
            udf = round(taxes_total * 0.35, 2)
            convenience = 350.0
            other_taxes = round(max(0.0, taxes_total - udf - convenience), 2)

            dep_time = first_leg.get("departure_airport", {}).get("time", "07:30")
            arr_time = first_leg.get("arrival_airport", {}).get("time", "09:45")

            return {
                "source": self.name,
                "source_type": self.source_type,
                "source_reference": f"serpapi_{origin}_{destination}_{departure_date}_{flight_num}",
                "origin": origin,
                "destination": destination,
                "route": f"{origin}-{destination}",
                "airline": airline_name,
                "flight_number": flight_num,
                "departure_date": departure_date,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "search_timestamp": datetime.utcnow().isoformat(),
                "advance_purchase_days": advance_days,
                "fare_class": "Economy",
                "fare_family": "Standard",
                "base_fare": base_fare,
                "taxes": other_taxes,
                "user_development_fee": udf,
                "convenience_fee": convenience,
                "other_charges": 0.0,
                "total_fare": price,
                "currency": "INR",
                "availability": 9,
                "stops": len(flights) - 1,
                "refundability": "Non-refundable",
            }
        except Exception as e:
            logger.error(f"Error normalizing SerpAPI quote: {e}")
            return None

    def fetch_quotes(
        self, origin: str, destination: str, departure_date: str, advance_days: int
    ) -> List[Dict[str, Any]]:
        raw_flights = self.search_google_flights(origin, destination, departure_date)
        quotes = []
        for f in raw_flights:
            norm = self.normalize_serpapi_result(f, origin, destination, departure_date, advance_days)
            if norm:
                quotes.append(norm)
        return quotes
