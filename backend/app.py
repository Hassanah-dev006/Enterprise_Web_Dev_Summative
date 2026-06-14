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