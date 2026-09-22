# Deployment & Operations Guide

## 1. Prerequisites

- **Python:** 3.10, 3.11, or 3.12+ (tested and verified on 3.11 and 3.14).
- **Node.js:** v18+ with `npm` (required only if building the React frontend from source; the repository comes with pre-compiled distribution assets in `frontend/dist`).
- **Docker & Docker Compose:** (Optional, for containerized deployments).
- **Git**

---

## 2. Quickstart: Local Zero-Config Setup (Under 2 Minutes)

AIRFARE-X is architected with a default `DEMO_MODE=true` mode and embedded SQLite fallback, requiring **zero cloud credentials or external API keys** to run immediately.

### Step 1: Clone and Set Up Virtual Environment
```bash
# Clone the repository
git clone <repository_url>
cd "Smart automation Project 5"

# Create and activate Python virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Seed Demo Database (10,000+ Observations)
```bash
python scripts/seed_demo.py
```
*This populates `airfare_x.db` with 13 trunk routes, 6 airlines, 11,512 quotes, and 30 days of pre-calculated APIx index values.*

### Step 4: Run the Backend & Web App
```bash
# Start FastAPI server (serves REST API on port 8000 and the compiled React SPA)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
- **Web Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 3. Launching the Streamlit Financial Terminal

If you prefer the MoSPI-styled Python Streamlit dashboard:
```bash
streamlit run streamlit/app.py --server.port 8501
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 4. Docker & Docker Compose Deployment

To run the complete production stack (PostgreSQL 15 database + FastAPI Backend + Streamlit Terminal):

```bash
# Build and start all services
docker compose up --build -d

# Check running containers
docker compose ps

# View backend logs
docker compose logs -f backend
```

Services exposed:
- **FastAPI Backend & React SPA:** `http://localhost:8000`
- **Streamlit Terminal:** `http://localhost:8501`
- **PostgreSQL Database:** `localhost:5432` (user: `postgres`, password: `postgres`, db: `airfarex`)

To seed the PostgreSQL database inside Docker:
```bash
docker compose exec backend python scripts/seed_demo.py
```

To shut down:
```bash
docker compose down -v
```

---

## 5. Development Mode (Hot Reloading Frontend)

If you wish to modify React / TypeScript components in real-time:
```bash
cd frontend
npm install
npm run dev
```
The Vite development server will run at [http://localhost:5173](http://localhost:5173) with automatic proxying to backend `http://localhost:8000`.

To recompile the production frontend build:
```bash
npm run build
```
*(Build artifacts are saved to `frontend/dist/` and automatically served by FastAPI).*

---

## 6. Environment Variables Reference

Create a `.env` file in the root directory (or copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_MODE` | `true` | When `true`, uses synthetic engine with zero credentials |
| `DATABASE_URL` | `sqlite:///airfare_x.db` | PostgreSQL URL or SQLite local path |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SECRET_KEY` | `dev-secret-key-change-in-prod` | Application secret key |
| `AMADEUS_CLIENT_ID` | `""` | Optional Amadeus GDS API client ID |
| `AMADEUS_CLIENT_SECRET` | `""` | Optional Amadeus GDS API client secret |
| `SERPAPI_KEY` | `""` | Optional SerpApi Google Flights API key |
| `RATE_LIMIT_DELAY_SECONDS` | `1.5` | Politeness delay between ethical web scraper requests |
| `CORS_ORIGINS` | `*` | Allowed CORS origins for REST API |
