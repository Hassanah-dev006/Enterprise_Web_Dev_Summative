"""Flask API + static frontend server.

Run:  python -m backend.app   →  http://localhost:5001
"""
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from . import db
from .algorithms import quicksort, top_k

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend"),
    static_url_path="",
)
CORS(app)

# Whitelists — never interpolate raw user input into SQL
SORTABLE = {
    "pickup_ts", "trip_distance", "fare_amount", "tip_amount",
    "total_amount", "duration_min", "avg_speed_mph",
}
ZONE_METRICS = {"trips", "total_revenue", "avg_fare", "avg_distance", "avg_tip_pct"}


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/health")
def health():
    n = db.query("SELECT count(*) AS n FROM fact_trip")[0]["n"]
    return jsonify({"status": "ok", "trips": n})


@app.route("/api/zones")
def zones():
    rows = db.query(
        "SELECT location_id, borough, zone_name, service_zone FROM dim_zone ORDER BY location_id"
    )
    return jsonify(rows)


def _trip_filters():
    """Shared WHERE clause from query-string filters."""
    clauses, params = [], []
    f = request.args
    if f.get("start"):
        clauses.append("pickup_ts >= %s"); params.append(f["start"])
    if f.get("end"):
        clauses.append("pickup_ts < %s"); params.append(f["end"])
    if f.get("hour_min"):
        clauses.append("pickup_hour >= %s"); params.append(int(f["hour_min"]))
    if f.get("hour_max"):
        clauses.append("pickup_hour <= %s"); params.append(int(f["hour_max"]))
    if f.get("borough"):
        clauses.append("pu_location_id IN (SELECT location_id FROM dim_zone WHERE borough = %s)")
        params.append(f["borough"])
    if f.get("fare_min"):
        clauses.append("fare_amount >= %s"); params.append(float(f["fare_min"]))
    if f.get("fare_max"):
        clauses.append("fare_amount <= %s"); params.append(float(f["fare_max"]))
    if f.get("dist_min"):
        clauses.append("trip_distance >= %s"); params.append(float(f["dist_min"]))
    if f.get("dist_max"):
        clauses.append("trip_distance <= %s"); params.append(float(f["dist_max"]))
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


@app.route("/api/trips")
def trips():
    """Paginated trip browser with filtering and sorting."""
    sort = request.args.get("sort", "pickup_ts")
    if sort not in SORTABLE:
        return jsonify({"error": f"sort must be one of {sorted(SORTABLE)}"}), 400
    order = "DESC" if request.args.get("order", "desc").lower() == "desc" else "ASC"
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(200, int(request.args.get("per_page", 50)))
    where, params = _trip_filters()

    rows = db.query(
        f"""SELECT t.trip_id, t.pickup_ts, t.dropoff_ts, zp.zone_name AS pu_zone,
                   zd.zone_name AS do_zone, t.trip_distance, t.duration_min,
                   t.fare_amount, t.tip_amount, t.total_amount, p.description AS payment
            FROM fact_trip t
            JOIN dim_zone zp ON zp.location_id = t.pu_location_id
            JOIN dim_zone zd ON zd.location_id = t.do_location_id
            LEFT JOIN dim_payment_type p ON p.payment_type_id = t.payment_type_id
            {where}
            ORDER BY t.{sort} {order}
            LIMIT %s OFFSET %s""",
        params + [per_page, (page - 1) * per_page],
    )
    total = db.query(f"SELECT count(*) AS n FROM fact_trip t {where}", params)[0]["n"]
    return jsonify({"page": page, "per_page": per_page, "total": total, "rows": rows})


@app.route("/api/stats/summary")
def summary():
    where, params = _trip_filters()
    row = db.query(
        f"""SELECT count(*) AS trips,
                   round(sum(total_amount), 2) AS total_revenue,
                   round(avg(trip_distance)::numeric, 2) AS avg_distance,
                   round(avg(fare_amount)::numeric, 2) AS avg_fare,
                   round(avg(duration_min)::numeric, 1) AS avg_duration_min,
                   round(avg(tip_pct)::numeric, 1) AS avg_tip_pct
            FROM fact_trip t {where}""",
        params,
    )[0]
    return jsonify(row)


@app.route("/api/stats/hourly")
def hourly():
    where, params = _trip_filters()
    rows = db.query(
        f"""SELECT pickup_hour AS hour, count(*) AS trips,
                   round(avg(fare_amount)::numeric, 2) AS avg_fare,
                   round(avg(avg_speed_mph)::numeric, 1) AS avg_speed_mph
            FROM fact_trip t {where}
            GROUP BY pickup_hour ORDER BY pickup_hour""",
        params,
    )
    return jsonify(rows)


@app.route("/api/stats/top-zones")
def top_zones():
    """K busiest pickup zones — ranked with the CUSTOM top-K min-heap
    (backend/algorithms/topk_heap.py), not SQL ORDER BY/LIMIT."""
    k = min(50, int(request.args.get("k", 10)))
    metric = request.args.get("metric", "trips")
    if metric not in ZONE_METRICS:
        return jsonify({"error": f"metric must be one of {sorted(ZONE_METRICS)}"}), 400
    where, params = _trip_filters()

    zones = db.query(
        f"""SELECT z.location_id, z.zone_name, z.borough,
                   count(*) AS trips,
                   round(sum(t.total_amount), 2) AS total_revenue,
                   round(avg(t.fare_amount)::numeric, 2) AS avg_fare,
                   round(avg(t.trip_distance)::numeric, 2) AS avg_distance,
                   round(avg(t.tip_pct)::numeric, 1) AS avg_tip_pct
            FROM fact_trip t JOIN dim_zone z ON z.location_id = t.pu_location_id
            {where}
            GROUP BY z.location_id, z.zone_name, z.borough""",
        params,
    )
    ranked = top_k(zones, k, key=lambda z: float(z[metric] or 0))
    return jsonify(ranked)

