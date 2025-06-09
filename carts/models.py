from uuid import uuid4

from django.db import models
from django.db.models import F, Sum, UniqueConstraint


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note = models.TextField(blank=True, null=True)
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='carts',
    )
    store = models.ForeignKey(
        'stores.Store', on_delete=models.CASCADE, related_name='carts'
    )
    cart_product = models.ManyToManyField('products.Product', through='carts.CartItem')

    class Meta:
        constraints = [UniqueConstraint(fields=['member', 'store'], name='unique_cart')]

    # 計算總價
    @property
    def total_price(self):
        return (
            self.items.aggregate(total=Sum(F('quantity') * F('product__price')))[
                'total'
            ]
            or 0
        )

    # 計算總量
    @property
    def total_quantity(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    # 計算總卡路里
    @property
    def total_calories(self):
        return (
            self.items.aggregate(total=Sum(F('quantity') * F('product__calories')))[
                'total'
            ]
            or 0
        )


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
