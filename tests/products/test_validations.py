import pytest

from tests.constants import INVALID_NEGATIVE_MSG
from tests.helpers import assert_validation_errors


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input, expected_messages',
    [
        ({'calories': -100}, {'calories': INVALID_NEGATIVE_MSG}),
        ({'quantity': -1}, {'quantity': INVALID_NEGATIVE_MSG}),
        ({'price': -200}, {'price': INVALID_NEGATIVE_MSG}),
    ],
)
def test_product_negative_numbers_fail_validation(
    product_factory, invalid_input, expected_messages
):
    valid_data = {
        'name': '雞胸便當',
        'description': '高蛋白健康餐',
        'calories': 500,
        'quantity': 10,
        'price': 150,
        'customize': '可加蛋',
    }
    test_data = {**valid_data, **invalid_input}
    product = product_factory.build(**test_data)

    assert_validation_errors(product, expected_messages)
