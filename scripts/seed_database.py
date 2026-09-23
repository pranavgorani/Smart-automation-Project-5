#!/usr/bin/env python3
"""
Seed Database Script for AIRINDEX INDIA / AIRFARE-X.
Populates standard routes, airlines, sources, DGCA reference data,
and runs the baseline bootstrap.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal, init_db
from backend.app.db.seed import seed_routes, seed_airlines, seed_sources, seed_dgca_reference
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("airindex.seed")

if __name__ == "__main__":
    print("================================================================")
    print("AIRINDEX INDIA: Seeding Core Reference Database")
    print("================================================================")
    init_db()
    db = SessionLocal()
    try:
        logger.info("Seeding routes...")
        seed_routes(db)
        logger.info("Seeding airlines...")
        seed_airlines(db)
        logger.info("Seeding data sources...")
        seed_sources(db)
        logger.info("Seeding DGCA reference benchmarks...")
        seed_dgca_reference(db)
        print("Database schema and core reference records seeded successfully.")
    finally:
        db.close()
