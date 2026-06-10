/* Thin client for the Flask API. */
const API = {
  base: "/api",

  /** Build query string from the current filter state. */
  qs(extra = {}) {
    const params = { ...App.filters, ...extra };
    const clean = Object.fromEntries(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    );
    return new URLSearchParams(clean).toString();
  },

  async get(path, extra = {}) {
    const res = await fetch(`${this.base}${path}?${this.qs(extra)}`);
    if (!res.ok) throw new Error(`${path} → ${res.status}`);
    return res.json();
  },

  summary() { return this.get("/stats/summary"); },
  hourly() { return this.get("/stats/hourly"); },
  topZones(metric, k = 10) { return this.get("/stats/top-zones", { metric, k }); },
  zoneRanking(metric) { return this.get("/stats/zone-ranking", { metric }); },
  trips(page, sort, order) { return this.get("/trips", { page, sort, order, per_page: 25 }); },
  zones() { return this.get("/zones"); },
};
