from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import UserForm


# 顯示註冊表單 (GET)
def sign_up(req):
    userform = UserForm()
    return render(req, 'users/sign_up.html', {'userform': userform})


# 處理註冊 (POST)
@require_POST
def create_user(req):
    userform = UserForm(req.POST)
    if userform.is_valid():
        user = userform.save()
        login(req, user)
        messages.success(req, '註冊成功已登入！')
        return redirect('pages:index')
    messages.error(req, '帳號或密碼錯誤')
    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
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
    user = authenticate(
        email=email,
        password=password,
    )
    if user is not None:
        login(req, user)
        messages.success(req, '登入成功！')
        return redirect('pages:index')
    else:
        messages.error(req, '登入失敗，請檢查電子郵件或密碼是否正確')
        return redirect('users:sign_in')


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    messages.success(req, '已登出！')
    return redirect('pages:index')
