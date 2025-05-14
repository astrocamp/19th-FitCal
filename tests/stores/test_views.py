from datetime import time

import pytest
from django.urls import reverse

from stores.models import Store
from tests.helpers import generate_tax_id


@pytest.mark.django_db
def test_store_index_get_view(client, store_factory):
    store_factory.create_batch(3)
    url = reverse('stores:index')
    response = client.get(url)

    assert response.status_code == 200
    assert 'stores' in response.context
    assert len(response.context['stores']) == 3


@pytest.mark.django_db
def test_store_index_post_valid(
    client,
):
    valid_data = {
        'address': '台北市中正區',
        'phone_number': '0912345678',
        'opening_time': time(7, 0),
        'closing_time': time(19, 0),
        'tax_id': generate_tax_id(),
    }
    url = reverse('stores:index')
    response = client.post(url, data=valid_data)
    if response.status_code == 200:
        print(response.context['form'].errors)  # 查看表單錯誤

    assert response.status_code == 302  # redirect after successful post
    assert Store.objects.count() == 1


@pytest.mark.django_db
def test_store_index_post_invalid(client):
    invalid_data = {
        'address': '台北市中正區',
        'phone_number': '09123',
        'opening_time': time(7, 0),
        'closing_time': time(19, 0),
        'tax_id': '12345678',
    }
    url = reverse('stores:index')
    response = client.post(url, data=invalid_data)

    # 表單無效時應回傳 200，並重渲染頁面
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert Store.objects.count() == 0


@pytest.mark.django_db
def test_store_new_view(client):
    url = reverse('stores:new')  # 假設你在 urls.py 有設定 name='new'
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'stores/new.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_store_show_view_get(client, store_factory):
    store = store_factory()
    url = reverse('stores:show', args=[store.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'store' in response.context
    assert response.context['store'].id == store.id
    assert 'stores/show.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_store_show_view_post_valid_data(client, store_factory):
    store = store_factory(phone_number='0912345678')
    url = reverse('stores:show', args=[store.id])
    data = {
        'address': '台北市信義區',
        'phone_number': '0987654321',
        'opening_time': time(10, 0),
        'closing_time': time(22, 0),
        'tax_id': generate_tax_id(),
    }

    response = client.post(url, data)

    assert response.status_code == 302  # redirect
    store.refresh_from_db()  # 確保更新後的資料被重新讀入
    assert store.address == '台北市信義區'
    assert store.phone_number == '0987654321'
    assert store.opening_time == time(10, 0)
    assert store.closing_time == time(22, 0)


@pytest.mark.django_db
def test_store_show_view_post_invalid_data(client, store_factory):
    store = store_factory()
    url = reverse('stores:show', args=[store.id])
    data = {
        'address': '台北市信義區',
        'phone_number': '098',
        'opening_time': time(10, 0),
        'closing_time': time(22, 0),
        'tax_id': 'generate_tax_id()',
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert 'stores/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_store_edit_view_get(client, store_factory):
    store = store_factory()

    url = reverse('stores:edit', args=[store.id])

    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'store' in response.context
    assert response.context['store'].id == store.id
    assert response.context['form'].instance == store
    assert 'stores/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_store_delete_view(client, store_factory):
    # 建立測試用 store
    store = store_factory()
    url = reverse('stores:delete', args=[store.id])

    # 先確認 store 存在於資料庫
    assert Store.objects.filter(id=store.id).exists()

    response = client.post(url)

    # 再確認 store 已被刪除
    assert response.status_code == 302  # Redirect
    assert response.url == reverse('stores:index')
    assert not Store.objects.filter(id=store.id).exists()
