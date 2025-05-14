from datetime import date

import pytest

from members.models import Member


@pytest.mark.django_db
def test_member_create(member_factory):
    # 使用工廠創建一個 member 實例
    member = member_factory(date_of_birth=date(1990, 1, 1))

    assert member.phone_number
    assert member.gender in ['male', 'female', 'other']
    assert member.date_of_birth == date(1990, 1, 1)

    member.save()
    assert Member.objects.count() == 1


@pytest.mark.django_db
def test_member_read(member_factory):
    member = member_factory(phone_number='0912345678', date_of_birth=date(2000, 12, 1))
    member.save()

    # 查詢該 member
    retrieved_member = Member.objects.get(phone_number='0912345678')

    assert retrieved_member.phone_number == '0912345678'
    assert retrieved_member.gender in ['male', 'female', 'other']
    assert retrieved_member.date_of_birth == date(2000, 12, 1)


@pytest.mark.django_db
def test_member_update(member_factory):
    member = member_factory(phone_number='0912345678', gender='male')
    member.save()

    # 更新資料
    member.phone_number = '0987654321'
    member.gender = 'female'
    member.save()

    updated_member = Member.objects.get(phone_number='0987654321')
    assert updated_member.phone_number == '0987654321'
    assert updated_member.gender == 'female'


@pytest.mark.django_db
def test_member_delete(member_factory):
    member = member_factory(phone_number='0912345678')
    member.save()

    # 刪除該 member
    member.delete()

    # 驗證該 member 是否已經被刪除
    with pytest.raises(Member.DoesNotExist):
        Member.objects.get(phone_number='0912345678')
