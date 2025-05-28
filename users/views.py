from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from stores.forms import StoreForm

from .forms import UserForm


def index(req):
    return render(req, 'pages/index.html')


def sign_up(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能註冊新帳號')
        return redirect('members:new' if req.user.is_member else 'stores:new')

    userform = UserForm(req.POST)
    if userform.is_valid():
        user = userform.save(commit=False)
        user.role = 'member'
        user.set_password(userform.cleaned_data['password1'])
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(req, user)
        return redirect('members:index')

    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
            'is_hidden': False,
        },
    )


# 建立店家帳號（包含 Store 資料）
@transaction.atomic
def create_user_store(req):
    if req.user.is_authenticated:
        messages.error(req, '你已登入，不能再建立帳號')
        return redirect('stores:index')

    userform = UserForm(req.POST)
    storeform = StoreForm(req.POST)

    if userform.is_valid() and storeform.is_valid():
        user = userform.save(commit=False)
        user.role = 'store'
        user.set_password(userform.cleaned_data['password1'])
        user.save()

        store = storeform.save(commit=False)
        store.user = user
        store.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(req, user)
        return redirect('stores:index')

    return render(
        req,
        'users/sign_up_store.html',
        {
            'userform': userform,
            'storeform': storeform,
        },
    )


# 顯示登入頁面（會員）
def sign_in(req):
    if req.user.is_authenticated:
        messages.error(req, '你已登入')
        return redirect('members:index')
    return render(req, 'users/sign_in.html')


# 顯示登入頁面（店家）
def sign_in_store(req):
    if req.user.is_authenticated:
        messages.error(req, '你已登入')
        return redirect('stores:index')
    return render(req, 'users/sign_in_store.html')


# 登入處理（會員）
@require_POST
def create_session(req):
    email = req.POST.get('email')
    password = req.POST.get('password')
    user = authenticate(email=email, password=password)

    if user is None or user.role != 'member':
        messages.error(req, '帳號或密碼錯誤，或此帳號非會員')
        return render(
            req,
            'users/sign_in.html',
            {
                'email': email,
            },
        )

    login(req, user)
    messages.success(req, '會員登入成功！')
    return redirect('members:index')


# 登入處理（店家）
@require_POST
def create_session_store(req):
    email = req.POST.get('email')
    password = req.POST.get('password')
    user = authenticate(email=email, password=password)

    if user is None or user.role != 'store':
        messages.error(req, '帳號或密碼錯誤，或此帳號非店家')
        return render(
            req,
            'users/sign_in_store.html',
            {
                'email': email,
            },
        )

    login(req, user)
    messages.success(req, '店家登入成功！')
    return redirect('stores:index')


# 登出處理
@require_POST
def delete_session(req):
    logout(req)
    messages.success(req, '已登出！')
    return redirect('users:index')
