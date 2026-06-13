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
├── docs/                  # Technical report, architecture docs, build scripts
├── Dockerfile             # App/ETL image
├── docker-compose.yml     # Postgres + ETL + web (one-command deploy)
└── docker/                # ETL entrypoint
```
