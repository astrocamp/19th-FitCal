export function initTabs() {
  const tabButtons = document.querySelectorAll('#tab-bar .tab-btn');

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach((b) => {
        b.classList.remove('border-b-2', 'border-blue-600', 'font-semibold');
      });
      btn.classList.add('border-b-2', 'border-blue-600', 'font-semibold');
    });
  });
}

// 這段集中寫在這裡 → 負責首次和 HTMX 的初始化
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
});

document.addEventListener('htmx:afterSwap', (e) => {
  // 確保新加入的內容也有 tab-bar 再執行（避免不必要重綁）
  if (e.target && e.target.querySelector('#tab-bar')) {
    initTabs();
  }
});
