"""
Route Weight Management for APIx.
Ensures normalized route weights (sum = 1.0) and supports loading official
or experimental weights from CSV / Database.
"""

from typing import Dict
from pathlib import Path
import pandas as pd
import logging
from backend.app.config import ROOT_DIR

logger = logging.getLogger("airfare_x.weights")

DEFAULT_WEIGHTS = {
    "DEL-BOM": 0.15,
    "DEL-BLR": 0.13,
    "BOM-BLR": 0.10,
    "DEL-CCU": 0.08,
    "BLR-HYD": 0.08,
    "MAA-DEL": 0.08,
    "BOM-DEL": 0.07,
    "BLR-DEL": 0.07,
    "HYD-DEL": 0.06,
    "CCU-DEL": 0.05,
    "BOM-GOI": 0.05,
    "DEL-GOI": 0.04,
    "BLR-GOI": 0.04,
}


class WeightManager:
    def __init__(self):
        self.weights: Dict[str, float] = self.load_weights()

    def load_weights(self) -> Dict[str, float]:
        """Loads weights from data/weights.csv if present, else uses defaults."""
        csv_path = ROOT_DIR / "data" / "weights.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                w_dict = dict(zip(df["route"].str.strip(), df["weight"].astype(float)))
                return self.normalize(w_dict)
            except Exception as e:
                logger.warning(f"Could not load weights.csv: {e}. Falling back to default.")

        return self.normalize(DEFAULT_WEIGHTS)

    @staticmethod
    def normalize(weights_dict: Dict[str, float]) -> Dict[str, float]:
        """Normalizes dictionary values to strictly sum to 1.0."""
        total = sum(weights_dict.values())
        if total <= 0:
            count = len(weights_dict)
            return {k: round(1.0 / count, 4) for k in weights_dict}
        return {k: round(v / total, 4) for k, v in weights_dict.items()}

    def get_route_weight(self, route: str) -> float:
        return self.weights.get(route, 0.05)


weight_manager = WeightManager()
