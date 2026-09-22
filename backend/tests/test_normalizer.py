"""
Unit tests for Fare Normalization and Component Decomposition.
"""

import pytest
from backend.app.processing.normalizer import normalizer


def test_normalize_quote_decomposition():
    quote = {
        "origin": "del",
        "destination": "bom",
        "airline": "indigo",
        "total_fare": 6500.0,
        "currency": "INR",
    }
    norm = normalizer.normalize_quote(quote)

    assert norm["origin"] == "DEL"
    assert norm["destination"] == "BOM"
    assert norm["route"] == "DEL-BOM"
    assert norm["airline"] == "IndiGo"
    assert norm["currency"] == "INR"
    assert norm["total_fare"] == 6500.0

    # Total must equal sum of base + taxes + udf + convenience + other
    calc_sum = (
        norm["base_fare"]
        + norm["taxes"]
        + norm["user_development_fee"]
        + norm["convenience_fee"]
        + norm["other_charges"]
    )
    assert abs(calc_sum - 6500.0) < 0.05


def test_foreign_currency_conversion():
    quote = {
        "origin": "DEL",
        "destination": "BLR",
        "airline": "Air India",
        "total_fare": 100.0,
        "currency": "USD",
    }
    norm = normalizer.normalize_quote(quote)

    # 100 USD at 86.5 INR/USD should be 8650 INR
    assert norm["currency"] == "INR"
    assert norm["total_fare"] == 8650.0
    assert norm["base_fare"] > 6000.0
