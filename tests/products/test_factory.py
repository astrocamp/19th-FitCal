import uuid

import pytest


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_product_factory_is_valid(product_factory):
    product = product_factory()
    product.full_clean()


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_product_model_fields(product_factory):
    product = product_factory()

    assert isinstance(product.id, uuid.UUID), 'id 應為 UUID 類型'
    assert isinstance(product.name, str), 'name 應為字串'
    assert isinstance(product.description, str), 'description 應為字串'
    assert isinstance(product.calories, int) and product.calories >= 0, (
        'calories 應為正整數'
    )
    assert isinstance(product.quantity, int) and product.quantity >= 0, (
        'quantity 應為正整數'
    )
    assert isinstance(product.price, int) and product.price >= 0, 'price 應為正整數'
    assert product.customize is None or isinstance(product.customize, str), (
        'customize 可為 None 或字串'
    )
