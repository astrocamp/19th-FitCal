import uuid

from django.core.validators import MinValueValidator
from django.db import models

from members.models import Member
from products.models import Product
from stores.models import Store


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', '待處理'),
        ('confirmed', '已確認'),
        ('canceled', '已取消'),
        ('completed', '已完成'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', '現金'),
        ('credit_card', '信用卡'),
        ('line_pay', 'LINE Pay'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', '未付款'),
        ('paid', '已付款'),
        ('refunded', '已退款'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
    )
    pickup_time = models.DateTimeField()
    note = models.TextField(null=True, blank=True)
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default='pending'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash'
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid'
    )
    # TODO
    # 如果未來會加入優惠券、服務費、運費等項目，可以名稱改為 final_total 或修改欄位如下
    # subtotal, discount, final_total
    total_price = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )
    customize = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    product = models.ManyToManyField(
        Product, through='OrderItem', related_name='orders'
    )
    # 快照
    member_name = models.CharField(max_length=50, editable=False, null=True)
    store_name = models.CharField(max_length=100, editable=False, null=True)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
    )
    # 快照
    product_name = models.CharField(max_length=100, default='')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
