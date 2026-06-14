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