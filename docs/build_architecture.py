"""Build the architecture design document (PDF + diagrams).

Usage:  python docs/build_architecture.py
Outputs: docs/arch_assets/*.png  and  docs/architecture.pdf
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "arch_assets")
os.makedirs(ASSETS, exist_ok=True)

YELLOW = "#F7B733"
DARK = "#1F2430"
BLUE = "#2D6CDF"
GREEN = "#2E8B57"
GREY = "#B8BCC6"
LIGHT = "#FBF6E7"


def _box(ax, x, y, w, h, label, fc=YELLOW, ec=DARK, fs=8.5, tc=DARK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fs, color=tc, zorder=5)


def _arrow(ax, p1, p2, color=DARK, style="-|>", lw=1.4):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13,
                                 color=color, lw=lw, zorder=1))


# ── 1. Layered component view ──────────────────────────────────────────
def diagram_layered():
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    # layer bands
    bands = [(7.3, "PRESENTATION", "#FFF3D6"), (4.9, "APPLICATION", "#E8F0FF"),
             (2.5, "DATA", "#E6F4EC"), (0.3, "SOURCE", "#F0F0F2")]
    for y, name, col in bands:
        ax.add_patch(FancyBboxPatch((0.2, y), 9.6, 2.0, boxstyle="round,pad=0.02",
                     fc=col, ec=GREY, lw=1))
        ax.text(0.4, y + 1.7, name, fontsize=7.5, color=GREY, fontweight="bold")

    _box(ax, 0.7, 7.7, 2.6, 1.1, "Dashboard (index.html)\nfilters · KPI cards", fc=YELLOW)
    _box(ax, 3.7, 7.7, 2.6, 1.1, "Chart.js\nhourly · zone bars", fc=YELLOW)
    _box(ax, 6.7, 7.7, 2.6, 1.1, "Leaflet\nzone choropleth", fc=YELLOW)

    _box(ax, 0.7, 5.3, 2.6, 1.1, "Flask app.py\nstatic + routes", fc="#Bcd2ff")
    _box(ax, 3.7, 5.3, 2.6, 1.1, "API endpoints\n/api/stats/*  /api/trips", fc="#Bcd2ff")
    _box(ax, 6.7, 5.3, 2.6, 1.1, "algorithms/\ntop-K heap · quicksort", fc="#Bcd2ff")

    _box(ax, 0.7, 2.9, 2.6, 1.1, "PostgreSQL\nfact_trip + dims", fc="#bfe6cf")
    _box(ax, 3.7, 2.9, 2.6, 1.1, "7 indexes\ntime · zone · fare", fc="#bfe6cf")
    _box(ax, 6.7, 2.9, 2.6, 1.1, "zones.geojson\n(static, for map)", fc="#bfe6cf")

    _box(ax, 1.7, 0.6, 2.6, 1.1, "yellow_tripdata\n.parquet", fc=GREY)
    _box(ax, 4.5, 0.6, 2.6, 1.1, "taxi_zone_lookup\n.csv", fc=GREY)
    # ETL bridge label
    _box(ax, 7.3, 0.6, 2.1, 1.1, "taxi_zones\nshapefile", fc=GREY)

    for x in (2.0, 5.0, 8.0):
        _arrow(ax, (x, 7.7), (x, 6.4), color=BLUE)       # app <- presentation
        _arrow(ax, (x, 5.3), (x, 4.0), color=GREEN)      # data <- app
    _arrow(ax, (3.0, 1.7), (3.0, 2.9), color=DARK, lw=1.6)
    _arrow(ax, (5.8, 1.7), (5.8, 2.9), color=DARK, lw=1.6)
    ax.text(5.0, 2.25, "ETL pipeline (one-time load)", ha="center", fontsize=7.5,
            color=DARK, style="italic")

    ax.set_title("1 · Layered component architecture", fontweight="bold", fontsize=11)
    fig.tight_layout()
    p = os.path.join(ASSETS, "arch1_layered.png"); fig.savefig(p, dpi=150)
    plt.close(fig); return p


# ── 2. ETL data-flow pipeline ──────────────────────────────────────────
def diagram_etl():
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    _box(ax, 0.2, 2.0, 1.7, 1.2, "parquet\n(7.70M rows)", fc=GREY)
    _box(ax, 2.4, 2.0, 1.8, 1.2, "read batches\n200k rows", fc=YELLOW)
    _box(ax, 4.7, 2.0, 1.8, 1.2, "clean\n8 rules", fc=YELLOW)
    _box(ax, 7.0, 2.0, 1.8, 1.2, "features\n+5 derived", fc=YELLOW)
    _box(ax, 9.3, 2.0, 1.8, 1.2, "COPY ->\nfact_trip", fc="#bfe6cf")
    for x in (1.9, 4.2, 6.5, 8.8):
        _arrow(ax, (x, 2.6), (x + 0.5, 2.6))
    # exclusion branch
    _box(ax, 4.5, 0.1, 2.2, 1.0, "exclusion_log.csv\n390,723 rows", fc="#F5D0CE")
    _arrow(ax, (5.6, 2.0), (5.6, 1.1), color="#C0392B")
    # zones branch
    _box(ax, 2.2, 3.7, 2.0, 1.0, "shapefile ->\nGeoJSON (WGS84)", fc=GREY)
    _box(ax, 9.3, 3.7, 1.8, 1.0, "dim_zone\n+ geometry", fc="#bfe6cf")
    _arrow(ax, (4.2, 4.2), (9.3, 4.2), color=GREEN, style="-|>")
    ax.text(6.7, 4.35, "263 zone polygons", ha="center", fontsize=7, color=GREEN)
    ax.set_title("2 · ETL data-flow pipeline", fontweight="bold", fontsize=11)
    fig.tight_layout()
    p = os.path.join(ASSETS, "arch2_etl.png"); fig.savefig(p, dpi=150)
    plt.close(fig); return p


# ── 3. ER / star schema ────────────────────────────────────────────────
def _table_box(ax, x, y, title, rows, w=2.6, fc=YELLOW):
    h = 0.34 * (len(rows) + 1)
    ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="square,pad=0.02",
                 fc="white", ec=DARK, lw=1.3))
    ax.add_patch(FancyBboxPatch((x, y - 0.34), w, 0.34, boxstyle="square,pad=0.02",
                 fc=fc, ec=DARK, lw=1.3))
    ax.text(x + w / 2, y - 0.17, title, ha="center", va="center",
            fontsize=8, fontweight="bold")
    for i, r in enumerate(rows):
        ax.text(x + 0.1, y - 0.34 - 0.30 * (i + 0.6), r, ha="left", va="center",
                fontsize=6.7, family="monospace")
    return (x, y, w, h)


def diagram_er():
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 11); ax.axis("off")

    fact = _table_box(ax, 4.4, 9.6, "fact_trip  (7.31M)", [
        "PK trip_id", "FK pu_location_id", "FK do_location_id", "FK vendor_id",
        "FK rate_code_id", "FK payment_type_id", "pickup_ts / dropoff_ts",
        "trip_distance / fare / total", "* duration_min  (derived)",
        "* avg_speed_mph (derived)", "* fare_per_mile (derived)",
        "* tip_pct       (derived)", "pickup_hour / dow / is_weekend"],
        w=3.4, fc=YELLOW)

    z = _table_box(ax, 0.3, 10.2, "dim_zone (263)", [
        "PK location_id", "borough", "zone_name", "service_zone", "geometry JSONB"],
        w=2.6, fc="#bfe6cf")
    v = _table_box(ax, 0.3, 4.6, "dim_vendor", ["PK vendor_id", "name"],
                   w=2.6, fc="#bfe6cf")
    r = _table_box(ax, 9.0, 10.2, "dim_rate_code", ["PK rate_code_id", "description"],
                   w=2.6, fc="#bfe6cf")
    p = _table_box(ax, 9.0, 5.4, "dim_payment_type", ["PK payment_type_id", "description"],
                   w=2.6, fc="#bfe6cf")

    # relationship lines (crow's-foot-ish): dims 1 --- * fact
    _arrow(ax, (2.9, 8.9), (4.4, 8.6), color=DARK, style="-")
    _arrow(ax, (2.9, 8.4), (4.4, 8.1), color=DARK, style="-")  # second zone FK
    _arrow(ax, (2.9, 4.2), (4.4, 6.2), color=DARK, style="-")
    _arrow(ax, (9.0, 9.5), (7.8, 8.6), color=DARK, style="-")
    _arrow(ax, (9.0, 4.9), (7.8, 6.0), color=DARK, style="-")
    ax.text(3.4, 8.95, "PU/DO", fontsize=6.5, color=DARK)

    ax.text(6.1, 0.6, "* = engineered feature   |   PK primary key   |   FK foreign key",
            ha="center", fontsize=7.5, color=GREY)
    ax.set_title("3 · Entity-relationship (star schema)", fontweight="bold", fontsize=11)
    fig.tight_layout()
    out = os.path.join(ASSETS, "arch3_er.png"); fig.savefig(out, dpi=150)
    plt.close(fig); return out


# ── 4. Runtime request flow ────────────────────────────────────────────
def diagram_request():
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    steps = [
        (0.2, "Browser\nApply filter", YELLOW),
        (2.4, "GET /api/stats/\ntop-zones?k=10", "#Bcd2ff"),
        (4.9, "Flask route\nbuild WHERE", "#Bcd2ff"),
        (7.2, "PostgreSQL\nGROUP BY zone", "#bfe6cf"),
        (9.6, "top-K heap\nO(n log k)", "#F5D0CE"),
    ]
    for x, label, c in steps:
        _box(ax, x, 1.4, 2.0, 1.2, label, fc=c)
    for x in (2.2, 4.4, 6.9, 9.2):
        _arrow(ax, (x, 2.0), (x + 0.4, 2.0))
    # return path
    _arrow(ax, (10.6, 1.4), (10.6, 0.6), color=DARK)
    _arrow(ax, (10.6, 0.6), (1.2, 0.6), color=DARK)
    _arrow(ax, (1.2, 0.6), (1.2, 1.4), color=DARK)
    ax.text(5.9, 0.42, "JSON response  ->  Chart.js renders ranked bars",
            ha="center", fontsize=7.5, color=DARK, style="italic")
    ax.set_title("4 · Runtime request flow (top-zones endpoint)",
                 fontweight="bold", fontsize=11)
    fig.tight_layout()
    out = os.path.join(ASSETS, "arch4_request.png"); fig.savefig(out, dpi=150)
    plt.close(fig); return out


# ── PDF assembly ───────────────────────────────────────────────────────
def build_pdf(figs):
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5,
                          leading=13, spaceAfter=6)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13,
                        textColor=colors.HexColor(DARK), spaceBefore=10, spaceAfter=4)
    title = ParagraphStyle("t", parent=styles["Title"], fontSize=18,
                           textColor=colors.HexColor(DARK))
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8)
    cap = ParagraphStyle("cap", parent=styles["Italic"], fontSize=8,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=10)

    def img(path, w=6.4):
        from PIL import Image as PILImage
        iw, ih = PILImage.open(path).size
        return Image(path, width=w * inch, height=w * inch * ih / iw)

    s = []
    s.append(Paragraph("NYC Yellow Taxi Trip Explorer", title))
    s.append(Paragraph("Architecture Design Document", sub))

    s.append(Paragraph("Overview", h1))
    s.append(Paragraph(
        "The system is a four-layer pipeline that turns a raw 7.7M-row TLC parquet "
        "file into an interactive urban-mobility dashboard. A one-time <b>ETL</b> "
        "cleans and enriches trips and loads them into a <b>PostgreSQL</b> star "
        "schema; a <b>Flask</b> service exposes aggregate and detail endpoints (two of "
        "which rank results with hand-written algorithms); and a static <b>HTML/CSS/JS "
        "</b> dashboard renders charts and a zone choropleth. The same Flask process "
        "serves both the API and the dashboard, so the whole product runs from a "
        "single command.", body))
    s.append(_meta_table())

    s.append(Paragraph("1. Layered Component View", h1))
    s.append(img(figs["layered"], w=6.0))
    s.append(Paragraph("Fig. 1 - Four layers; arrows show runtime calls (top three "
                       "layers) and the one-time ETL load (bottom).", cap))
    s.append(Paragraph(
        "<b>Presentation</b> is vanilla JS: <i>app.js</i> orchestrates filter state, "
        "<i>api.js</i> calls the backend, <i>charts.js</i> drives Chart.js, and "
        "<i>map.js</i> drives Leaflet. <b>Application</b> is Flask: <i>app.py</i> serves "
        "static files and JSON routes, delegating ranking to <i>algorithms/</i>. "
        "<b>Data</b> is PostgreSQL plus a static <i>zones.geojson</i> the map loads "
        "directly. <b>Source</b> is the three raw TLC files, consumed only by the ETL.",
        body))

    s.append(Paragraph("2. ETL Data-Flow Pipeline", h1))
    s.append(img(figs["etl"], w=6.4))
    s.append(Paragraph("Fig. 2 - Streaming load with an exclusion-log branch and a "
                       "one-pass zone-geometry branch.", cap))
    s.append(Paragraph(
        "The trip parquet is streamed in 200k-row batches so memory stays bounded. "
        "Each batch passes through eight integrity rules (duplicates, missing fields, "
        "and physical/logical outliers), then five engineered features are added "
        "(duration, average speed, fare-per-mile, tip percent, and temporal keys), and "
        "the batch is bulk-loaded with PostgreSQL <b>COPY</b>. Rejected rows "
        "(<b>390,723</b>, 5.1%) are sampled to <i>exclusion_log.csv</i> and counted in "
        "<i>etl_exclusion_summary</i>. In parallel, the zone shapefile is reprojected "
        "from EPSG:2263 to WGS84 once and written both to <i>dim_zone.geometry</i> and "
        "to the static GeoJSON.", body))

    s.append(Paragraph("3. Database Design (Star Schema)", h1))
    s.append(img(figs["er"], w=6.2))
    s.append(Paragraph("Fig. 3 - One fact table referencing four dimensions; engineered "
                       "features marked with an asterisk.", cap))
    s.append(Paragraph(
        "<i>fact_trip</i> holds one row per trip with foreign keys to four dimensions. "
        "<i>dim_zone</i> is referenced twice - pickup and dropoff. Engineered features "
        "and the temporal keys (hour, day-of-week, weekend) are denormalized onto the "
        "fact table so the dashboard's frequent group-bys become single-column scans. "
        "Seven B-tree indexes cover the filter columns: pickup timestamp, pickup zone, "
        "dropoff zone, hour, fare, distance, and payment type. Foreign keys are nullable "
        "so out-of-spec categorical codes can be set NULL without dropping the trip.",
        body))

    s.append(Paragraph("4. Runtime Request Flow", h1))
    s.append(img(figs["request"], w=6.4))
    s.append(Paragraph("Fig. 4 - A filtered top-zones request, end to end.", cap))
    s.append(Paragraph(
        "When the user applies a filter, the dashboard issues a single GET with the "
        "filter as query parameters. The Flask route validates inputs against a "
        "whitelist (sort columns and metrics are never interpolated raw) and builds a "
        "parameterised WHERE clause. PostgreSQL returns per-zone aggregates over the "
        "indexed columns; the route then ranks them with the custom <b>top-K min-heap</b> "
        "(O(n log k)) rather than SQL ORDER BY/LIMIT, demonstrating the hand-written "
        "structure on live data. The JSON response is rendered by Chart.js. The sibling "
        "<i>zone-ranking</i> endpoint sorts all 263 zones with the custom quicksort to "
        "colour the choropleth.", body))

    s.append(Paragraph("Cross-Cutting Concerns", h1))
    s.append(Paragraph(
        "<b>Security:</b> all SQL is parameterised and sortable columns/metrics are "
        "whitelisted, preventing injection. <b>Performance:</b> chunked COPY load, "
        "covering indexes, and denormalized temporal keys keep both load and query "
        "fast. <b>Reproducibility:</b> the ETL is deterministic and writes a summary "
        "(<i>etl_summary.json</i>) plus the exclusion log for audit. <b>Portability:</b> "
        "the API port is configurable (defaults to 5001 to avoid macOS AirPlay on "
        "5000), and the frontend uses relative paths so it works behind any host.", body))

    doc = SimpleDocTemplate(os.path.join(HERE, "architecture.pdf"), pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch)
    doc.build(s)


def _meta_table():
    data = [["Layer", "Technology", "Responsibility"],
            ["Presentation", "HTML/CSS/JS, Chart.js, Leaflet", "Filters, charts, map"],
            ["Application", "Flask, custom algorithms", "REST API, ranking"],
            ["Data", "PostgreSQL, static GeoJSON", "Storage, indexing"],
            ["ETL", "pandas, pyarrow, COPY", "Clean, enrich, load"]]
    t = Table(data, colWidths=[1.3 * inch, 2.7 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(LIGHT)]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4D8E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


if __name__ == "__main__":
    figs = {
        "layered": diagram_layered(),
        "etl": diagram_etl(),
        "er": diagram_er(),
        "request": diagram_request(),
    }
    build_pdf(figs)
    print("wrote docs/architecture.pdf and docs/arch_assets/*.png")
