import pytest
from django.urls import reverse

from members.models import Member


@pytest.mark.django_db
def test_member_index_get_view(client, member_factory):
    member_factory.create_batch(3)
    url = reverse('members:index')
    response = client.get(url)

    assert response.status_code == 200
    assert 'members' in response.context
    assert len(response.context['members']) == 3


@pytest.mark.django_db
def test_member_index_post_valid(client):
    url = reverse('members:index')
    data = {
        'phone_number': '0912345678',
        'gender': 'male',
        'date_of_birth': '1990-01-01',
    }
    response = client.post(url, data)

    assert response.status_code == 302  # Redirect
    assert Member.objects.count() == 1


@pytest.mark.django_db
def test_member_index_post_invalid(client):
    url = reverse('members:index')
    data = {
        'phone_number': 'invalid',  # 格式錯誤
        'gender': 'invalid',
        'date_of_birth': '1990-01-01',
    }
    response = client.post(url, data)

    assert response.status_code == 200  # 回到 form 頁面
    assert 'form' in response.context
    assert response.context['form'].errors
    assert Member.objects.count() == 0


@pytest.mark.django_db
def test_member_new_view(client):
    url = reverse('members:new')  # 假設你在 urls.py 有設定 name='new'
    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'members/new.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_member_show_view_get(client, member_factory):
    member = member_factory()
    url = reverse('members:show', args=[member.id])
    response = client.get(url)

    assert response.status_code == 200
    assert 'member' in response.context
    assert response.context['member'].id == member.id
    assert 'members/show.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_member_show_view_post_valid_data(client, member_factory):
    member = member_factory(phone_number='0912345678')
    url = reverse('members:show', args=[member.id])
    data = {
        'phone_number': '0987654321',
        'gender': member.gender,
        'date_of_birth': member.date_of_birth.strftime('%Y-%m-%d'),
    }

    response = client.post(url, data)

    assert response.status_code == 302  # redirect
    member.refresh_from_db()  # 確保更新後的資料被重新讀入
    assert member.phone_number == '0987654321'


@pytest.mark.django_db
def test_member_show_view_post_invalid_data(client, member_factory):
    member = member_factory()
    url = reverse('members:show', args=[member.id])
    data = {
        'phone_number': '123',  # 無效格式
        'gender': member.gender,
        'date_of_birth': member.date_of_birth.strftime('%Y-%m-%d'),
    }

    response = client.post(url, data)

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
    assert 'members/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_member_edit_view_get(client, member_factory):
    # 建立測試用的 member
    member = member_factory()
    # 假設 URL pattern 是 members:edit 對應 path('<int:id>/edit/', views.edit, name='edit')
    url = reverse('members:edit', args=[member.id])

    response = client.get(url)

    assert response.status_code == 200
    assert 'form' in response.context
    assert 'member' in response.context
    assert response.context['member'].id == member.id
    assert response.context['form'].instance == member
    assert 'members/edit.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_member_delete_view(client, member_factory):
    # 建立測試用 member
    member = member_factory()
    url = reverse('members:delete', args=[member.id])

    # 先確認 member 存在於資料庫
    assert Member.objects.filter(id=member.id).exists()

    response = client.post(url)

    # 再確認 member 已被刪除
    assert response.status_code == 302  # Redirect
    assert response.url == reverse('members:index')
    assert not Member.objects.filter(id=member.id).exists()
