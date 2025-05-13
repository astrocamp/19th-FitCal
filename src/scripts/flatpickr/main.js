import { StyledFlatpickr } from './init.js';

export function initPickupTimePicker(
  seletor,
  style,
  options = {
    enableTime: true,
    dateFormat: 'Y-m-d\\TH:i',
    minuteIncrement: 10,
    altInput: true,
    altFormat: 'Y年m月d日 H:i',
  },
) {
  new StyledFlatpickr(seletor, style, options);
}
// 範例: 套用 healthy_style 並覆寫選項

// 可在以下位置添加更多的 StyledFlatpickr 實例
