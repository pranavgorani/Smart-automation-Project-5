"""
Unit tests for Data Quality Scoring.
"""

from backend.app.processing.quality import quality_scorer


def test_quote_quality_scoring_perfect():
    quote = {
        "flight_number": "6E-101",
        "departure_time": "08:00",
        "arrival_time": "10:15",
        "base_fare": 4000.0,
        "taxes": 700.0,
        "user_development_fee": 350.0,
        "convenience_fee": 350.0,
        "other_charges": 0.0,
        "total_fare": 5400.0,
        "is_outlier": False,
    }
    score = quality_scorer.evaluate_quote(quote)
    assert score == 100.0


def test_quote_quality_scoring_deductions():
    quote = {
        "flight_number": None,  # -5
        "departure_time": "08:00",
        "arrival_time": "10:15",
        "base_fare": 4000.0,
        "taxes": 0.0,
        "user_development_fee": 0.0,
        "convenience_fee": 0.0,
        "other_charges": 0.0,
        "total_fare": 8000.0,  # Inconsistent sum: -15
        "is_outlier": True,    # -10
    }
    score = quality_scorer.evaluate_quote(quote)
    assert score <= 70.0


def test_batch_quality_composite():
    metrics = quality_scorer.calculate_batch_metrics(
        raw_count=1000,
        valid_count=980,
        rejected_count=20,
        duplicate_count=10,
        outlier_count=15,
        quotes=[],
        source_name="Test Source",
    )
    score = metrics["quality_score"]
    assert 90.0 <= score <= 100.0
    assert metrics["completeness_score"] == 98.0
