from datetime import date

import pytest

from tests.constants import *
from tests.helpers import assert_validation_errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    'invalid_input,expected_messages',
    [
        ({'phone_number': '123'}, {'phone_number': INVALID_PHONE_MSG}),
        ({'gender': 'invalid'}, {'gender': INVALID_GENDER_MSG}),
        (
            {'phone_number': '123', 'gender': 'invalid'},
            {'phone_number': INVALID_PHONE_MSG, 'gender': INVALID_GENDER_MSG},
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

    assert_validation_errors(member, expected_messages)
