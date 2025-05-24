export default function cartItem(initQuantity, itemId, editUrl) {
  return {
    // 取得csrf token
    csrfToken: document.querySelector('input[name="csrfmiddlewaretoken"]')?.value,
    type: '我的目前位置',
    qty: initQuantity,
    initQty: initQuantity,
    async isDelete() {
      if (this.qty !== this.initQty) {
        if (this.qty < 1) {
          if (confirm('確認要刪除這個品相嗎？')) {
            htmx.ajax('POST', `${editUrl}`, {
              swap: 'innerHTML',
              values: {
                quantity: this.qty,
              },
            });
          } else {
            this.qty = this.initQty;
          }
        } else {
          htmx.ajax('POST', `${editUrl}`, {
            target: '#totalPrice',
            swap: 'innerHTML',
            values: {
              quantity: this.qty,
            },
          });
        }
      }
      this.initQty = this.qty;
    },
  };
}
