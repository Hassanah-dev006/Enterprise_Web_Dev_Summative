/* Dashboard orchestration: filters → API → charts/map/table. */
const App = {
  filters: {},
  page: 1,

  async init() {
    await ZoneMap.init();
    await this.populateBoroughs();
    this.bindEvents();
    this.readFilters();
    this.refreshAll();
  },

  bindEvents() {
    document.getElementById("f-apply").onclick = () => {
      this.readFilters();
      this.page = 1;
      this.refreshAll();
    };
    document.getElementById("f-reset").onclick = () => {
      document.querySelectorAll(".filters input").forEach((i) => (i.value = i.defaultValue));
      document.getElementById("f-borough").value = "";
      this.readFilters();
      this.page = 1;
      this.refreshAll();
    };
    document.getElementById("zone-metric").onchange = () => this.refreshZones();
    document.getElementById("t-sort").onchange = () => this.refreshTrips();
    document.getElementById("t-order").onchange = () => this.refreshTrips();
    document.getElementById("t-prev").onclick = () => { if (this.page > 1) { this.page--; this.refreshTrips(); } };
    document.getElementById("t-next").onclick = () => { this.page++; this.refreshTrips(); };
  },

  readFilters() {
    const v = (id) => document.getElementById(id).value;
    this.filters = {
      start: v("f-start"),
      end: v("f-end") ? `${v("f-end")}T23:59:59` : "",
      hour_min: v("f-hour-min"),
      hour_max: v("f-hour-max"),
      borough: v("f-borough"),
      fare_min: v("f-fare-min"),
      fare_max: v("f-fare-max"),
      dist_min: v("f-dist-min"),
      dist_max: v("f-dist-max"),
    };
  },

  async populateBoroughs() {
    const zones = await API.zones();
    const boroughs = [...new Set(zones.map((z) => z.borough))].sort();
    const sel = document.getElementById("f-borough");
    boroughs.forEach((b) => sel.add(new Option(b, b)));
  },

  async refreshAll() {
    this.refreshSummary();
    this.refreshHourly();
    this.refreshZones();
    this.refreshTrips();
  },

  async refreshSummary() {
    const s = await API.summary();
    const fmt = (n) => Number(n).toLocaleString();
    document.getElementById("kpi-trips").textContent = fmt(s.trips);
    document.getElementById("kpi-revenue").textContent = `$${fmt(Math.round(s.total_revenue || 0))}`;
    document.getElementById("kpi-fare").textContent = `$${s.avg_fare ?? "–"}`;
    document.getElementById("kpi-distance").textContent = `${s.avg_distance ?? "–"} mi`;
    document.getElementById("kpi-duration").textContent = `${s.avg_duration_min ?? "–"} min`;
    document.getElementById("kpi-tip").textContent = `${s.avg_tip_pct ?? "–"}%`;
  },

  async refreshHourly() {
    Charts.renderHourly(await API.hourly());
  },

  async refreshZones() {
    const metric = document.getElementById("zone-metric").value;
    const [top, ranking] = await Promise.all([
      API.topZones(metric, 10),
      API.zoneRanking(metric),
    ]);
    Charts.renderZones(top, metric);
    ZoneMap.render(ranking, metric);
  },