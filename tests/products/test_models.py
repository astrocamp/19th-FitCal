import pytest

from products.models import Product


@pytest.mark.django_db
def test_product_create(product_factory):
    # 使用工廠創建一個 product 實例
    product = product_factory(
        name='雞胸餐盒',
        calories=100,
        quantity=5,
        price=200,
        description='A sample product',
    )

    # 檢查 product 的基本屬性
    assert product.name == '雞胸餐盒'
    assert product.calories == 100
    assert product.quantity == 5
    assert product.price == 200
    assert product.description == 'A sample product'

    product.save()
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_product_update(product_factory):
    # 創建 product 實例
    product = product_factory(
        name='Old Product', price=50.0, description='Old description'
    )
    product.save()

    # 更新 product 實例的資料
    product.name = 'Updated Product'
    product.price = 150
    product.description = 'Updated description'
    product.save()

    # 確保更新後的資料正確
    updated_product = Product.objects.get(id=product.id)
    assert updated_product.name == 'Updated Product'
    assert updated_product.price == 150
    assert updated_product.description == 'Updated description'


@pytest.mark.django_db
def test_product_delete(product_factory):
    # 創建並保存一個 product 實例
    product = product_factory(
        name='Product to Delete',
        price=200.0,
        description='This product will be deleted',
    )
    product.save()

    # 刪除該 product
    product.delete()

    # 確保產品已經被刪除
    with pytest.raises(Product.DoesNotExist):
        Product.objects.get(name='Product to Delete')
