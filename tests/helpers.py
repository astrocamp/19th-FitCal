import random

import pytest
from django.core.exceptions import ValidationError


def assert_validation_errors(instance, expected_messages):
    """
    檢查 Django model 實例在 full_clean 時是否產生預期的 ValidationError 訊息。

    :param instance: 要驗證的 model 實例
    :param expected_messages: dict 格式，key 是欄位名稱，value 是預期錯誤訊息（子字串即可）
    """
    with pytest.raises(ValidationError) as exc_info:
        instance.full_clean()

    validation_errors = exc_info.value.message_dict

    for field, expected_msg in expected_messages.items():
        assert field in validation_errors, f'{field} 沒有出現在錯誤訊息中'
        actual_msg = validation_errors[field][0]
        assert expected_msg in actual_msg, (
            f'{field} 錯誤訊息應包含: {expected_msg}，實際為: {actual_msg}'
        )


# def assert_index_get_view(client, factory, reverse_name, context_key, expected_count):
#     factory.create_batch(expected_count)
#     url = reverse(reverse_name)
#     response = client.get(url)

#     assert response.status_code == 200
#     assert context_key in response.context
#     assert len(response.context[context_key]) == expected_count


# def assert_index_post_create_view(client, reverse_name, valid_data, model_class):
#     url = reverse(reverse_name)
#     response = client.post(url, data=valid_data)

#     assert response.status_code == 302  # redirect after successful post
#     assert model_class.objects.count() == 1


# def assert_index_post_invalid_view(client, reverse_name, invalid_data, model_class):
#     url = reverse(reverse_name)
#     response = client.post(url, data=invalid_data)

#     # 表單無效時應回傳 200，並重渲染頁面
#     assert response.status_code == 200
#     assert 'form' in response.context
#     assert response.context['form'].errors
#     assert model_class.objects.count() == 0


def validate_tax_id(tax_id):
    if not tax_id.isdigit() or len(tax_id) != 8:
        return False

    weights = [1, 2, 1, 2, 1, 2, 4, 1]
    total = 0

    for i in range(8):
        products = int(tax_id[i]) * weights[i]
        if products >= 10:
            products = (products // 10) + (products % 10)
        total += products

    # 特例：第七碼是 7 時
    if total % 10 == 0:
        return True
    elif tax_id[6] == '7' and (total + 1) % 10 == 0:
        return True
    else:
        return False


def generate_tax_id():
    # 隨機生成8位數字
    tax_id = ''.join(str(random.randint(0, 9)) for _ in range(8))

    # 使用台灣統一編號檢查碼演算法來檢查是否有效
    while not validate_tax_id(tax_id):
        tax_id = ''.join(str(random.randint(0, 9)) for _ in range(8))

    return tax_id
