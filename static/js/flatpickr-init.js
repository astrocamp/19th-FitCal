class StyledFlatpickr {
  constructor(selector, stylePreset = 'default', customOptions = {}) {
    this.selector = selector;
    this.stylePreset = stylePreset;
    this.customOptions = customOptions;

    this.stylePresets = {
      healthy_style: {
        altInputClasses: [
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
        ],
      },
      cool_style: {
        altInputClasses: [
          'px-2',
          'py-2',
          'border',
          'border-blue-500',
          'rounded-md',
          'bg-blue-50',
          'text-blue-700',
          'focus:ring-2',
          'focus:ring-blue-400',
          'hover:border-blue-500',
          'cursor-pointer',
        ],
      },
      default: {
        altInputClasses: [],
      },
    };

    this.init();
  }

  init() {
    const inputElement = document.querySelector(this.selector);
    if (!inputElement) {
      console.error(`Element ${this.selector} not found.`);
      return;
    }

    const minDate = inputElement.min || null;
    const maxDate = inputElement.max || null;

    const style = this.stylePresets[this.stylePreset] || this.stylePresets['default'];

    const defaultOptions = {
      enableTime: false,
      time_24hr: true,
      dateFormat: 'Y-m-d',
      altInput: true,
      altFormat: 'Y年m月d日',
      scrollInput: true,
      shorthandCurrentMonth: true,
      locale: 'zh_tw',
      minDate,
      maxDate,
      onReady: (selectedDates, dateStr, instance) => {
        if (instance.altInput && style.altInputClasses.length) {
          instance.altInput.classList.add(...style.altInputClasses);
        }
      },
    };

    // 合併自訂選項
    const options = { ...defaultOptions, ...this.customOptions };

    flatpickr(this.selector, options);
  }
}

new StyledFlatpickr('#id_pickup_time', 'healthy_style', {
  enableTime: true,
  dateFormat: 'Y-m-d\\TH:i',
  altFormat: 'Y年m月d日',
  altInput: true,
  altFormat: 'Y年m月d日 H:i',
});

new StyledFlatpickr('input[type="datetime-local"]');

// 這是原本的 flatpickr 初始化程式碼
// 如果需要使用原本的樣式，可以取消註解這段程式碼
// flatpickr('#id_pickup_time', {
//   enableTime: true,
//   dateFormat: 'Y-m-d\\TH:i',
//   time_24hr: true,
//   minuteIncrement: 10,
//   altInput: true,
//   altFormat: 'Y年m月d日 H:i',
//   scrollInput: true,
//   shorthandCurrentMonth: true,
//   locale: 'zh_tw',

//   minDate: document.querySelector('#id_pickup_time').min,
//   maxDate: document.querySelector('#id_pickup_time').max,

//   onReady: function (selectedDates, dateStr, instance) {
//     // 用 Tailwind CSS 修改 altInput 的樣式
//     instance.altInput.classList.add(
//       'px-2',
//       'py-2',
//       'border',
//       'border-[#66bb6a]',
//       'rounded-lg',
//       'shadow-md',
//       'focus:ring-2',
//       'focus:ring-[#66bb6a]',
//       'bg-[#fff8e1]',
//       'text-[#66bb6a]',
//       'hover:border-[#66bb6a]',
//       'cursor-pointer',
//       'focus:outline-none',
//     );
//   },
// });
