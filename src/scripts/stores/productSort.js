import Sortable from 'sortablejs';

export function initProductSort() {
  function onSortedCallback(sortedIds) {
    // 從 DOM 容器取得 URL，避免硬編碼
    const containerWrapper = document.querySelector('#sortable-products');
    if (!containerWrapper) {
      return;
    }
    const sortUrl = containerWrapper.dataset.sortUrl;
    if (!sortUrl) {
      return;
    }

    htmx.ajax('POST', sortUrl, {
      target: '#messages-container',
      swap: 'innerHTML',
      values: { ids: sortedIds },
    });
  }

  function initSortable(containerSelector, callback) {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    Sortable.create(container, {
      animation: 150,
      handle: '.cursor-move',
      ghostClass: 'bg-yellow-100',
      onEnd: function () {
        const ids = [...container.children].map((el) => el.dataset.id);
        if (callback) callback(ids);
      },
    });
  }

  // 初次啟動（頁面載入時）
  initSortable('#sortable-products', onSortedCallback);

  // HTMX 動態交換後自動重綁定
  document.body.addEventListener('htmx:afterSwap', (evt) => {
    if (evt.detail.target.querySelector('#sortable-products')) {
      initSortable('#sortable-products', onSortedCallback);
    }
  });
}
