from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import UserForm


def index(req):
    return render(req, 'pages/index.html')


def sign_up(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能註冊新帳號')
        return redirect('members:new' if req.user.is_member else 'stores:new')

    userform = UserForm()
    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
        },
    )


@transaction.atomic
def create_user(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能再建立新帳號')
        return redirect('members:index' if req.user.is_member else 'stores:index')

    userform = UserForm(req.POST)

    if userform.is_valid():
        user = userform.save(commit=False)
        user.role = 'member'
        user.save()
        return create_session(req)
    return render(req, 'users/sign_up.html', {'userform': userform})


# 顯示登入頁面 (GET)
def sign_in(req):
    return render(req, 'users/sign_in.html')


@require_POST
def create_session(req):
    email = req.POST.get('email')
    password = req.POST.get('password')
    # 因為上方create_user有用到這隻function，但是在註冊的時候沒有‘password’欄位，
    # 所以在這裏額外判斷是否有‘password2’
    if not password:
        password = req.POST.get('password2')

    user = authenticate(email=email, password=password)

    if user is None:
        messages.error(req, '帳號或密碼錯誤，請再試一次。')
        return render(req, 'users/sign_in.html')

    login(req, user)

    if user.is_member:
        messages.success(req, '會員登入成功！')
    elif user.is_store:
        messages.success(req, '店家登入成功！')
    else:
        logout(req)
        user.delete()
        messages.error(req, '帳號存在異常，請重新註冊')
        return redirect('users:sign_up')
    return redirect('stores:index')


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    messages.success(req, '已登出！')
    return redirect('users:sign_in')
