import pytest

from users.models import User


@pytest.mark.django_db
def test_user_create(user_factory):
    raw_password = 'qwertyui1357'
    user = user_factory(email='abc12345@gmail.com')
    user.set_password(raw_password)
    user.save()

    assert user.email == 'abc12345@gmail.com'
    assert User.objects.count() == 1
    assert user.check_password(raw_password)


@pytest.mark.django_db
def test_user_read(user_factory):
    user = user_factory(email='abc54321@gmail.com')
    user.save()

    # 查詢該 user
    retrieved_user = User.objects.get(email='abc54321@gmail.com')

    assert retrieved_user.email == 'abc54321@gmail.com'


@pytest.mark.django_db
def test_user_update(user_factory):
    user = user_factory(email='abc54321@gmail.com')
    user.save()

    # 更新資料
    user.email = 'cba12345@gmail.com'
    user.save()

    updated_user = User.objects.get(email='cba12345@gmail.com')
    assert updated_user.email == 'cba12345@gmail.com'


@pytest.mark.django_db
def test_user_delete(user_factory):
    user = user_factory(email='abc54321@gmail.com')
    user.save()

    # 刪除該 user
    user.delete()

    # 驗證該 user 是否已經被刪除
    with pytest.raises(User.DoesNotExist):
        User.objects.get(email='abc54321@gmail.com')
