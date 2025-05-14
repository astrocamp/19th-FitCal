from datetime import time

import pytest

from stores.models import Store


@pytest.mark.django_db
def test_store_create(store_factory):
    # 使用工廠創建一個 store 實例
    store = store_factory(
        address='台北市中正區',
        phone_number='0912345678',
        opening_time=time(9, 0),
        closing_time=time(17, 0),
        tax_id='12345678',
    )

    assert store.address
    assert store.phone_number == '0912345678'
    assert store.opening_time == time(9, 0)
    assert store.closing_time == time(17, 0)
    assert store.tax_id == '12345678'

    store.save()
    assert Store.objects.count() == 1


@pytest.mark.django_db
def test_store_read(store_factory):
    store = store_factory(
        address='台北市大安區',
        phone_number='0987654321',
    )
    store.save()

    # 查詢該 store
    retrieved_store = Store.objects.get(address='台北市大安區')

    assert retrieved_store.phone_number == '0987654321'


@pytest.mark.django_db
def test_store_update(store_factory):
    store = store_factory(address='台北市大安區', phone_number='0912345678')
    store.save()

    # 更新資料
    store.address = '台北市中正區'
    store.phone_number = '0987654321'
    store.save()

    updated_store = Store.objects.get(address='台北市中正區')
    assert updated_store.address == '台北市中正區'
    assert updated_store.phone_number == '0987654321'


@pytest.mark.django_db
def test_store_delete(store_factory):
    store = store_factory(phone_number='0912345678')
    store.save()

    # 刪除該 store
    store.delete()

    # 驗證該 store 是否已經被刪除
    with pytest.raises(Store.DoesNotExist):
        Store.objects.get(phone_number='0912345678')
