"""Central config: paths, DB connection, cleaning thresholds."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

TRIPS_PARQUET = DATA_DIR / "yellow_tripdata_2019-01.parquet"
ZONE_LOOKUP_CSV = DATA_DIR / "taxi_zone_lookup.csv"
ZONES_ZIP = DATA_DIR / "taxi_zones.zip"

EXCLUSION_LOG = DATA_DIR / "exclusion_log.csv"
ETL_SUMMARY = DATA_DIR / "etl_summary.json"
ZONES_GEOJSON = ROOT / "frontend" / "js" / "zones.geojson"

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nyc_taxi"
)

CHUNK_SIZE = 200_000  # rows per batch streamed from parquet (~7.7M rows total)

# ── Cleaning thresholds ───────────────────────────────────────────
# TODO(team): justify each threshold in the report (§1 assumptions).
RULES = {
    "month_start": "2019-01-01",
    "month_end": "2019-02-01",     # dropoff may spill into Feb 1
    "min_duration_min": 1.0,
    "max_duration_min": 720.0,     # 12 h
    "min_distance_mi": 0.1,
    "max_distance_mi": 100.0,
    "min_fare": 0.01,
    "max_fare": 500.0,
    "max_total": 700.0,
    "max_speed_mph": 80.0,         # physically implausible above this in NYC
    "min_passengers": 1,
    "max_passengers": 6,
    "valid_location_ids": set(range(1, 264)),  # 1–263 per taxi_zone_lookup
    # Categorical IDs present in dim_* tables. Real TLC data carries codes
    # beyond the official spec (VendorID 4, RatecodeID 99); anything outside
    # these sets is coerced to NULL so the foreign keys hold. See db/schema.sql.
    "valid_vendor_ids": {1, 2, 4},
    "valid_rate_codes": {1, 2, 3, 4, 5, 6, 99},
    "valid_payment_types": {1, 2, 3, 4, 5, 6},
}
