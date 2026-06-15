#!/bin/sh
# One-shot ETL: wait for Postgres, load schema, run the pipeline, then exit.
set -e

echo "Waiting for PostgreSQL at db:5432 ..."
until pg_isready -h db -U postgres -d nyc_taxi >/dev/null 2>&1; do
  sleep 2
done

# Skip the load if a previous run already populated the database (the pgdata
# volume persists across `docker compose up`), so restarts come up instantly.
if [ "$(psql "$DATABASE_URL" -tAc "SELECT to_regclass('public.fact_trip')")" ]; then
  COUNT=$(psql "$DATABASE_URL" -tAc "SELECT count(*) FROM fact_trip")
  if [ "${COUNT:-0}" -gt 0 ]; then
    echo "Database already loaded (${COUNT} rows) - skipping ETL."
    exit 0
  fi
fi

echo "Loading schema ..."
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/schema.sql

echo "Running ETL pipeline (this loads ~7.3M rows; allow a few minutes) ..."
python -m etl.run_pipeline

echo "ETL complete."
