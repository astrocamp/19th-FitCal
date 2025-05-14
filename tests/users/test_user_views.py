import pytest
from django.urls import reverse

from users.forms import UserForm
from users.models import User


@pytest.mark.django_db
def test_sign_up_view_get(client):
    url = reverse('users:sign_up')
    response = client.get(url)

    assert response.status_code == 200
    assert 'users/sign_up.html' in [t.name for t in response.templates]
    assert 'userform' in response.context
    assert isinstance(response.context['userform'], UserForm)


@pytest.mark.django_db
def test_create_user_valid(client):
    valid_data = {
        'email': 'test@example.com',
        'password1': 'StrongPass1357',
        'password2': 'StrongPass1357',
    }
    url = reverse('users:create_user')
    response = client.post(url, data=valid_data)

    assert response.status_code == 302
    assert response.url == reverse('pages:index')
    assert User.objects.filter(email='test@example.com').exists()


@pytest.mark.django_db
def test_create_user_invalid(client):
    invalid_data = {
        'email': 'test@example.com',
        'password1': 'StrongPass1357',
        'password2': 'WrongPass9876',
    }
    url = reverse('users:create_user')
    response = client.post(url, data=invalid_data)

    # 應該會返回 200 並重新渲染表單頁面
    assert response.status_code == 200
    assert 'users/sign_up.html' in [t.name for t in response.templates]
    assert 'userform' in response.context
    assert response.context['userform'].errors
    assert not User.objects.exists()


@pytest.mark.django_db
def test_sign_in_view(client):
    url = reverse('users:sign_in')  # 確保你的 URL name 是 'sign_in'
    response = client.get(url)

    assert response.status_code == 200
    assert 'users/sign_in.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_session_success(client, user_factory):
    # 建立一個已存在的使用者
    password = 'validpassword123'
    user = user_factory(password=password)
    user.set_password(password)
    user.save()

    url = reverse('users:create_session')
    data = {
        'email': user.email,
        'password': password,
    }
    response = client.post(url, data)

    # 成功登入應該重導到首頁
    assert response.status_code == 302
    assert response.url == reverse('pages:index')


@pytest.mark.django_db
def test_create_session_fail_invalid_credentials(client):
    url = reverse('users:create_session')
    data = {
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword',
    }
    response = client.post(url, data)

    # 登入失敗應該重導回登入頁
    assert response.status_code == 302
    assert response.url == reverse('users:sign_in')
