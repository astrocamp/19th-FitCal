import { initPickupTimePicker } from './flatpickr/main.js';

export const DatePicker = () => ({
  init() {
    const openingTime = this.$el.dataset.openingTime;
    const closingTime = this.$el.dataset.closingTime;

    initPickupTimePicker('#id_pickup_time', 'healthy_style', {
      minTime: openingTime,
      maxTime: closingTime,
      enableTime: true,
      dateFormat: 'Y-m-d\\TH:i',
      minuteIncrement: 10,
      altInput: true,
      altFormat: 'Y年m月d日 H:i',
    });
    initPickupTimePicker('#id_date_of_birth', 'healthy_style', {
      enableTime: false,
      dateFormat: 'Y-m-d',
      altFormat: 'Y年m月d日',
      altInput: true,
    });
  },
});
