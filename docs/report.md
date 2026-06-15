#NYC YELLOW TAXI EXPLORER - TECHNICAL REPORT

**January 2019 . 7.31M cleaned trips**
> This is the readable source of the report. The submission PDF is
> `docs/report.pdf`, regenerated from real run figures with
> `python docs/build_report.py`.

## 1. Problem Framing and Dataset Analysis

The dataset is the NYC Taxi & Limousine Commission (TLC) Yellow Taxi record for
January 2019: **7,696,617** raw trips across 18 fields, joined to
`taxi_zone_lookup` (263 zones) and a zone boundary shapefile. The raw files form
a fact/dimension environment — trip-level facts plus categorical and spatial
dimensions. We integrated them in a streaming pipeline: trip parquet is read in
200k-row batches, enriched, and bulk-loaded; zone polygons are reprojected
(EPSG:2263 → WGS84) into the zone dimension.

**Data integrity.** Eight rules removed **390,723** records (5.1%). Thresholds
reflect physical and contractual limits: trip duration 1–720 min, distance
0.1–100 mi, fare \$0.01–\$500, average speed ≤ 80 mph, passengers 1–6, and
pickup timestamp within the month. Duplicates and rows missing critical fields
were dropped; out-of-spec categorical codes (e.g. VendorID 4, RatecodeID 99)
were preserved where legitimate and otherwise coerced to NULL so foreign keys
hold.

