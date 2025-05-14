# 驗證錯誤測試（Model Validation）
from datetime import time

import pytest

from tests.constants import INVALID_TAX_ID_MSG
from tests.helpers import assert_validation_errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input,expected_messages',
    [
        ({'tax_id': 'ABC12345'}, {'tax_id': INVALID_TAX_ID_MSG}),
        ({'tax_id': '123'}, {'tax_id': INVALID_TAX_ID_MSG}),
    ],
)
def test_store_validation_errors(store_factory, invalid_input, expected_messages):
    # 建立合法的預設資料
    valid_data = {
        'address': '台北市中正區',
        'phone_number': '0223456789',
        'opening_time': time(9, 0),
        'closing_time': time(18, 0),
        'tax_id': '12345678',  # valid by default
    }

    # 將不合法欄位更新進去
    test_data = {**valid_data, **invalid_input}
    store = store_factory.build(**test_data)

    assert_validation_errors(store, expected_messages)
