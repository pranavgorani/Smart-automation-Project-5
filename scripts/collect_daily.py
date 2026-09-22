#!/usr/bin/env python3
"""
CLI script: Executes a single daily airfare collection run.
"""

import sys
from pathlib import Path
from datetime import date

root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal
from backend.app.ingestion.collector import collector
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    target = date.today()
    print(f"Executing daily airfare collection for {target}...")
    db = SessionLocal()
    try:
        res = collector.run_collection(db, target_date=target)
        print(f"Collection complete: {res}")
    finally:
        db.close()
