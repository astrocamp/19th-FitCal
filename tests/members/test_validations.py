from datetime import date

import pytest
from django.core.exceptions import ValidationError


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

    # 驗證每個欄位的錯誤訊息是否包含預期內容
    for field, expected_msg in expected_messages.items():
        assert field in validation_errors, f'{field} 沒有出現在錯誤訊息中'
        actual_msg = validation_errors[field][0]
        assert expected_msg in actual_msg, (
            f'{field} 錯誤訊息應包含: {expected_msg}，實際為: {actual_msg}'
        )
