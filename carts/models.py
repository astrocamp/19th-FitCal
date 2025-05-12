from uuid import uuid4

from django.db import models

# from members.models import Member
# from stores.models import Store
# from products.models import Product


# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    note = models.TextField(blank=True, null=True)
    total_price = models.PositiveIntegerField()
    member = models.ForeignKey(
        # 此處先以user測試，待user-member關聯後改為member
        'users.User',
        on_delete=models.CASCADE,
        related_name='carts',
    )
    store = models.ForeignKey(
        'stores.Store', on_delete=models.CASCADE, related_name='carts'
    )

    # 下方為正常設定，但目前user-member尚未有對應關聯產生，先以上方預設值測試
    # member = models.ForeignKey(
    #     'members.Member', on_delete=models.CASCADE, related_name='carts'
    # )
    cart_product = models.ManyToManyField('products.Product', through='carts.CartItem')

    class Meta:
        unique_together = ('member', 'store')


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField()
    customize = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('cart', 'product')
