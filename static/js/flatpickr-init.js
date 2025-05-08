flatpickr('#id_pickup_time', {
  enableTime: true,
  dateFormat: 'Y-m-d\\TH:i',
  time_24hr: true,
  minuteIncrement: 10,
  altInput: true,
  altFormat: 'Y年m月d日 H:i',
  scrollInput: true,
  shorthandCurrentMonth: true,
  locale: 'zh_tw',

  minDate: document.querySelector('#id_pickup_time').min,
  maxDate: document.querySelector('#id_pickup_time').max,

  onReady: function (selectedDates, dateStr, instance) {
    // 用 Tailwind CSS 修改 altInput 的樣式
    instance.altInput.classList.add(
      'px-2',
      'py-2',
      'border',
      'border-[#66bb6a]',
      'rounded-lg',
      'shadow-md',
      'focus:ring-2',
      'focus:ring-[#66bb6a]',
      'bg-[#fff8e1]',
      'text-[#66bb6a]',
      'hover:border-[#66bb6a]',
      'cursor-pointer',
      'focus:outline-none',
    );
  },
});
