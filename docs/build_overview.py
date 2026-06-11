"""Build a single consolidated 'all components' system diagram (PNG + 1-page PDF).

Usage:  python docs/build_overview.py
Outputs: docs/arch_assets/arch5_overview.png  and  docs/system_overview.pdf
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import Image, SimpleDocTemplate

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "arch_assets")
os.makedirs(ASSETS, exist_ok=True)

DARK = "#1F2430"
BLUEC = "#2D6CDF"
YELLOW = "#F7B733"
BLUE = "#BCD2FF"
GREEN = "#BFE6CF"
GREY = "#C7CBD4"
PINK = "#F5D0CE"


def group(ax, x, y_top, w, title, items, body_color):
    item_h, gap, pad_top, pad_bot = 0.6, 0.14, 0.55, 0.22
    n = len(items)
    inner = n * item_h + (n - 1) * gap
    total = pad_top + inner + pad_bot
    y_bottom = y_top - total
    ax.add_patch(FancyBboxPatch((x, y_bottom), w, total, boxstyle="round,pad=0.05",
                                fc=body_color, ec=DARK, lw=1.8, zorder=2))
    ax.text(x + w / 2, y_top - 0.3, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=DARK, zorder=4)
    yy = y_top - pad_top - item_h
    for label, fc in items:
        ax.add_patch(FancyBboxPatch((x + 0.18, yy), w - 0.36, item_h,
                     boxstyle="round,pad=0.03", fc=fc, ec=DARK, lw=1.0, zorder=3))
        ax.text(x + w / 2, yy + item_h / 2, label, ha="center", va="center",
                fontsize=7.4, zorder=4)
        yy -= (item_h + gap)
    return {"x": x, "w": w, "y_top": y_top, "y_bot": y_bottom,
            "mid_y": (y_top - total + pad_bot + inner / 2)}


def arrow(ax, p1, p2, color=DARK, style="-|>", lw=1.8, ls="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=16,
                 color=color, lw=lw, linestyle=ls, zorder=1,
                 connectionstyle="arc3,rad=0"))


def build_png():
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_xlim(0, 15); ax.set_ylim(0, 10); ax.axis("off")
    yt = 9.1

    src = group(ax, 0.3, yt, 2.4, "SOURCE  (raw TLC)", [
        ("yellow_tripdata\n.parquet", GREY),
        ("taxi_zone_lookup\n.csv", GREY),
        ("taxi_zones\nshapefile", GREY)], "#F0F0F2")

    etl = group(ax, 3.0, yt, 3.0, "ETL  (etl/)", [
        ("run_pipeline.py  (orchestrator)", YELLOW),
        ("config.py  -  thresholds", YELLOW),
        ("clean.py  -  8 integrity rules", YELLOW),
        ("features.py  -  5 derived", YELLOW),
        ("zones.py  -  reproject->GeoJSON", YELLOW),
        ("load.py  -  bulk COPY", YELLOW)], "#FFF3D6")

    db = group(ax, 6.4, yt, 2.9, "DATABASE  (PostgreSQL)", [
        ("fact_trip   (7.31M rows)", GREEN),
        ("dim_zone   (+ geometry)", GREEN),
        ("dim_vendor / rate / payment", GREEN),
        ("etl_exclusion_summary", GREEN),
        ("7 B-tree indexes", GREEN),
        ("zones.geojson  (static file)", "#DDEBFF")], "#E6F4EC")

    be = group(ax, 9.7, yt, 2.7, "BACKEND  (Flask, backend/)", [
        ("app.py  -  routes + static", BLUE),
        ("db.py  -  connection pool", BLUE),
        ("algorithms/topk_heap.py", PINK),
        ("algorithms/quicksort.py", PINK),
        ("8 REST endpoints  /api/*", BLUE)], "#E8F0FF")

    fe = group(ax, 12.6, yt, 2.2, "FRONTEND  (frontend/)", [
        ("index.html", YELLOW),
        ("css/style.css", YELLOW),
        ("api.js / app.js", YELLOW),
        ("charts.js -> Chart.js", YELLOW),
        ("map.js -> Leaflet", YELLOW)], "#FFF3D6")

    # user
    ax.add_patch(FancyBboxPatch((12.9, 9.4), 1.6, 0.5, boxstyle="round,pad=0.04",
                 fc=DARK, ec=DARK))
    ax.text(13.7, 9.65, "User / Analyst", ha="center", va="center",
            fontsize=8.5, color="white")
    arrow(ax, (13.7, 9.4), (13.7, fe["y_top"] + 0.02), color=DARK)

    # main flow
    def mid(g): return g["mid_y"]
    arrow(ax, (src["x"] + src["w"], mid(src)), (etl["x"], mid(src)), color=DARK)
    ax.text((src["x"] + src["w"] + etl["x"]) / 2, mid(src) + 0.2, "read",
            ha="center", fontsize=7.5)

    arrow(ax, (etl["x"] + etl["w"], mid(etl)), (db["x"], mid(etl)), color="#2E8B57")
    ax.text((etl["x"] + etl["w"] + db["x"]) / 2, mid(etl) + 0.2, "COPY",
            ha="center", fontsize=7.5, color="#2E8B57")

    # backend <-> database (query)
    arrow(ax, (be["x"], mid(be) + 0.2), (db["x"] + db["w"], mid(be) + 0.2),
          color=BLUEC)
    ax.text((be["x"] + db["x"] + db["w"]) / 2, mid(be) + 0.4, "SQL",
            ha="center", fontsize=7.5, color=BLUEC)

    # backend <-> frontend (serve static + JSON)
    arrow(ax, (be["x"] + be["w"], mid(be) + 0.25), (fe["x"], mid(be) + 0.25),
          color=DARK)
    arrow(ax, (fe["x"], mid(be) - 0.25), (be["x"] + be["w"], mid(be) - 0.25),
          color=DARK)
    ax.text((be["x"] + be["w"] + fe["x"]) / 2, mid(be) + 0.45, "static",
            ha="center", fontsize=7, color=DARK)
    ax.text((be["x"] + be["w"] + fe["x"]) / 2, mid(be) - 0.62, "/api JSON",
            ha="center", fontsize=7, color=DARK)

    # audit outputs (dashed, below ETL)
    ax.add_patch(FancyBboxPatch((3.0, 1.0), 3.0, 0.7, boxstyle="round,pad=0.04",
                 fc=PINK, ec=DARK, lw=1.2))
    ax.text(4.5, 1.35, "exclusion_log.csv  ·  etl_summary.json",
            ha="center", va="center", fontsize=7.6)
    arrow(ax, (4.5, etl["y_bot"]), (4.5, 1.7), color="#C0392B", ls="--", lw=1.4)
    ax.text(5.0, (etl["y_bot"] + 1.7) / 2, "audit", fontsize=7, color="#C0392B")

    # zones.geojson served to map.js (dashed long arrow along the bottom)
    arrow(ax, (db["x"] + db["w"] / 2, db["y_bot"]), (db["x"] + db["w"] / 2, 0.6),
          color="#2D6CDF", ls="--", lw=1.2)
    arrow(ax, (db["x"] + db["w"] / 2, 0.55), (fe["x"] + fe["w"] / 2, 0.55),
          color="#2D6CDF", ls="--", lw=1.2)
    arrow(ax, (fe["x"] + fe["w"] / 2, 0.6), (fe["x"] + fe["w"] / 2, fe["y_bot"]),
          color="#2D6CDF", ls="--", lw=1.2)
    ax.text((db["x"] + fe["x"]) / 2, 0.38, "zones.geojson served as static file to map.js",
            ha="center", fontsize=7, color="#2D6CDF")

    ax.set_title("NYC Yellow Taxi Trip Explorer  -  Complete System (all components)",
                 fontweight="bold", fontsize=14, pad=14)
    fig.tight_layout()
    p = os.path.join(ASSETS, "arch5_overview.png")
    fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
    return p


def build_pdf(png):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(png).size
    page = landscape(letter)
    margin = 0.4 * inch
    avail_w = page[0] - 2 * margin
    img = Image(png, width=avail_w, height=avail_w * ih / iw)
    doc = SimpleDocTemplate(os.path.join(HERE, "system_overview.pdf"), pagesize=page,
                            topMargin=margin, bottomMargin=margin,
                            leftMargin=margin, rightMargin=margin)
    doc.build([img])


if __name__ == "__main__":
    png = build_png()
    build_pdf(png)
    print("wrote docs/system_overview.pdf and docs/arch_assets/arch5_overview.png")
