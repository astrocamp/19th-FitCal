import uuid
from datetime import date, datetime

import pytest
from django.core.exceptions import ValidationError


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_member_factory_is_valid(member_factory):
    member = member_factory()
    member.full_clean()  # 若通過則代表 factory 輸出資料合法


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_member_model_fields(member_factory):
    member = member_factory()

    assert isinstance(member.id, uuid.UUID), 'id 應該是 UUID 類型'
    assert isinstance(member.phone_number, str), 'phone_number 應該是字串'
    assert member.phone_number.startswith('09'), '台灣手機號碼應以 09 開頭'
    assert member.gender in ['male', 'female', 'other'], (
        'gender 應為 male/female/other 其中之一'
    )
    assert isinstance(member.date_of_birth, date), 'date_of_birth 應該是 date 類型'
    assert isinstance(member.created_at, datetime), 'created_at 應該是 datetime 類型'
    assert isinstance(member.updated_at, datetime), 'updated_at 應該是 datetime 類型'
    assert member.line_id is None or isinstance(member.line_id, str), (
        'line_id 可為 None 或字串'
    )
    assert member.google_id is None or isinstance(member.google_id, str), (
        'google_id 可為 None 或字串'
    )


# 驗證錯誤測試（Model Validation）
@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input,expected_messages',
    [
        (
            {'phone_number': '123'},
            {'phone_number': '手機號碼格式錯誤'},
        ),
        (
            {'gender': 'invalid'},
            {'gender': 'is not a valid choice'},
        ),
        (
            {'phone_number': '123', 'gender': 'invalid'},
            {
                'phone_number': '手機號碼格式錯誤',
                'gender': 'is not a valid choice',
            },
        ),
    ],
)
def test_member_validation_errors(member_factory, invalid_input, expected_messages):
    # 建立合法的預設資料
    valid_data = {
        'phone_number': '0912345678',
        'gender': 'male',
        'date_of_birth': date(1990, 1, 1),
    }

    # 將不合法欄位更新進去
    test_data = {**valid_data, **invalid_input}
    member = member_factory.build(**test_data)

    # 執行驗證並預期出現 ValidationError
    with pytest.raises(ValidationError) as exc_info:
        member.full_clean()

    validation_errors = exc_info.value.message_dict
    print(validation_errors)

    # 驗證每個欄位的錯誤訊息是否包含預期內容
    for field, expected_msg in expected_messages.items():
        assert field in validation_errors, f'{field} 沒有出現在錯誤訊息中'
        actual_msg = validation_errors[field][0]
        assert expected_msg in actual_msg, (
            f'{field} 錯誤訊息應包含: {expected_msg}，實際為: {actual_msg}'
        )


# TODO 關聯欄位測試
