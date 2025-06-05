import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product

from .enums import OrderStatus, PaymentMethod, PaymentStatus
from .fsm import OrderFSM
from .utils import get_order_number, get_pickup_number


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=20, unique=True, editable=False, null=True
    )
    pickup_number = models.CharField(max_length=20, editable=False, null=True)

    member = models.ForeignKey(
        'members.Member',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
    )
    store = models.ForeignKey(
        'stores.Store', on_delete=models.SET_NULL, null=True, related_name='orders'
    )
    pickup_time = models.DateTimeField()
    note = models.TextField(null=True, blank=True)
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    products = models.ManyToManyField(
        Product, through='orders.OrderItem', related_name='ordered_in'
    )

    # 快照
    member_name = models.CharField(max_length=50, editable=False, null=True)
    member_phone = models.CharField(max_length=20, editable=False, null=True)
    store_name = models.CharField(max_length=100, editable=False, null=True)
    store_phone = models.CharField(max_length=20, editable=False, null=True)
    store_address = models.CharField(max_length=200, editable=False, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # 新訂單
            if self.payment_method == PaymentMethod.CASH:
                self.payment_status = PaymentStatus.PAID

        # 生成訂單編號)
        if not self.order_number:
            self.order_number = get_order_number()
        # 生成取餐編號
        if not self.pickup_number:
            self.pickup_number = get_pickup_number(self.store.id)

        # 儲存快照資訊
        if self.member and not self.member_name:
            self.member_name = self.member.name
        if self.member and not self.member_phone:
            self.member_phone = self.member.phone_number

        if self.store:
            self.store_name = self.store.name
            self.store_phone = self.store.phone_number
            self.store_address = self.store.address

        super().save(*args, **kwargs)

    def __str__(self):
        return f'訂單編號: {self.order_number}'

    @property
    def fsm(self):
        """獲取訂單狀態機"""
        return OrderFSM(self)

    @property
    def can_cancel(self):
        """檢查訂單是否可以取消"""
        return self.fsm.can_cancel()

    @property
    def can_cancel_by_store(self):
        """檢查商家是否可以取消訂單"""
        return self.fsm.can_cancel(by_store=True)

    @property
    def can_prepare(self):
        """檢查訂單是否可以開始準備"""
        return self.fsm.can_prepare()

    @property
    def can_mark_ready(self):
        """檢查訂單是否可以標記為準備完成"""
        return self.fsm.can_mark_ready()

    @property
    def can_complete(self):
        """檢查訂單是否可以標記為完成取餐"""
        return self.fsm.can_complete()


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
    )

    # 快照
    product_name = models.CharField(
        max_length=100,
        editable=False,
        default='',
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'], name='unique_order_product'
            )
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity

        # 儲存產品快照
        if self.product:
            self.product_name = self.product.name

            if not self.unit_price:
                self.unit_price = self.product.price

        super().save(*args, **kwargs)

        # 更新訂單總金額
        if self.order:
            total = sum(item.subtotal for item in self.order.orderitem_set.all())
            Order.objects.filter(id=self.order.id).update(total_price=total)

    def clean(self):
        expected_subtotal = self.unit_price * self.quantity
        if self.subtotal != expected_subtotal:
            raise ValidationError(
                {'subtotal': 'Subtotal must equal unit_price × quantity'}
            )

    def __str__(self):
        return f'{self.product_name} ({self.quantity} x ${self.unit_price})'
