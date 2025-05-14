import uuid
from datetime import datetime
from decimal import Decimal

import pytest


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_order_factory_is_valid(order_factory):
    order = order_factory()
    order.full_clean()


@pytest.mark.django_db
def test_orderitem_factory_is_valid(orderitem_factory):
    orderitem = orderitem_factory()
    orderitem.full_clean()


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_order_model_fields(order_factory):
    order = order_factory()

    # UUID 欄位
    assert isinstance(order.id, uuid.UUID)

    # 關聯欄位
    assert order.member is not None
    assert order.store is not None

    # 時間欄位
    assert isinstance(order.pickup_time, datetime)
    assert isinstance(order.created_at, datetime)
    assert isinstance(order.updated_at, datetime)

    # 選項欄位
    assert order.order_status in dict(order.ORDER_STATUS_CHOICES)
    assert order.payment_method in dict(order.PAYMENT_METHOD_CHOICES)
    assert order.payment_status in dict(order.PAYMENT_STATUS_CHOICES)

    # 數值與格式欄位
    assert isinstance(order.total_price, Decimal)
    assert order.total_price >= 0

    # JSON 欄位
    assert isinstance(order.customize, dict) or order.customize is None

    # 快照欄位（若尚未填入可以是 None）
    assert hasattr(order, 'member_name')
    assert hasattr(order, 'store_name')


@pytest.mark.django_db
def test_orderitem_model_fields(orderitem_factory):
    order_item = orderitem_factory()

    # UUID 欄位
    assert isinstance(order_item.id, uuid.UUID)

    # 關聯欄位
    assert order_item.order is not None
    assert order_item.product is not None

    # 快照欄位
    assert isinstance(order_item.product_name, str)
    assert len(order_item.product_name) <= 100

    # 數值欄位
    assert isinstance(order_item.unit_price, Decimal)
    assert order_item.unit_price >= 0

    assert isinstance(order_item.quantity, int)
    assert order_item.quantity >= 1

    assert isinstance(order_item.subtotal, Decimal)
    assert order_item.subtotal == order_item.unit_price * order_item.quantity
