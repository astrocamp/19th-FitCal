import uuid

import pytest


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_user_factory_is_valid(user_factory):
    user = user_factory()
    user.full_clean()


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_user_model_fields(user_factory):
    user = user_factory.create()
    assert isinstance(user.id, uuid.UUID)
    assert '@' in user.email
    assert user.check_password('defaultpassword123')
