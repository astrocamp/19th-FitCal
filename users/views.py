from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
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
        userform.save()
        to_email = userform.cleaned_data['email']
        send_mail(
            subject='歡迎加入本站！',
            message='您好，感謝您的註冊，祝您使用愉快！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )

        user = authenticate(
            email=userform.cleaned_data['email'],
            password=userform.cleaned_data['password2'],
        )
        login(req, user)
        messages.success(req, '註冊成功已登入！')
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
