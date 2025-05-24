from uuid import uuid4

from django.db import models
from django.db.models import UniqueConstraint

# from members.models import Member
# from stores.models import Store
# from products.models import Product


# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note = models.TextField(blank=True, null=True)
    total_price = models.PositiveIntegerField(default=0)
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
    def calculate_total_price(self):
        # 利用 select_related 預先抓 product 避免N+1
        items = self.items.select_related('product').all()

        total = 0
        for item in items:
            total += item.product.price * item.quantity

        return total

    # 更新總價
    def update_total_price(self):
        self.total_price = self.calculate_total_price()
        self.save(update_fields=['total_price'])


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
