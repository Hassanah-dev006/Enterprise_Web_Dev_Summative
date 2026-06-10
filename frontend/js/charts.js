/* Chart.js renderers. */
const Charts = {
  hourly: null,
  zones: null,

  renderHourly(rows) {
    const ctx = document.getElementById("chart-hourly");
    this.hourly?.destroy();
    this.hourly = new Chart(ctx, {
      data: {
        labels: rows.map((r) => `${r.hour}:00`),
        datasets: [
          {
            type: "bar",
            label: "Trips",
            data: rows.map((r) => r.trips),
            backgroundColor: "rgba(247, 183, 51, 0.7)",
            yAxisID: "y",
          },
          {
            type: "line",
            label: "Avg speed (mph)",
            data: rows.map((r) => r.avg_speed_mph),
            borderColor: "#1f2430",
            tension: 0.3,
            yAxisID: "y2",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: { title: { display: true, text: "Trips" } },
          y2: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "mph" } },
        },
      },
    });
  },

  renderZones(rows, metric) {
    const ctx = document.getElementById("chart-zones");
    this.zones?.destroy();
    this.zones = new Chart(ctx, {
      type: "bar",
      data: {
        labels: rows.map((r) => r.zone_name),
        datasets: [{
          label: metric.replaceAll("_", " "),
          data: rows.map((r) => r[metric]),
          backgroundColor: "rgba(31, 36, 48, 0.8)",
        }],
      },
      options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } } },
    });
  },
};
