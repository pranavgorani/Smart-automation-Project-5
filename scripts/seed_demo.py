#!/usr/bin/env python3
"""
Seed script: Populates database with routes, airlines, DGCA benchmarks,
and 10,000+ realistic synthetic quotes across 30 days.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal
from backend.app.db.seed import run_full_seed
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    print("================================================================")
    print("AIRFARE-X INDIA: Initializing & Seeding Synthetic Airfare Data")
    print("================================================================")
    db = SessionLocal()
    try:
        res = run_full_seed(db)
        print(f"Seed Success: {res}")
    finally:
        db.close()
