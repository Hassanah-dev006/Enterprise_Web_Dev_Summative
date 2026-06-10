# Technical Report — NYC Taxi Trip Explorer
_Draft outline (2–3 pages when exported to PDF). Fill in after running the pipeline._

## 1. Problem Framing and Dataset Analysis
- Dataset: NYC TLC Yellow Taxi, January 2019 — 7,667,792 raw trip records, 18 fields,
  plus taxi_zone_lookup (263 zones) and zone shapefile.
- Data challenges found: _[fill from data/etl_summary.json — duplicates, missing
  congestion_surcharge, zero-distance trips, $0 / negative fares, impossible speeds,
  passenger_count = 0, LocationIDs 264/265 "Unknown"]_
- Cleaning assumptions: thresholds in `etl/config.py` (RULES dict) — justify each.
- **Unexpected observation that influenced design:** _[fill — e.g. share of trips with
  passenger_count 0, or fare distribution spike at flat-rate JFK $52]_

## 2. System Architecture and Design Decisions
- Diagram: _[frontend (Chart.js/Leaflet) → Flask API → PostgreSQL star schema ← ETL pipeline]_
- Stack: Python ETL (pandas chunked streaming + COPY) / PostgreSQL / Flask / vanilla JS.
- Schema: star schema — fact_trip + dim_zone, dim_vendor, dim_rate_code, dim_payment_type.
  Denormalized pickup_hour/dow on the fact for fast grouping (trade-off: storage vs speed).
- Trade-offs to discuss: chunked CSV vs in-memory; JSONB geometry in DB vs static
  GeoJSON file; SQL aggregation + custom algorithms vs pure-SQL ranking.

## 3. Algorithmic Logic and Data Structures (manual implementation)
Two hand-written implementations, both used by live endpoints:
1. **Top-K min-heap** (`backend/algorithms/topk_heap.py`) → `/api/stats/top-zones`
   - O(n log k) time, O(k) space. Pseudo-code: _[fill]_
2. **Quicksort, median-of-three** (`backend/algorithms/quicksort.py`) → `/api/stats/zone-ranking`
   - O(n log n) avg / O(n²) worst, O(log n) space. Pseudo-code: _[fill]_

## 4. Insights and Interpretation (three required)
1. _[e.g. Demand vs speed by hour — evening rush has most trips but slowest speeds → congestion]_
2. _[e.g. Tipping behaviour by zone/borough — card tip % patterns]_
3. _[e.g. Airport trips (JFK/LGA flat rates) dominate revenue per trip]_
Each: how derived (query/algorithm/visual) + screenshot + urban-mobility interpretation.

## 5. Reflection and Future Work
- Technical challenges: _[fill]_
- Team challenges: _[fill]_
- Next steps: multi-month data, PostGIS for true spatial queries, caching layer,
  deployment (Docker), demand prediction.
