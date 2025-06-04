export function searchFormComponent() {
  return {
    showFilter: false,
    keyword: window.__initialSearchKeyword || '',
    maxCalories: typeof window.__initialMaxCalories === 'number' ? window.__initialMaxCalories : 0,

    get isValidSearch() {
      return this.keyword.trim().length > 0 || this.maxCalories > 0;
    },
  };
}
