"""
Methodology Documentation Engine for MoSPI / DIID.
Defines formal statistical specifications, aggregation formulas,
and governance principles for the Experimental Real-time Airfare Price Index (APIx).
"""

from typing import Dict, Any


def get_methodology_spec() -> Dict[str, Any]:
    return {
        "title": "Experimental Real-time Airfare Price Index (APIx) Methodology",
        "organization": "Ministry of Statistics and Programme Implementation (MoSPI)",
        "department": "Data Informatics & Innovation Division (DIID)",
        "theme": "Smart Automation - High-Frequency Price Intelligence",
        "version": "1.0",
        "status": "EXPERIMENTAL_RESEARCH_PROTOTYPE",
        "disclaimer": (
            "This index is an experimental research prototype intended to explore the feasibility "
            "of augmenting the official Consumer Price Index (CPI) Transport/Airfare subgroup with high-frequency "
            "automated web-scraped data. It does NOT constitute official Government of India CPI statistics."
        ),
        "mathematical_framework": {
            "elementary_aggregate": {
                "description": "Route-level price aggregate across observed flight quotes for day t and advance-window d.",
                "formula": "P(r, d, t) = Median_{i in Q(r, d, t)} [ TotalFare_i ]",
                "properties": "Median is preferred over arithmetic mean to withstand dynamic pricing skewness."
            },
            "route_composite_price": {
                "description": "Weighted average of advance-purchase windows for route r on day t.",
                "formula": "P(r, t) = Sum_{d in {1,7,15,30,45}} [ w_d * P(r, d, t) ]",
                "default_window_weights": {
                    "T+1": 0.20,
                    "T+7": 0.30,
                    "T+15": 0.25,
                    "T+30": 0.15,
                    "T+45": 0.10
                }
            },
            "price_relative": {
                "description": "Price relative comparing current route median to base period price.",
                "formula": "R(r, t) = P(r, t) / P(r, base)",
                "base_period": "2026-01-01 (Base Index = 100.0)"
            },
            "index_aggregation": {
                "description": "Laspeyres-type weighted basket aggregation across all domestic trunk routes.",
                "formula": "APIx(t) = 100 * Sum_{r in Routes} [ w_r * R(r, t) ]",
                "constraint": "Sum_{r} [ w_r ] = 1.0"
            },
            "rate_of_change_metrics": {
                "daily_change": "((APIx_t / APIx_{t-1}) - 1) * 100",
                "weekly_change": "((APIx_t / APIx_{t-7}) - 1) * 100",
                "monthly_change": "((APIx_t / APIx_{t-30}) - 1) * 100"
            }
        },
        "advance_purchase_windows": [
            {"window": "T+1", "lead_days": 1, "description": "Last-minute business & emergency demand"},
            {"window": "T+7", "lead_days": 7, "description": "Short-horizon planned commercial travel"},
            {"window": "T+15", "lead_days": 15, "description": "Standard domestic leisure & personal travel"},
            {"window": "T+30", "lead_days": 30, "description": "Early booking baseline fare"},
            {"window": "T+45", "lead_days": 45, "description": "Advance promotional & holiday planning"}
        ],
        "data_provenance_and_integrity": [
            "Source attribution: Every record tagged with LIVE_API, PERMITTED_WEB, MOCK, or CSV_IMPORT.",
            "SHA-256 fingerprinting for duplicate prevention.",
            "Decomposed consumer fare: base_fare + taxes + UDF + convenience_fee = total_fare.",
            "Non-destructive outlier tagging via IQR and MAD."
        ]
    }
