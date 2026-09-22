"""
Unit tests for Outlier Detection (IQR & MAD).
"""

import numpy as np
from backend.app.processing.outlier import outlier_detector


def test_iqr_outlier_detection():
    # Normal fares around 4000-6000, with one extreme spike at 35000
    fares = np.array([4200.0, 4500.0, 4600.0, 4800.0, 5000.0, 5200.0, 5500.0, 35000.0])
    mask, lower, upper = outlier_detector.detect_iqr(fares)

    # The 35000 fare must be flagged as outlier
    assert mask[-1] == True
    # The normal fares must not be flagged
    assert sum(mask[:-1]) == 0
    assert upper < 35000.0


def test_mad_outlier_detection():
    fares = np.array([4000.0, 4100.0, 4050.0, 4150.0, 4200.0, 4080.0, 32000.0])
    mask, scale = outlier_detector.detect_mad(fares)

    assert mask[-1] == True
    assert sum(mask[:-1]) == 0


def test_flag_outliers_preserves_records():
    quotes = [
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 4500.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 4700.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 4800.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 5000.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 52000.0},  # Outlier
    ]
    flagged, count = outlier_detector.flag_outliers(quotes)

    # Crucial: records are tagged, never deleted
    assert len(flagged) == 5
    assert count == 1
    assert flagged[-1]["is_outlier"] == True
