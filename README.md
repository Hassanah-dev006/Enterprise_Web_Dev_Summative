# NYC Taxi Trip Explorer

Fullstack dashboard for exploring urban mobility patterns in the NYC Yellow Taxi dataset (January 2019, ~7.7M trips).

**Stack:** Python ETL → PostgreSQL → Flask API → vanilla JS dashboard (Chart.js + Leaflet)

> 📹 **Video walkthrough:** _[add link here]_

## Project structure

```
├── data/                  # Raw data (not in git) + ETL outputs
├── db/
│   └── schema.sql         # Normalized schema + indexes
├── etl/                   # Cleaning / feature-engineering / load pipeline
│   ├── config.py          # Paths, DB URL, cleaning thresholds
│   ├── clean.py           # Data integrity rules + exclusion logging
│   ├── features.py        # Derived features (duration, speed, fare/mile, tip %)
│   ├── zones.py           # Shapefile → GeoJSON (EPSG:2263 → WGS84)
│   ├── load.py            # Bulk COPY into PostgreSQL
│   └── run_pipeline.py    # Entry point: python -m etl.run_pipeline
├── backend/
│   ├── app.py             # Flask API + static frontend server
│   ├── db.py              # Connection helper
│   └── algorithms/        # Hand-written quicksort + top-K min-heap (no libraries)
├── frontend/              # Dashboard (HTML/CSS/JS, Chart.js, Leaflet)
└── docs/                  # Technical report
```

## Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally

### 2. Install
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # edit DATABASE_URL if needed
```

### 3. Data
Download the raw files into `data/` (see `data/README.md` for links):
- `yellow_tripdata_2019-01.parquet`
- `taxi_zone_lookup.csv`
- `taxi_zones.zip`

### 4. Create database and run ETL
```bash
createdb nyc_taxi
psql -d nyc_taxi -f db/schema.sql
python -m etl.run_pipeline        # cleans, engineers features, loads DB (~7.7M rows)
```
The pipeline writes an exclusion log to `data/exclusion_log.csv` and a summary to `data/etl_summary.json`.

### 5. Launch
```bash
python -m backend.app
```
Open **http://localhost:5001** — the Flask app serves both the API and the dashboard.

## API overview

| Endpoint | Description |
|---|---|
| `GET /api/health` | Liveness + row count |
| `GET /api/zones` | Zone lookup + GeoJSON boundaries |
| `GET /api/trips` | Paginated trips; filters: date, hour, borough, fare, distance; sortable |
| `GET /api/stats/summary` | KPI totals (trips, revenue, avg distance/fare/tip) |
| `GET /api/stats/hourly` | Trips/avg fare by hour of day |
| `GET /api/stats/top-zones?k=10` | Busiest zones — ranked with **custom top-K heap** |

## Custom algorithm (assignment §3)

`backend/algorithms/` contains hand-written implementations used by live endpoints (no `heapq`, `Counter`, or `sort_values`):
- **Top-K min-heap** — selects the K busiest zones in O(n log k)
- **Quicksort** — median-of-three, in-place; sorts API results in O(n log n) average

See `docs/report.md` §3 for pseudo-code and complexity analysis.

## Team

| Name | Role |
|---|---|
| _add_ | _add_ |
