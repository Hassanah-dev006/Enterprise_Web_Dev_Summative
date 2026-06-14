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