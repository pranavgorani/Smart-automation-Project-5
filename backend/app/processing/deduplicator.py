"""
Deduplication Engine.
Generates deterministic SHA-256 fingerprint hashes for each raw observation
to detect and filter duplicate airfare quotes.
"""

import hashlib
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("airfare_x.deduplicator")


class Deduplicator:
    @staticmethod
    def compute_hash(quote: Dict[str, Any]) -> str:
        """
        Generates SHA-256 fingerprint from core attributes:
        source, route, airline, flight_number, departure_date, departure_time, advance_days, total_fare.
        """
        key_fields = [
            str(quote.get("source", "")).strip().lower(),
            str(quote.get("route", "")).strip().upper(),
            str(quote.get("airline", "")).strip().lower(),
            str(quote.get("flight_number", "")).strip().upper(),
            str(quote.get("departure_date", "")).strip(),
            str(quote.get("departure_time", "")).strip(),
            str(quote.get("advance_purchase_days", "")).strip(),
            f"{float(quote.get('total_fare', 0.0)):.2f}",
        ]
        raw_key = "|".join(key_fields)
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def deduplicate(
        self, quotes: List[Dict[str, Any]], existing_hashes: set = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Filters duplicate quotes based on SHA-256 hash.
        Returns (unique_quotes, duplicate_count).
        """
        if existing_hashes is None:
            existing_hashes = set()

        seen_hashes = set(existing_hashes)
        unique_quotes: List[Dict[str, Any]] = []
        duplicate_count = 0

        for q in quotes:
            q_hash = self.compute_hash(q)
            q["raw_hash"] = q_hash
            if q_hash in seen_hashes:
                duplicate_count += 1
            else:
                seen_hashes.add(q_hash)
                unique_quotes.append(q)

        logger.info(
            f"Deduplication completed: {len(unique_quotes)} unique, {duplicate_count} duplicates identified."
        )
        return unique_quotes, duplicate_count


deduplicator = Deduplicator()
