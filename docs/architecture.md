# System Architecture & Technical Specification

## 1. Executive Summary

**AIRFARE-X INDIA** is an automated, production-ready, real-time airfare price index platform designed specifically for the **Ministry of Statistics and Programme Implementation (MoSPI)** and its **Data Informatics & Innovation Division (DIID)**.

Traditional official statistical indices (such as CPI Sub-group 7.3: Transport and Communication) rely on monthly or quarterly manual price quotations. In dynamic pricing environments like Indian civil aviation, ticket prices fluctuate minute-by-minute across advance booking windows ($T+1, T+7, T+15, T+30, T+45$). AIRFARE-X captures these fluctuations systematically to generate an **Experimental Real-time Airfare Price Index (APIx)** with daily cadence, econometric elasticity metrics, multi-source provenance, and automated audit trails.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            DATA COLLECTION LAYER                                  |
|                                                                                   |
|  +---------------------+  +---------------------+  +---------------------------+  |
|  |   Amadeus GDS API   |  | Google Flights API  |  | Permitted Web Scraper     |  |
|  |  (OAuth2 REST API)  |  |     (SerpApi)       |  | (Playwright + robots.txt) |  |
|  +----------+----------+  +----------+----------+  +-------------+-------------+  |
|             |                        |                           |                |
|  +----------+------------------------+---------------------------+-------------+  |
|  | Mock / Synthetic Engine (10,000+ deterministic quotes with seasonal cycles)  |  |
|  +-----------------------------------+-----------------------------------------+  |
+--------------------------------------|--------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                         INGESTION & ETHICAL COMPLIANCE                            |
|                                                                                   |
|  * Robots.txt Parser & Enforcer        * Domain Rate Limiter (Token Bucket)       |
|  * Legal / MoSPI User-Agent Header     * Collection Run Telemetry & Logging       |
+--------------------------------------|--------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                        PROCESSING & QUALITY ENGINE                                |
|                                                                                   |
|  * Fare Decomposition (Base, Fuel, User Dev Fee, Airport Taxes, Convenience Fee)  |
|  * SHA-256 Deduplication (Route + Airline + FlightNum + DeptDate + BookingDate)  |
|  * Non-Destructive Outlier Flagging (IQR & MAD 3.0x Thresholds)                  |
|  * 5-Dimension Data Quality Scoring (Completeness, Validity, Timeliness, etc.)   |
+--------------------------------------|--------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                        STORAGE LAYER (DUAL-ENGINE)                                |
|                                                                                   |
|  * Production: PostgreSQL 15+ / Supabase with TimescaleDB Hypertable support      |
|  * Zero-Config Fallback: Embedded SQLite (`airfare_x.db`)                         |
|  * Pre-populated with 13 trunk routes, 6 major carriers, 30 days of daily quotes  |
+--------------------------------------|--------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                   STATISTICAL INDEX & ANALYTICS ENGINE                            |
|                                                                                   |
|  * Laspeyres Route-Level & National Aggregation (Fixed Base: 2026-01-01 = 100.0)  |
|  * Advance Window Stratification (T+1, T+7, T+15, T+30, T+45)                     |
|  * Lead-Time Price Elasticity & Surge Multiplier Calculation                      |
|  * 30-Day DGCA Backtesting Engine (MAE, RMSE, MAPE, Pearson r, Directional Acc)  |
|  * Grounded Rule-Based AI Anomaly Attribution & MoSPI Briefing Generator          |
+--------------------------------------|--------------------------------------------+
                                       |
                    +------------------+------------------+
                    |                                     |
                    v                                     v
