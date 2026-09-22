# REST API Reference & Integration Guide

The AIRFARE-X REST API is built on FastAPI, offering asynchronous performance, strict schema validation via Pydantic v2, and auto-generated interactive OpenAPI docs at `/docs` and `/redoc`.

Base URL: `http://localhost:8000` (or configured production host).

---

## 1. System & Telemetry Endpoints

### `GET /api/health`
Returns system health, database connection status, and record count.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "demo_mode": true,
  "database": "sqlite:///airfare_x.db",
  "routes_count": 13,
  "quotes_count": 11512,
  "latest_index": 108.45
}
```

### `GET /api/info`
Returns platform metadata, version, and MoSPI statistical parameters.

---

## 2. Routes & City Pairs

### `GET /api/routes`
Retrieves all 13 monitored trunk domestic routes with MoSPI passenger weights.

**Response:**
```json
[
  {
    "route_code": "DEL-BOM",
    "origin": "DEL",
    "origin_city": "Delhi",
    "destination": "BOM",
    "destination_city": "Mumbai",
    "distance_km": 1148,
    "category": "Metro-Metro",
    "weight": 0.145,
    "is_active": true
  }
]
```

### `GET /api/routes/{route_code}`
Returns route details and historical summary for a specific city-pair.

---

## 3. Airfare Quotes

### `GET /api/flights`
Query normalized airfare observations.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_code` | string | `null` | Filter by route (e.g., `DEL-BOM`) |
| `airline_code`| string | `null` | Filter by airline (e.g., `6E`, `AI`) |
| `advance_window` | int | `null` | Filter by booking horizon (`1`, `7`, `15`, `30`, `45`) |
| `is_outlier` | bool | `null` | Filter outlier status |
| `limit` | int | `100` | Pagination limit (max 1000) |
| `offset` | int | `0` | Pagination offset |

**Sample Quote Item:**
```json
{
  "id": 1042,
  "route_code": "DEL-BOM",
  "airline_code": "6E",
  "flight_number": "6E-205",
  "departure_datetime": "2026-09-23T06:00:00",
  "advance_window_days": 1,
  "base_fare": 7450.0,
  "fuel_surcharge": 800.0,
  "udf_psf": 650.0,
  "taxes": 450.0,
  "convenience_fee": 300.0,
  "total_fare": 9650.0,
  "currency": "INR",
  "is_outlier": false,
  "fingerprint": "a3b9..."
}
```

---

## 4. Statistical Airfare Price Index (APIx)

### `GET /api/index/latest`
Returns the most recent composite APIx and advance window sub-indices.

**Response:**
```json
{
  "date": "2026-09-22",
  "composite_index": 108.45,
  "pct_change_1d": 0.42,
  "pct_change_7d": 1.85,
  "base_period": "2026-01-01 = 100.00",
  "advance_windows": {
    "T_1": 128.60,
    "T_7": 114.20,
    "T_15": 106.30,
    "T_30": 98.40,
    "T_45": 94.75
  },
  "total_quotes_sampled": 390
}
```

### `GET /api/index/daily`
Historical time-series of composite and sub-window indices.

**Query Parameters:**
- `start_date` (ISO date, e.g. `2026-08-01`)
- `end_date` (ISO date, e.g. `2026-09-22`)

### `GET /api/index/by-route`
Returns route-level price relatives and indices for the latest or specified date.

### `GET /api/index/methodology`
Returns the machine-readable statistical specification of the Laspeyres aggregation.

### `GET /api/index/export/csv`
Streams the complete index series as a clean RFC 4180 CSV file for external econometric modeling.

### `GET /api/index/export/json`
Exports the entire statistical dataset with calculation metadata.

---

## 5. Analytics & Econometric Intelligence

### `GET /api/analytics/elasticity`
Returns advance purchase price elasticity ($\epsilon$), surge multipliers, and average fare curves by advance booking horizon.

**Response:**
```json
{
  "overall_elasticity": -0.342,
  "overall_surge_multiplier": 1.78,
  "windows": [
    {"advance_days": 1, "avg_fare": 8420.0, "label": "T+1 (Emergency)"},
    {"advance_days": 7, "avg_fare": 6980.0, "label": "T+7 (Short-Notice)"},
    {"advance_days": 15, "avg_fare": 5840.0, "label": "T+15 (Standard)"},
    {"advance_days": 30, "avg_fare": 5120.0, "label": "T+30 (Planned)"},
    {"advance_days": 45, "avg_fare": 4730.0, "label": "T+45 (Early Bird)"}
  ]
}
```

### `GET /api/analytics/airlines`
Yield and average fare breakdown across carriers (IndiGo, Air India, SpiceJet, Akasa, etc.).

### `GET /api/analytics/anomalies`
Identifies statistically significant fare spikes, surge multiplier anomalies, and provides grounded econometric briefings formatted for MoSPI policymakers.

### `GET /api/analytics/backtest`
Performs dynamic cross-validation of APIx against official DGCA passenger yield benchmarks.
Returns:
- Pearson correlation coefficient ($r$)
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- Directional Accuracy (%)

---

## 6. Sources & Quality Auditing

### `GET /api/sources`
Telemetry of active data connectors (Amadeus, SerpApi, Permitted Web, Mock) with rate limits and operational status.

### `GET /api/sources/quality`
Returns the 5-dimension Data Quality Score (DQS) breakdown (Completeness, Validity, Timeliness, Uniqueness, Consistency) across recent ingestion runs.

---

## 7. Administrative & Pipeline Execution

### `POST /api/admin/trigger-collection`
Manually triggers an ingestion run across all active routes and advance windows.

### `POST /api/admin/recalculate-index`
Forces recalculation of the Laspeyres index over a specified date range.

### `POST /api/admin/reset-demo`
Re-initializes the embedded SQLite database and re-seeds it with 10,000+ deterministic synthetic quotes and 30 days of pre-computed indices.
