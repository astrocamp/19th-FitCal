import uuid

from django.db import models


# Create your models here.
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO
    # 還沒辦法關聯到 user 和 store model，等組員將 user, store model
    # 建立好後再加入欄位
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # store = models.ForeignKey(Store, on_delete=models.DO_NOTHING)
    pickup_time = models.DateTimeField()
    note = models.TextField(null=True, blank=True)
    order_status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, default='unpaid')
    total_price = models.PositiveIntegerField()
    customize = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # TODO
    # 還沒辦法關聯到 product model，等組員將 user, store model
    # 建立好後再加入欄位
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
