"""
Data Cleaning & Validation Engine.
Applies strict schema validation, range checks, currency validation,
and airport code checks.
"""

from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger("airfare_x.cleaner")

VALID_AIRPORTS = {"DEL", "BOM", "BLR", "CCU", "HYD", "MAA", "GOI"}
VALID_CURRENCIES = {"INR", "USD", "EUR", "GBP"}


class DataCleaner:
    def __init__(self):
        self.validation_errors: List[str] = []

    def validate_quote(self, quote: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates individual airfare quote fields.
        Returns (is_valid, list_of_errors).
        """
        errors = []

        # Required fields check
        required_fields = [
            "origin", "destination", "airline", "departure_date", "total_fare"
        ]
        for field in required_fields:
            if field not in quote or quote[field] is None:
                errors.append(f"Missing mandatory field '{field}'")

        if errors:
            return False, errors

        # Airport code validation
        origin = str(quote.get("origin", "")).upper()
        dest = str(quote.get("destination", "")).upper()
        if origin not in VALID_AIRPORTS:
            errors.append(f"Invalid or untracked origin airport code: {origin}")
        if dest not in VALID_AIRPORTS:
            errors.append(f"Invalid or untracked destination airport code: {dest}")
        if origin == dest:
            errors.append(f"Origin and destination cannot be identical ({origin})")

        # Fare numeric and sanity range check
        try:
            total_fare = float(quote.get("total_fare", 0.0))
            if total_fare <= 500.0:
                errors.append(f"Unrealistically low total fare (< 500 INR): {total_fare}")
            elif total_fare > 150000.0:
                errors.append(f"Unrealistically excessive domestic total fare (> 150k INR): {total_fare}")
        except (ValueError, TypeError):
            errors.append(f"Non-numeric total fare: {quote.get('total_fare')}")

        # Currency validation
        currency = str(quote.get("currency", "INR")).upper()
        if currency not in VALID_CURRENCIES:
            errors.append(f"Unsupported currency: {currency}")

        # Departure date validation
        dep_date_str = str(quote.get("departure_date", ""))
        try:
            dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Invalid departure date format (expected YYYY-MM-DD): {dep_date_str}")

        # Advance purchase days sanity
        adv_days = quote.get("advance_purchase_days")
        if adv_days is not None:
            try:
                adv_int = int(adv_days)
                if adv_int < 0 or adv_int > 365:
                    errors.append(f"Advance purchase days out of reasonable range (0-365): {adv_int}")
            except (ValueError, TypeError):
                errors.append(f"Invalid advance purchase days: {adv_days}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def clean_batch(self, quotes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Cleans a list of raw quotes.
        Returns (valid_quotes, rejected_quotes_with_reason).
        """
        valid = []
        rejected = []
        for q in quotes:
            is_valid, errs = self.validate_quote(q)
            if is_valid:
                # Sanitize text
                q_clean = dict(q)
                q_clean["origin"] = str(q_clean["origin"]).upper().strip()
                q_clean["destination"] = str(q_clean["destination"]).upper().strip()
                q_clean["route"] = f"{q_clean['origin']}-{q_clean['destination']}"
                q_clean["currency"] = str(q_clean.get("currency", "INR")).upper().strip()
                valid.append(q_clean)
            else:
                rejected.append({"quote": q, "errors": errs})

        logger.info(f"Cleaner processed {len(quotes)} quotes: {len(valid)} valid, {len(rejected)} rejected.")
        return valid, rejected


cleaner = DataCleaner()
