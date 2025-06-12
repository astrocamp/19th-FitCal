import { initPickupTimePicker } from './flatpickr/main.js';

export const DatePicker = () => ({
  init() {
    initPickupTimePicker('#id_pickup_time', 'healthy_style');
    initPickupTimePicker('#id_date_of_birth', 'healthy_style', {
      enableTime: false,
      dateFormat: 'Y-m-d',
      altFormat: 'Y年m月d日',
      altInput: true,
    });
  },
});
