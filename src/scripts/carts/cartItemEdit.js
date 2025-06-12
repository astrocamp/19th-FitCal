export default function cartItem(initQuantity, itemId, editUrl, stockQuantity) {
  return {
    qty: initQuantity,
    initQty: initQuantity,
    isDelete() {
      if (this.qty !== this.initQty) {
        if (this.qty < 1) {
          if (confirm('確認要刪除這個品項嗎？')) {
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
          if (this.qty > stockQuantity) {
            htmx.ajax('POST', `${editUrl}`, {
              swap: 'none',
              values: {
                quantity: this.qty,
              },
            });
            this.qty = this.initQty;
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
      }
      this.initQty = this.qty;
    },
  };
}
