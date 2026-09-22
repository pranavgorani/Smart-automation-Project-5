"""
Base connector interface with rate-limiting, exponential backoff,
and common error handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import asyncio
import logging

logger = logging.getLogger("airfare_x.connectors")


class BaseConnector(ABC):
    """Abstract base class for all airfare data connectors."""

    def __init__(self, name: str, source_type: str, rate_limit_seconds: float = 2.0):
        self.name = name
        self.source_type = source_type
        self.rate_limit_seconds = rate_limit_seconds
        self.last_request_time = 0.0

    def enforce_rate_limit(self):
        """Enforces respectful request intervals according to compliance specifications."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_seconds:
            sleep_time = self.rate_limit_seconds - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    async def async_enforce_rate_limit(self):
        """Async version of respectful rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_seconds:
            sleep_time = self.rate_limit_seconds - elapsed
            await asyncio.sleep(sleep_time)
        self.last_request_time = time.time()

    @abstractmethod
    def fetch_quotes(
        self, origin: str, destination: str, departure_date: str, advance_days: int
    ) -> List[Dict[str, Any]]:
        """Fetch quotes for a specific origin-destination pair and departure date."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if connector credentials and dependencies are properly configured."""
        pass
