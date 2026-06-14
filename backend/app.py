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

