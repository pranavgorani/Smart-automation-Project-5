#!/usr/bin/env python3
"""
CLI script: Computes or recalculates APIx daily index.
"""

import sys
from pathlib import Path
from datetime import date

root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal
from backend.app.index.calculator import index_calculator
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    target = date.today()
    print(f"Calculating APIx index for {target}...")
    db = SessionLocal()
    try:
        res = index_calculator.calculate_daily_index(db, target_date=target)
        print(f"Calculation complete: {res}")
    finally:
        db.close()
