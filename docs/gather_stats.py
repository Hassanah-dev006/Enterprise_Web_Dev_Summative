"""Print aggregate stats for the technical report in one shot.

Run from the repo root with the venv active:
    python docs/gather_stats.py

Copy the JSON it prints and hand it back so the report uses real figures.
"""
import json
import os
import sys

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql:///nyc_taxi")


def q(cur, sql):
    cur.execute(sql)
    return [dict(r) for r in cur.fetchall()]


def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    out = {}

    out["summary"] = q(cur, """
        SELECT count(*) AS trips,
               round(sum(total_amount), 2) AS total_revenue,
               round(avg(trip_distance)::numeric, 2) AS avg_distance,
               round(avg(fare_amount)::numeric, 2) AS avg_fare,
               round(avg(duration_min)::numeric, 1) AS avg_duration_min,
               round(avg(avg_speed_mph)::numeric, 1) AS avg_speed_mph,
               round(avg(tip_pct)::numeric, 1) AS avg_tip_pct
        FROM fact_trip""")[0]

    out["hourly"] = q(cur, """
        SELECT pickup_hour AS hour, count(*) AS trips,
               round(avg(fare_amount)::numeric, 2) AS avg_fare,
               round(avg(avg_speed_mph)::numeric, 1) AS avg_speed_mph
        FROM fact_trip GROUP BY pickup_hour ORDER BY pickup_hour""")

    out["top_zones_by_trips"] = q(cur, """
        SELECT z.zone_name, z.borough, count(*) AS trips
        FROM fact_trip t JOIN dim_zone z ON z.location_id = t.pu_location_id
        GROUP BY z.zone_name, z.borough ORDER BY trips DESC LIMIT 10""")

    out["top_zones_by_revenue"] = q(cur, """
        SELECT z.zone_name, z.borough, round(sum(t.total_amount),2) AS revenue
        FROM fact_trip t JOIN dim_zone z ON z.location_id = t.pu_location_id
        GROUP BY z.zone_name, z.borough ORDER BY revenue DESC LIMIT 10""")

    out["by_borough"] = q(cur, """
        SELECT z.borough, count(*) AS trips,
               round(avg(t.fare_amount)::numeric,2) AS avg_fare,
               round(avg(t.tip_pct)::numeric,1) AS avg_tip_pct
        FROM fact_trip t JOIN dim_zone z ON z.location_id = t.pu_location_id
        GROUP BY z.borough ORDER BY trips DESC""")

    out["payment_split"] = q(cur, """
        SELECT p.description AS payment, count(*) AS trips,
               round(avg(t.tip_pct)::numeric,1) AS avg_tip_pct
        FROM fact_trip t LEFT JOIN dim_payment_type p
             ON p.payment_type_id = t.payment_type_id
        GROUP BY p.description ORDER BY trips DESC""")

    out["weekend_vs_weekday"] = q(cur, """
        SELECT is_weekend, count(*) AS trips,
               round(avg(fare_amount)::numeric,2) AS avg_fare,
               round(avg(avg_speed_mph)::numeric,1) AS avg_speed_mph
        FROM fact_trip GROUP BY is_weekend ORDER BY is_weekend""")

    # Airport zones: JFK=132, LaGuardia=138, Newark/EWR=1
    out["airport_trips"] = q(cur, """
        SELECT z.zone_name, count(*) AS trips,
               round(avg(t.fare_amount)::numeric,2) AS avg_fare,
               round(avg(t.trip_distance)::numeric,2) AS avg_distance
        FROM fact_trip t JOIN dim_zone z ON z.location_id = t.pu_location_id
        WHERE t.pu_location_id IN (1, 132, 138)
        GROUP BY z.zone_name ORDER BY trips DESC""")

    out["exclusions"] = q(cur,
        "SELECT rule, n_excluded FROM etl_exclusion_summary ORDER BY n_excluded DESC")

    cur.close()
    conn.close()
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
