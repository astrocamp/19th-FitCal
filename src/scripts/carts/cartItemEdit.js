export default function cartItem(initQuantity, itemId) {
  return {
    qty: initQuantity,
    initQty: initQuantity,
    isDelete() {
      if (this.qty < 1) {
        if (confirm('確認要刪除這個品相嗎？')) {
          htmx.ajax('POST', `/carts/edit_item/${itemId}/`, {
            target: `#cart-item-${itemId}`,
            swap: 'outerHTML',
            values: {
              quantity: this.qty,
            },
          });
        } else {
          this.qty = initQty;
        }
      } else {
        htmx.ajax('POST', `/carts/edit_item/${itemId}/`, {
          target: '#messages-container',
          swap: 'innerHTML',
          values: {
            quantity: this.qty,
          },
        });
      }
    },
  };
}
