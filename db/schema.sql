-- NYC Taxi — normalized relational schema (PostgreSQL)
-- Star schema: small dimension tables + one fact table, indexed for the
-- dashboard's filter patterns (time, location, fare, distance).

DROP TABLE IF EXISTS fact_trip CASCADE;
DROP TABLE IF EXISTS dim_zone CASCADE;
DROP TABLE IF EXISTS dim_vendor CASCADE;
DROP TABLE IF EXISTS dim_rate_code CASCADE;
DROP TABLE IF EXISTS dim_payment_type CASCADE;
DROP TABLE IF EXISTS etl_exclusion_summary CASCADE;

-- ───────────────────────── Dimensions ─────────────────────────

CREATE TABLE dim_zone (
    location_id   SMALLINT PRIMARY KEY,
    borough       TEXT NOT NULL,
    zone_name     TEXT NOT NULL,
    service_zone  TEXT,
    geometry      JSONB              -- GeoJSON polygon (WGS84), for the map
);

CREATE TABLE dim_vendor (
    vendor_id  SMALLINT PRIMARY KEY,
    name       TEXT NOT NULL
);
INSERT INTO dim_vendor VALUES
    (1, 'Creative Mobile Technologies'),
    (2, 'VeriFone Inc.'),
    (4, 'Other / third-party');   -- undocumented but present in real TLC data

CREATE TABLE dim_rate_code (
    rate_code_id  SMALLINT PRIMARY KEY,
    description   TEXT NOT NULL
);
INSERT INTO dim_rate_code VALUES
    (1, 'Standard rate'), (2, 'JFK'), (3, 'Newark'),
    (4, 'Nassau or Westchester'), (5, 'Negotiated fare'), (6, 'Group ride'),
    (99, 'Unknown');   -- junk code present in real TLC data

CREATE TABLE dim_payment_type (
    payment_type_id  SMALLINT PRIMARY KEY,
    description      TEXT NOT NULL
);
INSERT INTO dim_payment_type VALUES
    (1, 'Credit card'), (2, 'Cash'), (3, 'No charge'),
    (4, 'Dispute'), (5, 'Unknown'), (6, 'Voided trip');

-- ───────────────────────── Fact table ─────────────────────────

CREATE TABLE fact_trip (
    trip_id            BIGSERIAL PRIMARY KEY,
    vendor_id          SMALLINT REFERENCES dim_vendor(vendor_id),
    pickup_ts          TIMESTAMP NOT NULL,
    dropoff_ts         TIMESTAMP NOT NULL,
    passenger_count    SMALLINT,
    trip_distance      REAL NOT NULL,
    rate_code_id       SMALLINT REFERENCES dim_rate_code(rate_code_id),
    store_and_fwd      BOOLEAN,
    pu_location_id     SMALLINT NOT NULL REFERENCES dim_zone(location_id),
    do_location_id     SMALLINT NOT NULL REFERENCES dim_zone(location_id),
    payment_type_id    SMALLINT REFERENCES dim_payment_type(payment_type_id),
    fare_amount        NUMERIC(8,2) NOT NULL,
    extra              NUMERIC(8,2),
    mta_tax            NUMERIC(8,2),
    tip_amount         NUMERIC(8,2),
    tolls_amount       NUMERIC(8,2),
    improvement_surcharge NUMERIC(8,2),
    total_amount       NUMERIC(8,2) NOT NULL,
    congestion_surcharge  NUMERIC(8,2),
    -- Derived features (engineered in ETL — see etl/features.py)
    duration_min       REAL NOT NULL,      -- dropoff − pickup, minutes
    avg_speed_mph      REAL,               -- distance / duration
    fare_per_mile      REAL,               -- fare efficiency
    tip_pct            REAL,               -- tip / fare (card payments only)
    pickup_hour        SMALLINT NOT NULL,  -- 0–23, denormalized for fast grouping
    pickup_dow         SMALLINT NOT NULL,  -- 0=Mon … 6=Sun
    is_weekend         BOOLEAN NOT NULL
);

-- Indexes chosen for dashboard query patterns
CREATE INDEX idx_trip_pickup_ts   ON fact_trip (pickup_ts);
CREATE INDEX idx_trip_pu_zone     ON fact_trip (pu_location_id);
CREATE INDEX idx_trip_do_zone     ON fact_trip (do_location_id);
CREATE INDEX idx_trip_hour        ON fact_trip (pickup_hour);
CREATE INDEX idx_trip_fare        ON fact_trip (fare_amount);
CREATE INDEX idx_trip_distance    ON fact_trip (trip_distance);
CREATE INDEX idx_trip_payment     ON fact_trip (payment_type_id);

-- ETL transparency: per-rule exclusion counts (full log in data/exclusion_log.csv)
CREATE TABLE etl_exclusion_summary (
    rule        TEXT PRIMARY KEY,
    n_excluded  BIGINT NOT NULL,
    note        TEXT
);
