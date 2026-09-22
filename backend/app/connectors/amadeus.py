"""
Amadeus Flight Offers Search API Connector.
Uses official OAuth2 Client Credentials flow against test/production endpoint.
"""

from typing import List, Dict, Any, Optional
import httpx
import time
import logging
from datetime import datetime
from backend.app.config import settings
from backend.app.connectors.base import BaseConnector

logger = logging.getLogger("airfare_x.amadeus")


class AmadeusConnector(BaseConnector):
    def __init__(self):
        super().__init__(
            name="Amadeus Flight Offers Search",
            source_type="LIVE_API",
            rate_limit_seconds=float(settings.DEFAULT_RATE_LIMIT_SECONDS)
        )
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.base_url = settings.AMADEUS_BASE_URL.rstrip("/")
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0.0

    def is_available(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_access_token(self) -> Optional[str]:
        """Obtains or reuses a valid OAuth2 bearer token from Amadeus."""
        if not self.is_available():
            return None

        # Return cached token if valid with 60s buffer
        if self.access_token and time.time() < (self.token_expiry - 60):
            return self.access_token

        token_url = f"{self.base_url}/v1/security/oauth2/token"
        try:
            self.enforce_rate_limit()
            response = httpx.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 1799)
            self.token_expiry = time.time() + expires_in
            logger.info("Successfully acquired Amadeus OAuth2 token.")
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to obtain Amadeus token: {e}")
            return None

    def search_flights(
        self, origin: str, destination: str, departure_date: str, adults: int = 1
    ) -> List[Dict[str, Any]]:
        """Invokes Amadeus Flight Offers Search v2 endpoint."""
        token = self.get_access_token()
        if not token:
            return []

        search_url = f"{self.base_url}/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": "INR",
            "max": 15,
        }
        headers = {"Authorization": f"Bearer {token}"}

        # Exponential backoff retry loop (1s, 2s, 4s)
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.enforce_rate_limit()
                response = httpx.get(
                    search_url, params=params, headers=headers, timeout=12.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                elif response.status_code == 429:
                    sleep_time = 2 ** attempt
                    logger.warning(f"Amadeus rate limit hit (429). Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Amadeus search returned status {response.status_code}: {response.text}")
                    break
            except Exception as e:
                logger.warning(f"Amadeus search error (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)

        return []

    def normalize_amadeus_result(
        self, raw_offer: Dict[str, Any], origin: str, destination: str, departure_date: str, advance_days: int
    ) -> Optional[Dict[str, Any]]:
        """Maps an Amadeus offer into the standardized airfare quote schema."""
        try:
            itineraries = raw_offer.get("itineraries", [])
            if not itineraries:
                return None
            segments = itineraries[0].get("segments", [])
            if not segments:
                return None

            first_segment = segments[0]
            last_segment = segments[-1]
            carrier_code = first_segment.get("carrierCode", "AI")
            flight_number = f"{carrier_code}{first_segment.get('number', '')}"

            # Airline mapping
            airline_map = {
                "6E": "IndiGo",
                "AI": "Air India",
                "IX": "Air India Express",
                "QP": "Akasa Air",
                "SG": "SpiceJet",
                "9I": "Alliance Air",
                "UK": "Air India",  # Vistara merged with Air India
            }
            airline_name = airline_map.get(carrier_code, f"Carrier {carrier_code}")

            price_info = raw_offer.get("price", {})
            total_fare = float(price_info.get("grandTotal") or price_info.get("total", 0.0))
            base_fare = float(price_info.get("base", total_fare * 0.82))
            taxes_total = total_fare - base_fare

            # Estimated decomposition of taxes based on Indian civil aviation structure
            udf = round(taxes_total * 0.35, 2)
            convenience = 350.0
            other_taxes = round(max(0.0, taxes_total - udf - convenience), 2)

            dep_dt = first_segment.get("departure", {}).get("at", "")
            arr_dt = last_segment.get("arrival", {}).get("at", "")
            dep_time = dep_dt.split("T")[1][:5] if "T" in dep_dt else "08:00"
            arr_time = arr_dt.split("T")[1][:5] if "T" in arr_dt else "10:15"

            return {
                "source": self.name,
                "source_type": self.source_type,
                "source_reference": raw_offer.get("id", ""),
                "origin": origin,
                "destination": destination,
                "route": f"{origin}-{destination}",
                "airline": airline_name,
                "flight_number": flight_number,
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
                "total_fare": total_fare,
                "currency": price_info.get("currency", "INR"),
                "availability": raw_offer.get("numberOfBookableSeats", 9),
                "stops": len(segments) - 1,
                "refundability": "Non-refundable",
            }
        except Exception as e:
            logger.error(f"Error normalizing Amadeus quote: {e}")
            return None

    def fetch_quotes(
        self, origin: str, destination: str, departure_date: str, advance_days: int
    ) -> List[Dict[str, Any]]:
        raw_offers = self.search_flights(origin, destination, departure_date)
        quotes = []
        for offer in raw_offers:
            normalized = self.normalize_amadeus_result(
                offer, origin, destination, departure_date, advance_days
            )
            if normalized:
                quotes.append(normalized)
        return quotes
