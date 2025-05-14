import uuid
from datetime import time

import pytest
from django.core.exceptions import ValidationError


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_store_factory_is_valid(store_factory):
    store = store_factory()
    store.full_clean()


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_store_model_fields(store_factory):
    store = store_factory()

    assert isinstance(store.id, uuid.UUID), 'id 應該是 UUID 類型'
    assert isinstance(store.address, str), 'address 應為字串'
    assert isinstance(store.phone_number, str), 'phone_number 應為字串'
    assert isinstance(store.opening_time, time), 'opening_time 應為 time 類型'
    assert isinstance(store.closing_time, time), 'closing_time 應為 time 類型'
    assert store.tax_id.isdigit() and len(store.tax_id) == 8, '統編應為 8 位數字'


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_data, expected_error_field, expected_message',
    [
        ({'tax_id': 'ABC12345'}, 'tax_id', '統編必須為8位數字'),
        ({'tax_id': '123'}, 'tax_id', '統編必須為8位數字'),
    ],
)
def test_store_invalid_tax_id(
    store_factory, invalid_data, expected_error_field, expected_message
):
    base_data = {
        'address': '台北市中正區',
        'phone_number': '0223456789',
        'opening_time': time(9, 0),
        'closing_time': time(18, 0),
        'tax_id': '12345678',  # valid by default
    }
    base_data.update(invalid_data)
    store = store_factory.build(**base_data)

    with pytest.raises(ValidationError) as e:
        store.full_clean()

    assert expected_error_field in e.value.message_dict
    assert expected_message in e.value.message_dict[expected_error_field][0]


# TODO 關聯欄位測試
