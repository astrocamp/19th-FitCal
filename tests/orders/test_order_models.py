from datetime import datetime

import pytest
from django.utils import timezone

from orders.models import Order


@pytest.mark.django_db
def test_order_create(order_factory):
    # 使用工廠創建一個 order 實例
    order = order_factory(
        pickup_time=timezone.make_aware(datetime(2025, 5, 15, 10, 0, 0)),
        note='註記:要加辣',
    )

    assert order.pickup_time == timezone.make_aware(datetime(2025, 5, 15, 10, 0, 0))
    assert order.order_status == 'pending'
    assert order.payment_status == 'unpaid'
    assert order.payment_method in ('cash', 'credit_card', 'line_pay')
    assert order.note == '註記:要加辣'

    order.save()
    assert Order.objects.count() == 1


@pytest.mark.django_db
def test_order_read(order_factory):
    order = order_factory(
        pickup_time=timezone.make_aware(datetime(2025, 5, 17, 11, 30, 0)),
        note='註記:要加蔥',
        order_status='completed',
        payment_status='paid',
        payment_method='line_pay',
    )
    order.save()

    # 查詢該 order
    retrieved_order = Order.objects.get(id=order.id)

    assert retrieved_order.pickup_time == timezone.make_aware(
        datetime(2025, 5, 17, 11, 30, 0)
    )
    assert retrieved_order.note == '註記:要加蔥'
    assert retrieved_order.order_status == 'completed'
    assert retrieved_order.payment_status == 'paid'
    assert retrieved_order.payment_method == 'line_pay'


@pytest.mark.django_db
def test_order_update(order_factory):
    order = order_factory(
        pickup_time=timezone.make_aware(datetime(2025, 5, 17, 11, 30, 0)),
        note='註記:要加蔥',
        order_status='pending',
        payment_status='unpaid',
        payment_method='line_pay',
    )
    order.save()

    # 更新資料
    order.note = '註記:要加辣'
    order.order_status = 'completed'
    order.payment_status = 'paid'
    order.save()

    updated_order = Order.objects.get(id=order.id)
    assert updated_order.note == '註記:要加辣'
    assert updated_order.order_status == 'completed'
    assert updated_order.payment_status == 'paid'


@pytest.mark.django_db
def test_order_delete(order_factory):
    order = order_factory()
    order.save()

    # 刪除該 order
    order.delete()

    # 驗證該 order 是否已經被刪除
    with pytest.raises(Order.DoesNotExist):
        Order.objects.get(id=order.id)
