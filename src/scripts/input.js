import Alpine from 'alpinejs';
import flatpickr from 'flatpickr';
import 'htmx.org';
import { StyledFlatpickr } from './components/StyledFlatpickr.js';

window.Alpine = Alpine;
window.flatpickr = flatpickr;
window.StyledFlatpickr = StyledFlatpickr;

Alpine.start();
