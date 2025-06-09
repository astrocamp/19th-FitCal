export function initCategorySidebarActive() {
  const items = document.querySelectorAll('#category-sidebar .category-item');

  items.forEach((item) => {
    item.addEventListener('click', () => {
      items.forEach((el) => {
        el.classList.remove('category-select');
      });
      item.classList.add('category-select');
    });
  });
}

// 初始與 HTMX 動態綁定
document.addEventListener('DOMContentLoaded', initCategorySidebarActive);

document.addEventListener('htmx:afterSwap', (e) => {
  if (e.target.querySelector('#category-sidebar')) {
    initCategorySidebarActive();
  }
});
