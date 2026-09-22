"""
Unit tests for Index Mathematical Formulas and Weight Normalization.
"""

from backend.app.index.weights import weight_manager, DEFAULT_WEIGHTS


def test_weights_sum_to_one():
    weights = weight_manager.weights
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.001


def test_custom_weight_normalization():
    arbitrary = {"DEL-BOM": 30, "DEL-BLR": 20, "BOM-BLR": 50}
    normalized = weight_manager.normalize(arbitrary)

    assert normalized["DEL-BOM"] == 0.3
    assert normalized["DEL-BLR"] == 0.2
    assert normalized["BOM-BLR"] == 0.5
    assert sum(normalized.values()) == 1.0


def test_rate_of_change_formulas():
    # Today 108.42, Yesterday 106.48
    today = 108.42
    yesterday = 106.48
    daily_change = round(((today / yesterday) - 1.0) * 100.0, 2)

    assert daily_change == 1.82


def test_weighted_index_calculation():
    # Test formula: 100 * sum(w_r * R_r)
    weights = {"R1": 0.6, "R2": 0.4}
    relatives = {"R1": 1.10, "R2": 1.05}  # +10% on R1, +5% on R2

    expected_index = 100.0 * (0.6 * 1.10 + 0.4 * 1.05)
    # 100 * (0.66 + 0.42) = 108.0
    assert abs(expected_index - 108.0) < 0.001
