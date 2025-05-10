import { StyledFlatpickr } from './init.js';

// 範例: 套用 healthy_style 並覆寫選項
new StyledFlatpickr('#id_pickup_time', 'healthy_style', {
  enableTime: true,
  dateFormat: 'Y-m-d\\TH:i',
  minuteIncrement: 10,
  altFormat: 'Y年m月d日',
  altInput: true,
  altFormat: 'Y年m月d日 H:i',
});

// 可在以下位置添加更多的 StyledFlatpickr 實例
