import uuid
from datetime import date, datetime

import pytest


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
