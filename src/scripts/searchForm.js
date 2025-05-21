export function searchFormComponent() {
  return {
    showFilter: (window.__initialSearchKeyword || '').trim().length > 0,
    maxCalories: window.__initialMaxCalories || 1000,

    init() {
      // console.log("Search form initialized");
    }
  };
}
