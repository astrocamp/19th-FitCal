import Alpine from 'alpinejs';
import { Chart, registerables } from 'chart.js';
import flatpickr from 'flatpickr';
import htmx from 'htmx.org';
import cartItem from './carts/cartItemEdit.js';
import { initPickupTimePicker } from './flatpickr/main.js';
import { searchFormComponent } from './searchForm.js';
import { initCategorySort } from './stores/categorySort.js';
import { initProductSort } from './stores/productSort.js';
import { copyToClipboard } from './utils/clipboard.js';
Chart.register(...registerables);
window.Chart = Chart;

window.Alpine = Alpine;
window.htmx = htmx;
window.flatpickr = flatpickr;
window.searchFormComponent = searchFormComponent;
window.copyToClipboard = copyToClipboard;

Alpine.data('clipboard', copyToClipboard);

initPickupTimePicker('#id_pickup_time', 'healthy_style');
initPickupTimePicker('#id_date_of_birth', 'cool_style', {
  enableTime: false,
  dateFormat: 'Y-m-d',
  altFormat: 'Y年m月d日',
  altInput: true,
});

window.cartItem = cartItem;

initProductSort();
initCategorySort();

Alpine.start();
