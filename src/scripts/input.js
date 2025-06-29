import Alpine from 'alpinejs';
import { Chart, registerables } from 'chart.js';
import flatpickr from 'flatpickr';
import htmx from 'htmx.org';
import cartItem from './carts/cartItemEdit.js';
import { DatePicker } from './datePicker.js';
import storeDistance from './geocoding/storeDistance.js';
import { initCategorySort } from './stores/categorySort.js';
import { initProductSort } from './stores/productSort.js';
import { initCategorySidebarActive } from './stores/selectCategory.js';
import { initTabs } from './stores/selectTab.js';

Chart.register(...registerables);
window.Chart = Chart;

window.Alpine = Alpine;
window.htmx = htmx;
window.flatpickr = flatpickr;

Alpine.data('dataPicker', DatePicker);

window.cartItem = cartItem;

initProductSort();
initCategorySort();
initTabs();
initCategorySidebarActive();

Alpine.data('storeDistance', storeDistance);
Alpine.start();
