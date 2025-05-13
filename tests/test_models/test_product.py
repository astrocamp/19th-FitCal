import uuid
from datetime import time

import pytest
from django.core.exceptions import ValidationError


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_product_factory_is_valid(product_factory):
    product = product_factory()
    product.full_clean()


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_product_creation(product_factory):
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


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'field_name, invalid_value',
    [
        ('calories', -100),
        ('quantity', -1),
        ('price', -50),
    ],
)
def test_product_negative_numbers_fail_validation(
    product_factory, field_name, invalid_value
):
    base_data = {
        'name': '雞胸便當',
        'description': '高蛋白健康餐',
        'calories': 500,
        'quantity': 10,
        'price': 150,
        'customize': '可加蛋',
    }
    base_data[field_name] = invalid_value
    product = product_factory.build(**base_data)

    with pytest.raises(ValidationError) as e:
        product.full_clean()

    assert field_name in e.value.message_dict
    assert 'Ensure this value is greater than or equal to 0' in str(
        e.value.message_dict[field_name][0]
    )


# TODO 關聯欄位測試
