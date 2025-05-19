import Alpine from 'alpinejs';
import flatpickr from 'flatpickr';
import 'htmx.org';
import { initPickupTimePicker } from './flatpickr/main.js';
import { copyToClipboard } from './utils/clipboard.js';

window.Alpine = Alpine;
window.flatpickr = flatpickr;
window.copyToClipboard = copyToClipboard;

Alpine.data('clipboard', copyToClipboard);

initPickupTimePicker('#id_pickup_time', 'healthy_style');
initPickupTimePicker('#id_date_of_birth', 'cool_style', {
  enableTime: false,
  dateFormat: 'Y-m-d',
  altFormat: 'Y年m月d日',
  altInput: true,
});
Alpine.start();
