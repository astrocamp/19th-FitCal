import uuid
from datetime import time

import pytest


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
