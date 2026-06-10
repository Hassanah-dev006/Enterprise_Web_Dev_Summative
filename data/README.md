# `data/` — raw inputs (not committed)

These files are the public NYC TLC dataset, not project source code, so they are
gitignored and must be downloaded locally before running the ETL pipeline.

Place exactly these three files in this folder:

| File | What it is | Where to get it |
|---|---|---|
| `yellow_tripdata_2019-01.parquet` | Fact table — ~7.7M trip records | TLC CloudFront bucket (see below) |
| `taxi_zone_lookup.csv` | Dimension — LocationID → borough/zone | TLC Trip Record Data page |
| `taxi_zones.zip` | Spatial — zone boundary shapefile | TLC Trip Record Data page |

## Download

TLC landing page (links to the lookup CSV and the zone shapefile zip):
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Trip data is served as **parquet** from the TLC CloudFront bucket. The January
2019 yellow file is:

```
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2019-01.parquet
```

Save it here as `yellow_tripdata_2019-01.parquet`.

## Notes

- The ETL reads parquet via `pyarrow` (`etl/run_pipeline.py`), streamed in
  row-batches of `CHUNK_SIZE` so the full file never loads into memory at once.
- After a successful run, this folder also holds the generated
  `exclusion_log.csv` and `etl_summary.json` (both gitignored).
- Column names match the TLC schema (`VendorID`, `tpep_pickup_datetime`,
  `PULocationID`, …); if a future month renames fields, update `etl/clean.py`.
