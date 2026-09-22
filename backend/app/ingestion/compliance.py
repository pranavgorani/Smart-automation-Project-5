"""
Compliance and Ethical Safeguards Engine.
Ensures zero unauthorized scraping, robots.txt compliance,
rate limiting, and transparent data provenance.
"""

from typing import Dict, Any, Optional
import urllib.robotparser
import urllib.parse
import logging
from backend.app.config import settings

logger = logging.getLogger("airfare_x.compliance")


class ComplianceOfficer:
    def __init__(self):
        self.user_agent = "AirfareX-MoSPI-Bot/1.0"
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.disallowed_domains = [
            # Explicit blacklist of unauthorized aggregators
            "makemytrip.com",
            "easemytrip.com",
            "yatra.com",
            "cleartrip.com",
            "goibibo.com"
        ]

    def is_domain_allowed(self, url: str) -> bool:
        """Verifies domain is not on the ethical exclusion list."""
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        for d in self.disallowed_domains:
            if d in domain:
                logger.warning(f"Compliance block: Access to {domain} without commercial API contract is restricted.")
                return False
        return True

    def check_robots(self, target_url: str) -> bool:
        """Validates robots.txt rules before any HTTP call."""
        if not self.is_domain_allowed(target_url):
            return False

        try:
            parsed = urllib.parse.urlparse(target_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.parsers:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                rp.read()
                self.parsers[base_url] = rp

            return self.parsers[base_url].can_fetch(self.user_agent, target_url)
        except Exception as e:
            logger.error(f"Failed to check robots.txt: {e}")
            return False


compliance_officer = ComplianceOfficer()
