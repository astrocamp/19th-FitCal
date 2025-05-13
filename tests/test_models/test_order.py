import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_order_factory_is_valid(order_factory):
    order = order_factory()
    order.full_clean()


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_orderitem_factory_is_valid(order_factory, product_factory, orderitem_factory):
    order = order_factory()
    product = product_factory()

    # Use the factory to create OrderItem instead of manually instantiating it
    order_item = orderitem_factory(order=order, product=product)

    # Validate the instance
    order.full_clean()
    order_item.full_clean()

    # Assert that the subtotal is correct
    assert order_item.subtotal == order_item.unit_price * order_item.quantity


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


# Factory 欄位型別與格式檢查（包含必填欄位）
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


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'field, value, expected_error_key',
    [
        ('order_status', 'invalid_status', 'order_status'),
        ('payment_method', 'wrong_method', 'payment_method'),
        ('payment_status', 'unknown_status', 'payment_status'),
        ('total_price', Decimal('-100'), 'total_price'),
    ],
)
def test_order_invalid_fields(order_factory, field, value, expected_error_key):
    order = order_factory(**{field: value})
    with pytest.raises(ValidationError) as exc_info:
        order.full_clean()
    errors = exc_info.value.message_dict
    assert expected_error_key in errors


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'field, value, expected_exception',
    [
        ('unit_price', Decimal('-10'), ValidationError),
        ('quantity', -1, ValidationError),
        ('subtotal', Decimal('-200'), ValidationError),
    ],
)
def test_order_item_invalid_fields_db_constraint(
    order_factory, product_factory, orderitem_factory, field, value, expected_exception
):
    order = order_factory()
    product = product_factory()

    defaults = {
        'order': order,
        'product': product,
        'unit_price': Decimal('100'),
        'quantity': 1,
        'subtotal': Decimal('100'),
    }
    defaults[field] = value

    orderitem = orderitem_factory.build(**defaults)

    # 確保觸發驗證
    with pytest.raises(expected_exception):
        orderitem.full_clean()


# TODO 關聯欄位測試
@pytest.mark.django_db
def test_order_orderitem_relationship(order_factory, orderitem_factory):
    # 建立一筆訂單
    order = order_factory()

    # 建立兩筆與該訂單相關的訂單項目
    order_item_1 = orderitem_factory(order=order)
    order_item_2 = orderitem_factory(order=order)

    # 驗證 Order 物件透過 orderitem_set 反向關聯取得 OrderItem
    assert order.orderitem_set.count() == 2
    assert order_item_1 in order.orderitem_set.all()
    assert order_item_2 in order.orderitem_set.all()


@pytest.mark.django_db
def test_order_m2m_product_relation(order_factory, product_factory, orderitem_factory):
    # 建立訂單與兩個產品
    order = order_factory()
    product1 = product_factory()
    product2 = product_factory()

    # 建立 OrderItem，連結產品與訂單（透過中介模型）
    orderitem_factory(order=order, product=product1)
    orderitem_factory(order=order, product=product2)

    # 驗證 Order 的 ManyToMany 關聯包含這兩個產品
    assert order.product.count() == 2
    assert product1 in order.product.all()
    assert product2 in order.product.all()


@pytest.mark.django_db
def test_product_ordered_in_relationship(
    order_factory, product_factory, orderitem_factory
):
    # 建立訂單與產品
    order = order_factory()
    product = product_factory()

    # 建立 orderitem 將兩者連結
    orderitem = orderitem_factory(order=order, product=product)

    # 驗證 product 透過 related_name 反向關聯到 order
    assert order in product.ordered_in.all()
    assert product in order.product.all()

    # 驗證 orderitem 關聯欄位
    assert orderitem.order == order
    assert orderitem.product == product

    # 也可以從 order 取回 orderitem 並確認裡面的 product
    orderitem_from_order = order.orderitem_set.first()
    assert orderitem_from_order.product == product


# 驗證 subtotal
@pytest.mark.django_db
def test_order_item_subtotal_validation(
    orderitem_factory, order_factory, product_factory
):
    order = order_factory()
    product = product_factory()

    # 故意讓 subtotal 錯誤（unit_price * quantity != subtotal）
    orderitem = orderitem_factory.build(
        order=order,
        product=product,
        unit_price=Decimal('100'),
        quantity=3,
        subtotal=Decimal('200'),
    )

    with pytest.raises(ValidationError) as exc_info:
        orderitem.full_clean()

    assert 'subtotal' in exc_info.value.message_dict
