import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from members.models import Member
from products.models import Product
from stores.models import Store

from .enums import OrderStatus, PaymentMethod, PaymentStatus


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=20, unique=True, editable=False, null=True
    )
    pickup_number = models.CharField(max_length=20, editable=False, null=True)

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

    class Meta:
        unique_together = ('member', 'store')

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORDYYYYMMDDnnnn
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = (
                Order.objects.filter(order_number__startswith=f'ORD{date_str}')
                .order_by('order_number')
                .last()
            )

            if last_order:
                last_number = int(last_order.order_number[-4:])
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'

            self.order_number = f'ORD{date_str}{new_number}'

        if not self.pickup_number:
            # Generate pickup number: 依照當天日期重新計數
            today = timezone.now().date()
            today_start = timezone.make_aware(
                timezone.datetime.combine(today, timezone.datetime.min.time())
            )
            today_end = timezone.make_aware(
                timezone.datetime.combine(today, timezone.datetime.max.time())
            )

            # 取得今天的最後一個取餐號碼
            last_pickup = (
                Order.objects.filter(created_at__range=(today_start, today_end))
                .order_by('created_at')
                .last()
            )

            if last_pickup:
                last_number = int(last_pickup.pickup_number)
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'

            self.pickup_number = new_number

        # 儲存快照資訊
        if self.member:
            self.member_name = self.member.name
            self.member_phone = self.member.phone_number

        if self.store:
            self.store_name = self.store.name
            self.store_phone = self.store.phone_number
            self.store_address = self.store.address

        super().save(*args, **kwargs)

    def __str__(self):
        return f'訂單編號: {self.order_number}'


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
        unique_together = ('order', 'product')

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
