#!/usr/bin/env python3
"""
CLI script: Executes 30-day prototype backtest against DGCA reference series.
"""

import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal
from backend.app.index.backtest import backtest_engine
import json

if __name__ == "__main__":
    print("Running 30-day prototype backtest...")
    db = SessionLocal()
    try:
        res = backtest_engine.run_backtest(db, days=30)
        print(json.dumps(res, indent=2))
    finally:
        db.close()
