from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime, make_aware

from orders.models import Order, OrderItem
from orders.utils import next_10min


@pytest.mark.django_db
def test_order_index_get_view(client, order_factory):
    order_factory.create_batch(3)
    url = reverse('orders:index')
    response = client.get(url)

    assert response.status_code == 200
    assert 'orders' in response.context
    assert len(response.context['orders']) == 3


@pytest.mark.django_db
def test_order_index_post_valid(client, product_factory):
    product = product_factory(name='雞肉餐盒', quantity=10, price=Decimal('150'))

    pickup_time = next_10min(timezone.localtime(timezone.now()))

    data = {
        'pickup_time': pickup_time,
        'note': '請加辣',
        'product_id': str(product.id),
        'quantity': '2',
        'payment_method': 'credit_card',
    }

    url = reverse('orders:index')
    response = client.post(url, data)

    assert response.status_code == 302  # redirect on success
    order = Order.objects.first()
    assert order is not None
    assert OrderItem.objects.filter(order=order, product=product).exists()

    order_item = OrderItem.objects.get(order=order, product=product)
    assert order_item.quantity == 2
    assert order_item.unit_price == product.price
    assert order_item.subtotal == product.price * 2

    product.refresh_from_db()
    assert product.quantity == 8


@pytest.mark.django_db
def test_order_index_post_invalid(client, product_factory):
    product = product_factory(quantity=1, price=100)

    data = {
        'pickup_time': '2025-05-15T12:00',
        'note': '',
        'product_id': str(product.id),
        'quantity': '5',  # 超過庫存
    }

    response = client.post(reverse('orders:index'), data)

    assert response.status_code == 200
    assert '庫存不足' in response.content.decode()
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_order_new_view(client, product_factory):
    # 準備資料：建立幾個產品
    product_factory.create_batch(3)

    url = reverse('orders:new')  # 假設你在 urls.py 中設定為 name='orders:new'
    response = client.get(url)

    # 檢查 HTTP 狀態碼
    assert response.status_code == 200

    # 檢查 context 中是否有 form 和 product
    assert 'form' in response.context
    assert 'product' in response.context
    assert response.context['product'] is not None

    # 檢查 product 是 Product 的實例
    from products.models import Product

    assert isinstance(response.context['product'], Product)


@pytest.mark.django_db
def test_order_show_view_get(client, order_factory):
    order = order_factory()
    url = reverse('orders:show', args=[order.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'order' in response.context
    assert response.context['order'].id == order.id
    assert 'orders/show.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_order_show_view_post_valid_data(client, order_factory):
    order = order_factory(pickup_time=make_aware(datetime(2025, 5, 15, 11, 0)))

    updated_data = {
        'pickup_time': make_aware(datetime(2025, 5, 15, 12, 0)),
        'order_status': 'completed',
        'payment_status': 'paid',
    }

    url = reverse('orders:show', args=[order.id])
    response = client.post(url, updated_data)
    # 成功應該會 redirect
    assert response.status_code == 302
    assert response.url == url

    # 資料應該被更新
    order.refresh_from_db()
    assert order.order_status == 'completed'
    assert order.payment_status == 'paid'


@pytest.mark.django_db
def test_order_show_view_post_invalid_data(client, order_factory):
    # 建立原始訂單
    original_pickup_time = localtime() + timedelta(days=1)
    order = order_factory(pickup_time=original_pickup_time)

    # 無效的 pickup_time（超出允許範圍）
    invalid_pickup_time = original_pickup_time + timedelta(hours=3)

    invalid_data = {
        'pickup_time': invalid_pickup_time.strftime('%Y-%m-%dT%H:%M'),
        'order_status': order.order_status,
        'payment_status': order.payment_status,
    }

    url = reverse('orders:show', args=[order.id])
    response = client.post(url, invalid_data)

    # 頁面應重新渲染（不應該 redirect）
    assert response.status_code == 200

    # 解碼成字串，檢查錯誤訊息
    response_content = response.content.decode('utf-8')
    assert '請選擇在原訂時間後2小時內的時間' in response_content

    # 資料不應變更
    order.refresh_from_db()
    assert order.pickup_time == original_pickup_time


@pytest.mark.django_db
def test_order_edit_view_get(client, order_factory):
    # 創建一個測試用訂單
    order = order_factory(pickup_time=make_aware(datetime(2025, 5, 15, 11, 0)))

    # 訪問編輯頁面
    url = reverse('orders:edit', args=[order.id])
    response = client.get(url)

    # 檢查是否返回成功的響應
    assert response.status_code == 200

    # 檢查是否有傳遞訂單到模板中
    assert 'order' in response.context
    assert response.context['order'] == order

    # 檢查表單中的值是否正確顯示（例如 'note' 與 'pickup_time'）
    assert response.context['form'].initial['note'] == order.note
    # 檢查日期時間是否轉換為正確的格式
    assert response.context['form'].initial['pickup_time'] == make_aware(
        datetime(2025, 5, 15, 11, 0)
    )


@pytest.mark.django_db
def test_order_delete_view(client, order_factory):
    # 創建一個測試用訂單
    order = order_factory(note='測試訂單')

    # 確保訂單已存在於資料庫
    assert Order.objects.filter(id=order.id).exists()

    # 刪除訂單
    url = reverse('orders:delete', args=[order.id])
    response = client.post(url)  # 發送 POST 請求以刪除訂單

    # 檢查是否重定向回訂單列表頁面
    assert response.status_code == 302
    assert response.url == reverse('orders:index')

    # 確保訂單已經被刪除
    assert not Order.objects.filter(id=order.id).exists()
