#!/usr/bin/env python3
"""
Generate Demo Data Script for AIRINDEX INDIA / AIRFARE-X.
Generates 10,000+ realistic synthetic airfare quotes across 30 days,
cleans, normalizes, detects outliers, and computes daily index history.
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
    print("AIRINDEX INDIA: Generating Synthetic Demo Dataset (10,000+ Observations)")
    print("================================================================")
    db = SessionLocal()
    try:
        res = run_full_seed(db)
        print("Demo dataset generation and chronological index calculation completed.")
        print(f"Summary: {res}")
    finally:
        db.close()
