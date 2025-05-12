from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, UserForm


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
        return redirect('pages:index')
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
    if req.method == 'POST':
        form = LoginForm(req.POST)
        if form.is_valid():
            login(req, form.user)
            messages.success(req, '登入成功，歡迎回來！')
            return redirect('pages:home')
        else:
            messages.error(req, '登入失敗')
    else:
        form = LoginForm()
    return render(req, 'users/sign_in.html', {'form': form})


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    return redirect('pages:index')
