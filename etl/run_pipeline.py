"""ETL entry point: python -m etl.run_pipeline

Streams the raw parquet in row-batches → clean → engineer features → COPY to
PostgreSQL. Writes data/exclusion_log.csv (sampled excluded rows) and
data/etl_summary.json.
"""
import json
import time

import pyarrow.parquet as pq

from . import clean, features, load, zones
from .config import CHUNK_SIZE, ETL_SUMMARY, EXCLUSION_LOG, TRIPS_PARQUET


def main() -> None:
    t0 = time.time()
    print("1/3 zones: shapefile → GeoJSON → dim_zone")
    geojson = zones.build_geojson()
    conn = load.get_conn()
    load.load_zones(conn, geojson)

    print("2/3 trips: clean + features + load (chunked)")
    totals: dict[str, int] = {}
    n_in = n_out = 0
    first_sample = True

    pf = pq.ParquetFile(TRIPS_PARQUET)
    for i, batch in enumerate(pf.iter_batches(batch_size=CHUNK_SIZE)):
        chunk = batch.to_pandas()
        n_in += len(chunk)
        cleaned, counts, samples = clean.clean_chunk(chunk)
        for rule, n in counts.items():
            totals[rule] = totals.get(rule, 0) + n
        if not samples.empty:
            samples.to_csv(
                EXCLUSION_LOG, mode="w" if first_sample else "a",
                header=first_sample, index=False,
            )
            first_sample = False
        cleaned = features.add_features(cleaned)
        load.copy_chunk(conn, cleaned)
        n_out += len(cleaned)
        print(f"  chunk {i + 1}: kept {len(cleaned):,}/{len(chunk):,} (total {n_out:,})")

    print("3/3 summary")
    load.write_exclusion_summary(conn, totals)
    conn.close()

    summary = {
        "rows_in": n_in,
        "rows_loaded": n_out,
        "rows_excluded": n_in - n_out,
        "exclusions_by_rule": totals,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    ETL_SUMMARY.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
