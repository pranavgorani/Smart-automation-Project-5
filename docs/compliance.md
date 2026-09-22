# Ethical Scraping, Compliance & Statutory Data Governance

## 1. Compliance Charter & Core Principles

AIRFARE-X is built strictly in accordance with official public-sector data collection ethics and legal compliance frameworks suitable for the **Ministry of Statistics and Programme Implementation (MoSPI)** and Government of India regulatory guidelines.

### Zero-Tolerance Policies
1. **NO Anti-Bot Evasion:** AIRFARE-X does not employ fingerprint spoofing, TLS fingerprint impersonation, browser header obfuscation, or residential proxy rotation designed to circumvent bot detection mechanisms.
2. **NO CAPTCHA Solving:** The platform contains **zero** automated CAPTCHA bypassing logic, optical OCR solvers, or third-party CAPTCHA solving API integrations. If an endpoint presents a CAPTCHA challenge, the platform terminates the request session immediately, logs a compliance warning, and falls back to official open/permitted APIs.
3. **NO Unauthorized Access:** All web ingestion targets are restricted to publicly available quote search endpoints where access is legally permitted.
4. **NO Private or Personal Data (PII):** The platform solely extracts publicly quoted flight ticket prices, flight numbers, and schedule times. No user data, booking accounts, or passenger identifiers are ever accessed or stored.

---

## 2. Automated `robots.txt` Conformance

The ingestion subsystem enforces programmatic compliance via `backend/app/ingestion/compliance.py`:

```
                 +-----------------------------+
                 |  Target Domain / Airline    |
                 +--------------+--------------+
                                |
                                v
                 +-----------------------------+
                 | Fetch and Parse robots.txt  |
                 +--------------+--------------+
                                |
                  [ Is User-Agent Permitted? ]
                       /               \
                    YES                 NO
                     /                   \
                    v                     v
+-----------------------+     +-----------------------------+
| Check Crawl-Delay &   |     | Hard Block Request          |
| Apply Rate Limiter    |     | Log Statutory Denial Record |
| Execute Polite Fetch  |     | Fallback to Alternative API |
+-----------------------+     +-----------------------------+
```

### Standard MoSPI User-Agent Header
When operating in production mode, all outbound requests identify themselves transparently:
```http
User-Agent: MoSPI-AirfareX-Bot/1.0 (+https://www.mospi.gov.in/diid; research-airfare-index@mospi.gov.in)
```
This enables airline webmasters and infrastructure engineers to verify the origin and legitimacy of research crawls and reach out directly if needed.

---

## 3. Rate Limiting & Politeness Policies

To ensure zero operational impact on civil aviation booking infrastructures:
- **Token Bucket Rate Limiting:** Outbound requests are governed by a token bucket algorithm enforcing a minimum inter-request delay (default: `1.5 seconds`, configurable up to 5.0 seconds).
- **Concurrency Restrictions:** Maximum 1 active worker per domain at any instant.
- **Off-Peak Execution:** Scheduled automated crawls are scheduled during off-peak Indian travel hours (02:00 UTC / 07:30 IST) when domestic airline server load is at its daily minimum.
- **Backoff & Jitter:** Upon receiving HTTP `429 (Too Many Requests)` or `503 (Service Unavailable)`, the crawler backs off exponentially with randomized jitter ($T_{\text{wait}} = 2^k + \text{rand}(0, 1)$ seconds) and suspends queries for that domain if errors persist.

---

## 4. Multi-Source Redundancy & Provenance Architecture

To prevent reliance on any single web scraping source, AIRFARE-X implements a tiered source fallback structure:

1. **Tier 1 (Official GDS APIs):** Licensed enterprise APIs (Amadeus, Sabre) providing direct, authorized access to global distribution system seat availability.
2. **Tier 2 (Authorized Travel Aggregator APIs):** SerpApi / Google Flights API structured data feeds.
3. **Tier 3 (Permitted Public Web Portals):** Direct Playwright headless browser crawls with strict `robots.txt` enforcement.
4. **Tier 4 (Manual Batch Ingestion):** Official CSV / Excel uploads from airline submissions or DGCA data dumps.
5. **Tier 5 (Deterministic Synthetic Generator):** In offline or demo environments (`DEMO_MODE=true`), the system generates high-fidelity synthetic market quotes modeled after real Indian civil aviation yield curves.

---

## 5. Auditability & Data Provenance

For any statistical index utilized in official government economic policy or CPI augmentation, provenance is legally mandatory:
- **SHA-256 Observation Fingerprint:** Every collected fare quote receives an immutable hash generated from its constituent attributes.
- **Collection Run Telemetry:** Each batch is recorded with source URL, HTTP status codes, latency, record counts, and timestamps.
- **Immutable Log Retention:** Quality scores and outlier audit logs are preserved in perpetuity for retrospective verification by National Statistical Commission (NSC) auditors.
