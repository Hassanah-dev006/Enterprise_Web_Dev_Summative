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