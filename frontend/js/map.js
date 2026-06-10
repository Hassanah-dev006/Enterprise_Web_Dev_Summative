/* Leaflet choropleth of pickup intensity per taxi zone. */
const ZoneMap = {
  map: null,
  layer: null,
  geojson: null, // loaded once from js/zones.geojson (built by the ETL)

  async init() {
    this.map = L.map("map").setView([40.73, -73.95], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap",
    }).addTo(this.map);
    const res = await fetch("js/zones.geojson");
    if (res.ok) this.geojson = await res.json();
  },

  /** Color zones by metric value (quantile-ish linear scale). */
  render(ranking, metric) {
    if (!this.geojson) return;
    const byId = Object.fromEntries(ranking.map((z) => [z.location_id, z]));
    const values = ranking.map((z) => Number(z[metric]) || 0);
    const max = Math.max(...values, 1);

    this.layer?.remove();
    this.layer = L.geoJSON(this.geojson, {
      style: (f) => {
        const v = Number(byId[f.properties.location_id]?.[metric]) || 0;
        return {
          fillColor: this.color(v / max),
          fillOpacity: 0.65,
          color: "#555",
          weight: 0.5,
        };
      },
      onEachFeature: (f, layer) => {
        const z = byId[f.properties.location_id];
        layer.bindPopup(
          `<b>${f.properties.zone}</b> (${f.properties.borough})<br>` +
            (z ? `${metric.replaceAll("_", " ")}: ${z[metric]}` : "no trips")
        );
      },
    }).addTo(this.map);
  },

  color(t) {
    // white → yellow → dark red
    const stops = ["#ffffe0", "#f7b733", "#e8590c", "#7f1d1d"];
    const i = Math.min(stops.length - 1, Math.floor(t * stops.length));
    return stops[i];
  },
};
