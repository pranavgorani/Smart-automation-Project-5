"""
Integration and API endpoint tests for AIRFARE-X INDIA.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "AIRFARE-X INDIA"
    assert "documentation_url" in data


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("OPERATIONAL", "DEGRADED")
    assert "connectors" in data
    assert "database" in data


def test_index_current_endpoint():
    response = client.get("/api/index/current")
    assert response.status_code == 200
    data = response.json()
    assert data["index_code"] == "APIx"
    assert "value" in data
    assert "daily_change_pct" in data
    assert "routes" in data


def test_index_history_endpoint():
    response = client.get("/api/index/history?days=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "index_value" in data[0]


def test_routes_endpoint():
    response = client.get("/api/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 13
    route_codes = [r["route_code"] for r in data]
    assert "DEL-BOM" in route_codes
    assert "DEL-BLR" in route_codes


def test_airlines_endpoint():
    response = client.get("/api/airlines")
    assert response.status_code == 200
    data = response.json()
    names = [a["name"] for a in data]
    assert "IndiGo" in names
    assert "Air India" in names


def test_flights_endpoint():
    response = client.get("/api/flights?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


def test_lead_time_analytics():
    response = client.get("/api/analytics/lead-time")
    assert response.status_code == 200
    data = response.json()
    assert "curve" in data
    assert "empirical_elasticity" in data


def test_airline_analytics():
    response = client.get("/api/analytics/airlines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_heatmap_analytics():
    response = client.get("/api/analytics/heatmap?timeframe=daily")
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data


def test_executive_summary():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "headline" in data
    assert "takeaways" in data


def test_sources_endpoint():
    response = client.get("/api/sources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4


def test_quality_endpoint():
    response = client.get("/api/quality")
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data


def test_backtest_endpoint():
    response = client.get("/api/backtest?days=15")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "series" in data


def test_methodology_endpoint():
    response = client.get("/api/methodology")
    assert response.status_code == 200
    data = response.json()
    assert "mathematical_framework" in data
