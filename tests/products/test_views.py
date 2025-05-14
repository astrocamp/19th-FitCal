import pytest
from django.urls import reverse

from products.models import Product


@pytest.mark.django_db
def test_product_index_get_view(client, product_factory):
    product_factory.create_batch(3)
    url = reverse('products:index')
    response = client.get(url)

    assert response.status_code == 200
    assert 'products' in response.context
    assert len(response.context['products']) == 3


@pytest.mark.django_db
def test_product_index_post_valid(client):
    valid_data = {
        'name': 'Test Product',
        'calories': 200,
        'quantity': 3,
        'price': 199,
        'description': 'A sample product',
    }
    url = reverse('products:index')
    response = client.post(url, data=valid_data)

    assert response.status_code == 302  # redirect after successful post
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_product_index_post_invalid(client):
    invalid_data = {
        'name': 'Test Product',
        'calories': 200,
        'quantity': 10,
        'price': 'not_a_number',
        'description': 'desc',
    }
    url = reverse('products:index')
    response = client.post(url, data=invalid_data)

    # 表單無效時應回傳 200，並重渲染頁面
    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert Product.objects.count() == 0


@pytest.mark.django_db
def test_product_new_view(client):
    url = reverse('products:new')  # 假設你在 urls.py 有設定 name='new'
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'products/new.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_product_show_view_get(client, product_factory):
    product = product_factory()
    url = reverse('products:show', args=[product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'product' in response.context
    assert response.context['product'].id == product.id
    assert 'products/show.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_product_show_view_post_valid_data(client, product_factory):
    product = product_factory(quantity=8)
    url = reverse('products:show', args=[product.id])
    data = {
        'name': product.name,
        'calories': product.calories,
        'quantity': 5,
        'price': product.price,  # price 須為數字
        'description': product.description,
    }

    response = client.post(url, data)

    assert response.status_code == 302  # redirect
    product.refresh_from_db()  # 確保更新後的資料被重新讀入
    assert product.quantity == 5


@pytest.mark.django_db
def test_product_show_view_post_invalid_data(client, product_factory):
    product = product_factory()
    url = reverse('products:show', args=[product.id])
    data = {
        'name': product.name,
        'calories': product.calories,
        'quantity': -5,
        'price': product.price,  # price 須為數字
        'description': product.description,
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert 'products/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_product_edit_view_get(client, product_factory):
    # 建立測試用的 product
    product = product_factory()
    # 假設 URL pattern 是 products:edit 對應 path('<int:id>/edit/', views.edit, name='edit')
    url = reverse('products:edit', args=[product.id])

    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'product' in response.context
    assert response.context['product'].id == product.id
    assert response.context['form'].instance == product
    assert 'products/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_product_delete_view(client, product_factory):
    # 建立測試用 product
    product = product_factory()
    url = reverse('products:delete', args=[product.id])

    # 先確認 product 存在於資料庫
    assert Product.objects.filter(id=product.id).exists()

    response = client.post(url)

    # 再確認 product 已被刪除
    assert response.status_code == 302  # Redirect
    assert response.url == reverse('products:index')
    assert not Product.objects.filter(id=product.id).exists()
