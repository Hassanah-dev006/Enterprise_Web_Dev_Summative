"""Build the technical report PDF (and its charts) from the run's real figures.

Usage:  python docs/build_report.py
Outputs: docs/assets/*.png  and  docs/report.pdf

Figures are the actual aggregates produced by the Jan-2019 pipeline run
(see docs/gather_stats.py). Editing them here keeps the report reproducible.
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
ASSETS = os.path.join(HERE, "assets")
os.makedirs(ASSETS, exist_ok=True)

YELLOW = "#F7B733"
DARK = "#1F2430"
RED = "#C0392B"

# ──────────────────────────────── Data ────────────────────────────────
HOURLY = [
    (0, 197126, 14.9), (1, 141430, 14.9), (2, 103240, 15.1), (3, 73316, 16.0),
    (4, 57097, 18.4), (5, 70253, 19.0), (6, 168025, 15.4), (7, 289357, 12.3),
    (8, 355915, 10.3), (9, 348647, 10.3), (10, 343986, 10.5), (11, 357149, 10.3),
    (12, 381241, 10.5), (13, 383386, 10.8), (14, 410527, 10.5), (15, 428481, 10.2),
    (16, 397167, 10.5), (17, 444214, 10.2), (18, 490085, 10.4), (19, 452619, 11.5),
    (20, 403035, 12.7), (21, 390298, 13.3), (22, 351357, 13.7), (23, 267943, 14.5),
]
REVENUE_ZONES = [
    ("JFK Airport", 10.20, True), ("LaGuardia Airport", 7.20, True),
    ("Midtown Center", 4.31, False), ("Times Sq/Theatre", 3.85, False),
    ("Midtown East", 3.75, False), ("UES South", 3.72, False),
    ("UES North", 3.71, False), ("Penn Station", 3.57, False),
    ("Murray Hill", 3.19, False), ("Clinton East", 3.10, False),
]
PAYMENTS = [("Credit card", 5.24, True), ("Cash", 2.01, False),
            ("Unknown", 0.028, False), ("No charge", 0.020, False),
            ("Dispute", 0.006, False)]
EXCLUSIONS = [
    ("unknown_location_id", 187558), ("implausible_passenger_count", 117438),
    ("implausible_duration", 94303), ("implausible_distance", 71145),
    ("implausible_fare", 9804), ("implausible_speed", 6556),
    ("pickup_outside_month", 537), ("implausible_total", 30),
]
BOROUGH = [
    ("Manhattan", "6,766,044", "$10.59", "21.9%"),
    ("Queens", "436,148", "$35.07", "20.6%"),
    ("Brooklyn", "86,830", "$18.88", "14.1%"),
    ("Bronx", "16,559", "$27.18", "2.1%"),
    ("Staten Island", "290", "$46.50", "5.5%"),
    ("EWR", "23", "$63.63", "56.7%"),
]


# ──────────────────────────────── Charts ──────────────────────────────
def chart_demand_speed():
    hours = [h for h, _, _ in HOURLY]
    trips = [t / 1000 for _, t, _ in HOURLY]
    speed = [s for _, _, s in HOURLY]
    fig, ax1 = plt.subplots(figsize=(8, 3.6))
    ax1.bar(hours, trips, color=YELLOW, label="Trips (thousands)")
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("Trips (thousands)", color=DARK)
    ax1.set_xticks(range(0, 24, 2))
    ax2 = ax1.twinx()
    ax2.plot(hours, speed, color=DARK, marker="o", ms=3, lw=2,
             label="Avg speed (mph)")
    ax2.set_ylabel("Avg speed (mph)", color=DARK)
    ax2.set_ylim(8, 20)
    ax1.set_title("Hourly demand vs. average speed — congestion signature",
                  fontweight="bold")
    fig.tight_layout()
    p = os.path.join(ASSETS, "fig1_demand_speed.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_airport_revenue():
    labels = [z for z, _, _ in REVENUE_ZONES][::-1]
    vals = [v for _, v, _ in REVENUE_ZONES][::-1]
    cols = [RED if a else YELLOW for _, _, a in REVENUE_ZONES][::-1]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.barh(labels, vals, color=cols)
    ax.set_xlabel("Total revenue ($ millions)")
    ax.set_title("Top pickup zones by revenue — airports lead (red)",
                 fontweight="bold")
    for i, v in enumerate(vals):
        ax.text(v + 0.1, i, f"${v:.1f}M", va="center", fontsize=8)
    ax.set_xlim(0, 11.5)
    fig.tight_layout()
    p = os.path.join(ASSETS, "fig2_airport_revenue.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_payment_tip():
    labels = [p for p, _, _ in PAYMENTS]
    vals = [v for _, v, _ in PAYMENTS]
    cols = [YELLOW if c else "#B8BCC6" for _, _, c in PAYMENTS]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.bar(labels, vals, color=cols)
    ax.set_ylabel("Trips (millions)")
    ax.set_title("Payment mix — tips recorded for card only (21.6% avg)",
                 fontweight="bold")
    ax.text(1, 2.2, "Cash tips (28% of trips)\nnot recorded -> $0",
            ha="center", fontsize=9, color=RED)
    fig.tight_layout()
    p = os.path.join(ASSETS, "fig3_payment_tip.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


def chart_architecture():
    fig, ax = plt.subplots(figsize=(8, 2.6))
    ax.set_xlim(-0.1, 10.3); ax.set_ylim(0, 3); ax.axis("off")
    boxes = [
        (0.2, "Raw data\nparquet · CSV\nshapefile"),
        (2.2, "ETL pipeline\nclean · features\nload (pyarrow)"),
        (4.4, "PostgreSQL\nstar schema\n7 indexes"),
        (6.6, "Flask API\n8 endpoints\ncustom algos"),
        (8.6, "Dashboard\nChart.js\nLeaflet"),
    ]
    for x, label in boxes:
        ax.add_patch(FancyBboxPatch((x, 1.0), 1.4, 1.0,
                     boxstyle="round,pad=0.05", fc=YELLOW, ec=DARK, lw=1.5))
        ax.text(x + 0.7, 1.5, label, ha="center", va="center", fontsize=8.5)
    for x in (1.6, 3.8, 6.0, 8.2):
        ax.add_patch(FancyArrowPatch((x, 1.5), (x + 0.6, 1.5),
                     arrowstyle="-|>", mutation_scale=14, color=DARK, lw=1.5))
    ax.set_title("System architecture", fontweight="bold", fontsize=11)
    fig.tight_layout()
    p = os.path.join(ASSETS, "fig0_architecture.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    return p


# ──────────────────────────────── PDF ─────────────────────────────────
def build_pdf(figs):
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5,
                          leading=13, spaceAfter=6)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13,
                        textColor=colors.HexColor(DARK), spaceBefore=10,
                        spaceAfter=4)
    title = ParagraphStyle("t", parent=styles["Title"], fontSize=18,
                           textColor=colors.HexColor(DARK))
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8)
    cap = ParagraphStyle("cap", parent=styles["Italic"], fontSize=8,
                         textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8)

    def img(path, w=6.4):
        from PIL import Image as PILImage
        iw, ih = PILImage.open(path).size
        return Image(path, width=w * inch, height=w * inch * ih / iw)

    s = []
    s.append(Paragraph("NYC Yellow Taxi Trip Explorer", title))
    s.append(Paragraph("Technical Report &nbsp;|&nbsp; January 2019 &nbsp;|&nbsp; "
                       "7.31M cleaned trips", sub))

    s.append(Paragraph("1. Problem Framing and Dataset Analysis", h1))
    s.append(Paragraph(
        "The dataset is the NYC Taxi &amp; Limousine Commission (TLC) Yellow Taxi "
        "record for January 2019: <b>7,696,617</b> raw trips across 18 fields, joined "
        "to <i>taxi_zone_lookup</i> (263 zones) and a zone boundary shapefile. The raw "
        "files form a fact/dimension environment - trip-level facts plus categorical "
        "and spatial dimensions. We integrated them in a streaming pipeline: trip "
        "parquet is read in 200k-row batches, enriched, and bulk-loaded; zone polygons "
        "are reprojected (EPSG:2263 to WGS84) into the zone dimension.", body))
    s.append(Paragraph(
        "<b>Data integrity.</b> Eight rules removed <b>390,723</b> records (5.1%). "
        "Thresholds reflect physical and contractual limits: trip duration 1-720 min, "
        "distance 0.1-100 mi, fare $0.01-$500, average speed &le; 80 mph, passengers "
        "1-6, and pickup timestamp within the month. Duplicates and rows missing "
        "critical fields were dropped; out-of-spec categorical codes (e.g. VendorID 4, "
        "RatecodeID 99) were preserved where legitimate and otherwise coerced to NULL "
        "so foreign keys hold.", body))
    s.append(_excl_table())
    s.append(Paragraph(
        "<b>Unexpected observation.</b> The single largest exclusion bucket "
        "(<b>187,558</b> trips) was <i>unknown location IDs</i> - codes 264/265, which "
        "the TLC uses for \"Unknown\" and trips leaving the zone system. These have no "
        "polygon in the shapefile. This directly shaped two design choices: the "
        "choropleth had to tolerate zones with no matching trips, and spatial analysis "
        "excludes these rows rather than mapping them to a fake location. A second "
        "surprise - 117,438 trips with passenger_count = 0 - is a known meter/data-entry "
        "artifact and was likewise excluded.", body))

    s.append(Paragraph("2. System Architecture and Design Decisions", h1))
    s.append(img(figs["arch"]))
    s.append(Paragraph(
        "<b>Stack.</b> A Python ETL (pandas + pyarrow, streamed in batches and loaded "
        "with PostgreSQL COPY) keeps cleaning and loading in one language and never "
        "holds the full 7.7M rows in memory. <b>PostgreSQL</b> was chosen over SQLite "
        "for real indexing and referential integrity at this scale. <b>Flask</b> serves "
        "both the JSON API and the static dashboard, so there is a single process to "
        "run. The frontend is vanilla <b>HTML/CSS/JS</b> with Chart.js and Leaflet - "
        "matching the brief literally while letting Leaflet render the zone GeoJSON as "
        "an interactive choropleth.", body))
    s.append(Paragraph(
        "<b>Schema.</b> A star schema centers on <i>fact_trip</i> with four dimensions "
        "(zone, vendor, rate code, payment type). Seven indexes target the dashboard's "
        "filter patterns (pickup time, pickup/dropoff zone, hour, fare, distance, "
        "payment). The hour/day-of-week/weekend keys are denormalized onto the fact "
        "table - a deliberate storage-for-speed trade-off that turns the most common "
        "group-bys into single-column scans. Zone geometry is stored as JSONB and also "
        "emitted once as a static GeoJSON file the map loads directly.", body))
    s.append(Paragraph(
        "<b>Trade-offs.</b> Chunked streaming trades a little speed for bounded memory; "
        "COPY over per-row INSERT trades flexibility for a ~50x load speedup; coercing "
        "unknown categorical IDs to NULL trades completeness for guaranteed integrity; "
        "and excluding 5% of rows trades coverage for a clean, defensible analytic base.",
        body))

    s.append(Paragraph("3. Algorithmic Logic and Data Structures", h1))
    s.append(Paragraph(
        "Two structures are implemented by hand (no heapq, Counter, sorted, or "
        "sort_values) and both run inside live API endpoints.", body))
    s.append(Paragraph("<b>3.1 Top-K min-heap</b> - powers <i>/api/stats/top-zones</i>. "
        "To rank the K busiest zones out of 263 without sorting everything, we keep a "
        "binary min-heap of size K; each candidate that beats the heap's minimum "
        "replaces the root and sifts down.", body))
    s.append(_code(
        "build empty min-heap H            # ordered by metric\n"
        "for each zone z in zones:\n"
        "    if size(H) < K:  push(H, z)\n"
        "    elif metric(z) > metric(peek(H)):\n"
        "        replace_root(H, z); sift_down(H, 0)\n"
        "return drain(H) reversed           # K items, descending"))
    s.append(Paragraph(
        "<b>Complexity:</b> time O(n log K) - n items, each heap op O(log K); "
        "space O(K). A full sort would be O(n log n) time and O(n) space, so the heap "
        "wins whenever K &lt;&lt; n (here 10 of 263).", body))
    s.append(Paragraph("<b>3.2 Quicksort (median-of-three)</b> - powers "
        "<i>/api/stats/zone-ranking</i>, which orders all 263 zones to colour the map. "
        "An in-place quicksort picks the pivot as the median of first/middle/last and "
        "recurses into the smaller partition first to bound stack depth.", body))
    s.append(_code(
        "quicksort(A, lo, hi):\n"
        "    while lo < hi:\n"
        "        p = partition(A, lo, hi)        # median-of-three pivot\n"
        "        if p-lo < hi-p: quicksort(A, lo, p-1); lo = p+1\n"
        "        else:           quicksort(A, p+1, hi); hi = p-1"))
    s.append(Paragraph(
        "<b>Complexity:</b> time O(n log n) average, O(n^2) worst case (made unlikely by "
        "the median-of-three pivot on real, partially-ordered fare/zone data); space "
        "O(log n) for the recursion stack. Both structures were validated against "
        "Python's built-ins over 200 randomized trials.", body))

    s.append(Paragraph("4. Insights and Interpretation", h1))

    s.append(Paragraph("<b>Insight 1 - Congestion is written into the hourly curve.</b>",
                       body))
    s.append(img(figs["demand"]))
    s.append(Paragraph("Fig. 1 - Trips per hour (bars) against average speed (line).", cap))
    s.append(Paragraph(
        "Derived from a GROUP BY pickup_hour over the engineered <i>avg_speed_mph</i> "
        "feature. Demand peaks at 6 PM (<b>490,085</b> trips) precisely when average "
        "speed bottoms out near <b>10.4 mph</b>; the 5 AM lull moves at <b>19.0 mph</b> "
        "- nearly double. The inverse relationship is a clean congestion signature: more "
        "taxis on the road coincide with slower roads. Notably fares do not spike at "
        "peak demand, because the meter charges for time-in-traffic regardless, so "
        "congestion is paid in minutes rather than surge pricing.", body))

    s.append(Paragraph("<b>Insight 2 - Two airports are the revenue engine.</b>", body))
    s.append(img(figs["airport"]))
    s.append(Paragraph("Fig. 2 - Top pickup zones by total revenue; airports in red.", cap))
    s.append(Paragraph(
        "JFK (<b>$10.2M</b>) and LaGuardia (<b>$7.2M</b>) are the top two revenue zones "
        "yet appear nowhere in the top ten by <i>trip count</i> - they convert volume "
        "into value through long, flat-rate fares (JFK averages <b>$45.92</b> per trip "
        "vs. the <b>$12.19</b> city-wide mean). At borough level the same effect "
        "dominates: Queens' average fare (<b>$35.07</b>) is over 3x Manhattan's "
        "(<b>$10.59</b>). For an operator, this means airport supply is disproportionately "
        "valuable, and demand modelling should treat airport zones as a separate regime.",
        body))

    s.append(Paragraph("<b>Insight 3 - \"Average tip\" really means \"average card tip\".</b>",
                       body))
    s.append(img(figs["payment"]))
    s.append(Paragraph("Fig. 3 - Payment mix; cash tips are never recorded.", cap))
    s.append(Paragraph(
        "Credit-card trips tip <b>21.6%</b> on average, but the <b>2.01M</b> cash trips "
        "(28% of the total) record no tip at all - the meter only captures card tips. "
        "Any naive average over all trips silently measures card users only. This also "
        "explains odd borough numbers: the Bronx's 2.1% \"tip rate\" reflects a high "
        "cash share, not stinginess. The design lesson - surfaced in our feature "
        "engineering - is that <i>tip_pct</i> is only meaningful conditioned on "
        "payment_type = card, and the dashboard labels it accordingly.", body))
    s.append(_borough_table())

    s.append(Paragraph("5. Reflection and Future Work", h1))
    s.append(Paragraph(
        "<b>Technical challenges.</b> Real-world friction dominated: the TLC parquet "
        "stores integer IDs as floats (forcing a nullable-int cast before COPY), "
        "undocumented VendorID 4 / RatecodeID 99 broke foreign keys until the "
        "dimensions and a coercion step were added, and macOS quietly occupies port "
        "5000 with AirPlay Receiver (the API moved to 5001). Streaming 7.7M rows within "
        "memory limits required batching rather than a single read.", body))
    s.append(Paragraph(
        "<b>Team challenges.</b> Because the system is a multi-stage pipeline, the "
        "hardest coordination problem was agreeing on contracts early: the cleaned "
        "column names and types had to be frozen before database and API work could "
        "proceed in parallel, so a single change to a cleaning rule rippled into the "
        "schema and the endpoints. Environment consistency was a recurring friction "
        "point - Python version and dependency mismatches across machines, a shared "
        "database that had to be re-seeded after every schema change, and a multi-"
        "hundred-megabyte raw file that could not live in version control. We split the "
        "work along the architecture seams (ETL, database/API, frontend/report) and "
        "relied on small, frequent commits to keep the integration points visible; the "
        "main lesson was to lock the data contract and schema first, since they are the "
        "interfaces every other component depends on.", body))
    s.append(Paragraph(
        "<b>Future work.</b> Extend beyond one month to expose seasonality; adopt "
        "PostGIS for true point-in-polygon spatial joins instead of pre-mapped zone "
        "IDs; add a demand-forecasting model keyed on the hour/zone features; cache hot "
        "aggregates; containerise with Docker for one-command deployment; and add "
        "trip-level drill-down from the map.", body))

    doc = SimpleDocTemplate(os.path.join(HERE, "report.pdf"), pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch)
    doc.build(s)


def _excl_table():
    data = [["Exclusion rule", "Records"]] + [[r, f"{n:,}"] for r, n in EXCLUSIONS]
    data.append(["TOTAL excluded (5.1%)", "390,723"])
    t = Table(data, colWidths=[3.6 * inch, 1.4 * inch])
    t.setStyle(_tbl_style())
    return t


def _borough_table():
    data = [["Borough", "Trips", "Avg fare", "Avg card tip"]] + [list(r) for r in BOROUGH]
    t = Table(data, colWidths=[1.7 * inch, 1.5 * inch, 1.2 * inch, 1.4 * inch])
    t.setStyle(_tbl_style())
    return t


def _tbl_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBF6E7")]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor(YELLOW)),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4D8E0")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])


def _code(text):
    style = ParagraphStyle("code", fontName="Courier", fontSize=8, leading=10,
                           backColor=colors.HexColor("#F4F5F7"),
                           borderPadding=6, spaceBefore=2, spaceAfter=8,
                           leftIndent=4)
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), style)


if __name__ == "__main__":
    figs = {
        "arch": chart_architecture(),
        "demand": chart_demand_speed(),
        "airport": chart_airport_revenue(),
        "payment": chart_payment_tip(),
    }
    build_pdf(figs)
    print("wrote docs/report.pdf and docs/assets/*.png")
