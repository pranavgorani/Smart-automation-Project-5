"""
Statistical Outlier Detection Engine.
Implements:
1. IQR (Interquartile Range)
2. MAD (Median Absolute Deviation)
3. Configurable Percentile Trimming
Crucially, records are flagged rather than deleted to ensure complete statistical auditability.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import logging
from backend.app.config import settings

logger = logging.getLogger("airfare_x.outlier")


class OutlierDetector:
    def __init__(self, method: str = None, iqr_multiplier: float = None):
        self.method = method or settings.OUTLIER_METHOD
        self.iqr_multiplier = iqr_multiplier or settings.OUTLIER_IQR_MULTIPLIER

    def detect_iqr(self, fares: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Computes IQR bounds: [Q1 - 1.5*IQR, Q3 + 1.5*IQR].
        Returns (is_outlier_bool_mask, lower_bound, upper_bound).
        """
        if len(fares) < 4:
            return np.zeros(len(fares), dtype=bool), 0.0, float("inf")

        q25, q75 = np.percentile(fares, [25, 75])
        iqr = q75 - q25
        lower = max(1000.0, q25 - (self.iqr_multiplier * iqr))
        upper = q75 + (self.iqr_multiplier * iqr)
        is_outlier = (fares < lower) | (fares > upper)
        return is_outlier, float(lower), float(upper)

    def detect_mad(self, fares: np.ndarray, threshold: float = 3.0) -> Tuple[np.ndarray, float]:
        """
        Computes Median Absolute Deviation (MAD) modified z-scores.
        """
        if len(fares) < 4:
            return np.zeros(len(fares), dtype=bool), 0.0

        median = np.median(fares)
        diff = np.abs(fares - median)
        mad = np.median(diff)
        if mad == 0:
            mad = 1.0  # Prevent division by zero

        # Modified z-score
        mod_z = 0.6745 * diff / mad
        is_outlier = mod_z > threshold
        return is_outlier, float(mad)

    def flag_outliers(
        self, quotes: List[Dict[str, Any]], method: str = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Groups quotes by (route, advance_purchase_days) and flags statistical outliers.
        Returns (quotes_with_flags, outlier_count).
        """
        if not quotes:
            return [], 0

        selected_method = method or self.method
        # Group quotes by route & advance window
        groups: Dict[Tuple[str, int], List[int]] = {}
        for idx, q in enumerate(quotes):
            key = (q.get("route", ""), int(q.get("advance_purchase_days", 7)))
            groups.setdefault(key, []).append(idx)

        total_outliers = 0

        for key, indices in groups.items():
            if len(indices) < 4:
                # Insufficient sample size for robust distribution metrics
                for i in indices:
                    quotes[i].setdefault("is_outlier", False)
                    quotes[i].setdefault("outlier_method", selected_method)
                    quotes[i].setdefault("outlier_score", 1.0)
                continue

            fares = np.array([float(quotes[i]["total_fare"]) for i in indices])

            if selected_method == "MAD":
                mask, scale = self.detect_mad(fares)
                for local_i, idx in enumerate(indices):
                    is_out = bool(mask[local_i])
                    quotes[idx]["is_outlier"] = is_out
                    quotes[idx]["outlier_method"] = "MAD"
                    quotes[idx]["outlier_score"] = round(float(abs(fares[local_i] - np.median(fares)) / (scale or 1.0)), 2)
                    if is_out:
                        total_outliers += 1
            else:
                # Default IQR
                mask, lower, upper = self.detect_iqr(fares)
                for local_i, idx in enumerate(indices):
                    is_out = bool(mask[local_i])
                    quotes[idx]["is_outlier"] = is_out
                    quotes[idx]["outlier_method"] = "IQR"
                    quotes[idx]["outlier_score"] = round(float(fares[local_i] / (upper or 1.0)), 2)
                    if is_out:
                        total_outliers += 1

        logger.info(
            f"Outlier detection ({selected_method}) completed: {total_outliers} outliers flagged out of {len(quotes)} quotes."
        )
        return quotes, total_outliers


outlier_detector = OutlierDetector()