+-----------------------------------+ +---------------------------------------------+
|        REST API (FastAPI)         | |       PRESENTATION LAYER                    |
|                                   | |                                             |
| * OpenAPI / Swagger Specification | | * React + TypeScript + Vite Dashboard       |
| * Health & Telemetry Endpoints    | |   (Lucide icons, Glassmorphism, SVG charts) |
| * Route, Index & Analytics APIs   | | * Streamlit Financial Terminal Dashboard    |
| * Dynamic CSV / JSON Export Engine| |   (Multi-tab, Plotly interactive graphics)  |
+-----------------------------------+ +---------------------------------------------+
```

---

## 3. Data Pipeline Lifecycle

### Phase 1: Ingestion & Orchestration
1. **Trigger:** Pipeline runs on a configurable cron schedule (`APScheduler` in backend or GitHub Actions at 02:00 UTC daily).
2. **Matrix Generation:** For each active route (13 routes) and each advance purchase window ($T+1, T+7, T+15, T+30, T+45$), queries are generated.
3. **Connector Dispatch:**
   - In production with keys: queries Amadeus or SerpApi.
   - In ethical web mode: verifies `robots.txt` compliance before dispatching Playwright requests with rate limiting.
   - In zero-credentials demo mode: invokes `MockConnector`, which applies a deterministic pricing formula factoring route distance, airline tier, advance window decay, day-of-week surges, and seasonal fuel fluctuations.

### Phase 2: Cleaning & Normalization
1. **Currency Normalization:** All fares converted to Indian Rupee (INR).
2. **Fare Unbundling:** Deconstructs ticket price into civil aviation standard components:
   $$\text{Total Fare} = \text{Base Fare} + \text{Fuel Surcharge} + \text{UDF/PSF} + \text{CGST/SGST} + \text{Convenience Fee}$$
3. **Deduplication:** Computes an immutable SHA-256 fingerprint from:
   $$\text{Hash} = \text{SHA256}(\text{origin} + \text{dest} + \text{airline} + \text{flight\_num} + \text{dep\_time} + \text{quote\_date} + \text{dep\_date})$$
   Duplicate quotes within the same collection run are rejected.

### Phase 3: Outlier Detection
Prices are evaluated within route-and-window cohorts using two statistical fences:
- **Tukey's Interquartile Range (IQR):**
  $$[\text{IQR}_{\text{lower}}, \text{IQR}_{\text{upper}}] = [Q_1 - 1.5 \times \text{IQR},\; Q_3 + 1.5 \times \text{IQR}]$$
- **Median Absolute Deviation (MAD):**
  $$\text{MAD} = \text{median}(|x_i - \tilde{x}|), \quad Z_{\text{MAD}} = \frac{0.6745 \times |x_i - \tilde{x}|}{\text{MAD}}$$
Values exceeding $Z_{\text{MAD}} > 3.0$ or falling outside Tukey's fences are flagged as `is_outlier = True` with audit rationale. Crucially, outliers are **non-destructively retained** for auditability.

### Phase 4: Data Quality Scoring
Every observation batch receives an objective 0–100 Data Quality Score (DQS) across 5 weighted dimensions:
- **Completeness ($w=0.25$):** Ratio of non-null mandatory fields.
- **Validity ($w=0.20$):** Adherence to bounds ($₹1,000 \le \text{fare} \le ₹100,000$, valid IATA codes).
- **Timeliness ($w=0.20$):** Collection timestamp vs departure timestamp latency.
- **Uniqueness ($w=0.20$):** Proportion of non-duplicate fingerprints.
- **Consistency ($w=0.15$):** Fare sum reconciliation ($\sum \text{components} \approx \text{total}$).

---

## 4. Database Schema Specification

The relational schema is defined in [backend/app/db/schema.sql](file:///c:/Users/Pranav/OneDrive/Documents/Projects/Smart%20automation%20Project%205/backend/app/db/schema.sql) and mapped via SQLAlchemy ORM:

- **`routes`**: Origin, destination, distance (km), route classification (Metro-Metro, Metro-NonMetro, Tier-2), and national MoSPI passenger weight.
- **`airlines`**: Carrier name, 2-letter IATA code, business model (LCC vs FSC), and domestic market share.
- **`sources`**: Ingestion source type (gds_api, aggregator_api, permitted_scraper, mock), domain, and rate limits.
- **`collection_runs`**: Execution status, timestamps, total records fetched, valid records, and error messages.
- **`airfare_quotes`**: Granular quote entity including route ID, airline ID, flight number, departure datetime, advance purchase days ($T+N$), price breakdown (base, tax, total), outlier flags, and SHA-256 fingerprint.
- **`index_values`**: Daily aggregate index values (composite APIx, advance window indices, base period, sample size).
- **`route_indices`**: Daily route-specific price relatives and Laspeyres indices.
- **`data_quality_logs`**: Daily batch dimensional quality audits.
- **`dgca_reference_records`**: Official DGCA monthly domestic yield and passenger traffic statistics for empirical backtesting.
