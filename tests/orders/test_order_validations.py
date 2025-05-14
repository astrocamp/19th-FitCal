from decimal import Decimal

import pytest
from django.utils import timezone

from tests.helpers import assert_validation_errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input,expected_messages',
    [
        ({'order_status': 'invalid_status'}, {'order_status': 'not a valid choice'}),
        (
            {'payment_method': 'invalid_method'},
            {'payment_method': 'not a valid choice'},
        ),
        (
            {'payment_status': 'invalid_status'},
            {'payment_status': 'not a valid choice'},
        ),
        (
            {'total_price': -100},
            {'total_price': 'Ensure this value is greater than or equal to 0'},
        ),
        ({'pickup_time': 'invalid_date'}, {'pickup_time': 'invalid format'}),
    ],
)
def test_order_validation_errors(
    order_factory, invalid_input, expected_messages, member_factory, store_factory
):
    # 建立合法的預設資料
    valid_data = {
        'member': member_factory(),  # 假設會員已經存在
        'store': store_factory(),  # 假設商店已經存在
        'pickup_time': timezone.now() + timezone.timedelta(hours=1),
        'order_status': 'pending',
        'payment_method': 'cash',
        'payment_status': 'unpaid',
        'total_price': 100,
    }

    # 將不合法欄位更新進去
    test_data = {**valid_data, **invalid_input}
    order = order_factory.build(**test_data)

    assert_validation_errors(order, expected_messages)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input,expected_messages',
    [
        (
            {'unit_price': -100},
            {'unit_price': 'Ensure this value is greater than or equal to 0.'},
        ),
        (
            {'subtotal': 500, 'unit_price': 100, 'quantity': 2},
            {'subtotal': 'Subtotal must equal unit_price × quantity'},
        ),
        (
            {'quantity': -5},
            {'quantity': 'Ensure this value is greater than or equal to 0'},
        ),
        (
            {'subtotal': -1},
            {'subtotal': 'Ensure this value is greater than or equal to 0.'},
        ),
    ],
)
def test_orderitem_validation_errors(
    orderitem_factory, invalid_input, expected_messages
):
    valid_data = {
        'unit_price': Decimal('100'),
        'quantity': 2,
        'subtotal': Decimal('200'),  # 100 * 2
    }

    test_data = {**valid_data, **invalid_input}
    orderitem = orderitem_factory.build(**test_data)

    assert_validation_errors(orderitem, expected_messages)
