export function searchFormComponent() {
  return {
    showFilter: (window.__initialSearchKeyword || '').trim().length > 0,
    keyword: window.__initialSearchKeyword || '',
    maxCalories: typeof window.__initialMaxCalories === 'number' ? window.__initialMaxCalories : 0,

    init() {
      // console.log("Search form initialized");
    },

    get isValidSearch() {
      return this.keyword.trim().length > 0 || this.maxCalories > 0;
    },
  };
}
