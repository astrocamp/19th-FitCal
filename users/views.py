from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from members.models import Member
from stores.models import Store

from .forms import UserForm


# 顯示註冊表單 (GET)
def sign_up(req):
    userform = UserForm()
    return render(req, 'users/sign_up.html', {'userform': userform})


# 處理註冊 (POST)
@require_POST
def create_user(req):
    userform = UserForm(req.POST)
    role = req.POST.get('role')  # 'member' 或 'store'

    if userform.is_valid() and role in ['member', 'store']:
        user = userform.save()
        login(req, user)

        if role == 'member':
            from members.models import Member

            Member.objects.create(user=user, name=user.email)  # 可自定義 name 欄位值
            return redirect('members:new')

        elif role == 'store':
            from stores.models import Store

            Store.objects.create(user=user, name=user.email)  # 可自定義 name 欄位值
            return redirect('stores:new')

    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
            'error': '註冊失敗，請確認所有欄位與身份選擇',
        },
    )


# 顯示登入頁面 (GET)
def sign_in(req):
    return render(req, 'users/sign_in.html')


# 處理登入 (POST)
@require_POST
def create_session(req):
    email = req.POST.get('email')
    password = req.POST.get('password')
    next_page = req.POST.get('next', '/')
    User = get_user_model()

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # 帳號不存在，導向註冊頁
        return redirect('users:sign_up')

    user = authenticate(
        email=email,
        password=password,
    )
    if user is not None:
        login(req, user)
        return redirect('users:login_redirect')
    else:
        return render(
            req, 'users/sign_in.html', {'error': '密碼錯誤，請再試一次', 'email': email}
        )


@login_required
def login_redirect(req):
    user = req.user

    try:
        store = user.store  # 透過一對一關聯取得 Store
        return redirect('stores:show', store.id)
    except Store.DoesNotExist:
        pass

    try:
        member = user.member  # 若不是店家則檢查是否為會員
        return redirect('members:show', member.id)
    except Member.DoesNotExist:
        pass

    return render(
        req,
        'users/sign_in.html',
        {'error': '尚未設定會員或店家身份，請重新註冊。', 'email': user.email},
    )


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    return redirect('pages:index')
