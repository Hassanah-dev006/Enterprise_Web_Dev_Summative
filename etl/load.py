"""Bulk-load cleaned chunks into PostgreSQL via COPY (fast path for 7.7M rows)."""
import io
import json

import pandas as pd
import psycopg2

from .config import DATABASE_URL, ZONE_LOOKUP_CSV

# fact_trip columns in COPY order (trip_id is BIGSERIAL → omitted)
FACT_COLS = [
    "vendor_id", "pickup_ts", "dropoff_ts", "passenger_count", "trip_distance",
    "rate_code_id", "store_and_fwd", "pu_location_id", "do_location_id",
    "payment_type_id", "fare_amount", "extra", "mta_tax", "tip_amount",
    "tolls_amount", "improvement_surcharge", "total_amount",
    "congestion_surcharge", "duration_min", "avg_speed_mph", "fare_per_mile",
    "tip_pct", "pickup_hour", "pickup_dow", "is_weekend",
]

RENAME = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_ts",
    "tpep_dropoff_datetime": "dropoff_ts",
    "RatecodeID": "rate_code_id",
    "store_and_fwd_flag": "store_and_fwd",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
    "payment_type": "payment_type_id",
}


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def load_zones(conn, geojson: dict) -> None:
    """Populate dim_zone from lookup CSV + GeoJSON geometries."""
    lookup = pd.read_csv(ZONE_LOOKUP_CSV)
    geoms = {
        f["properties"]["location_id"]: json.dumps(f["geometry"])
        for f in geojson["features"]
    }
    with conn.cursor() as cur:
        for _, row in lookup.iterrows():
            cur.execute(
                """INSERT INTO dim_zone (location_id, borough, zone_name, service_zone, geometry)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (location_id) DO NOTHING""",
                (
                    int(row["LocationID"]),
                    row["Borough"],
                    row["Zone"],
                    row["service_zone"],
                    geoms.get(int(row["LocationID"])),
                ),
            )
    conn.commit()


# Integer-typed fact columns. The TLC parquet stores these as doubles (to allow
# NaN), so they would serialize as "1.0" and be rejected by SMALLINT. Cast to
# pandas nullable Int so they emit "1" and NaN → the COPY NULL marker.
INT_COLS = [
    "vendor_id", "passenger_count", "rate_code_id", "payment_type_id",
    "pu_location_id", "do_location_id", "pickup_hour", "pickup_dow",
]


def copy_chunk(conn, df: pd.DataFrame) -> None:
    """COPY one cleaned+featured chunk into fact_trip."""
    out = df.rename(columns=RENAME)[FACT_COLS].copy()
    for col in INT_COLS:
        out[col] = out[col].astype("Int64")
    buf = io.StringIO()
    out.to_csv(buf, index=False, header=False, na_rep="\\N")
    buf.seek(0)
    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY fact_trip ({', '.join(FACT_COLS)}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
            buf,
        )
    conn.commit()


def write_exclusion_summary(conn, counts: dict[str, int]) -> None:
    with conn.cursor() as cur:
        for rule, n in sorted(counts.items()):
            cur.execute(
                """INSERT INTO etl_exclusion_summary (rule, n_excluded)
                   VALUES (%s, %s)
                   ON CONFLICT (rule) DO UPDATE SET n_excluded = EXCLUDED.n_excluded""",
                (rule, n),
            )
    conn.commit()
