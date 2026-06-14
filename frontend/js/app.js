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
