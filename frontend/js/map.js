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
  