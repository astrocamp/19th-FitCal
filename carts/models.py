from uuid import uuid4

from django.db import models
from django.db.models import UniqueConstraint


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note = models.TextField(blank=True, null=True)
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
    )
    store = models.ForeignKey(
        'stores.Store', on_delete=models.CASCADE, related_name='carts'
    )
    cart_product = models.ManyToManyField('products.Product', through='carts.CartItem')

    class Meta:
        constraints = [UniqueConstraint(fields=['member', 'store'], name='unique_cart')]

    # 計算總價
    @property
    def calculate_total_price(self):
        # 利用 select_related 預先抓 product 避免N+1
        items = self.items.select_related('product').all()

        total = 0
        for item in items:
            total += item.product.price * item.quantity

        return total

    # 計算總價
    @property
    def calculate_total_price(self):
        # 利用 select_related 預先抓 product 避免N+1
        items = self.items.select_related('product').all()

        total = 0
        for item in items:
            total += item.product.price * item.quantity

        return total


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    customize = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['cart', 'product'], name='unique_cart_item')
        ]
