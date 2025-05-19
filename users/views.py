from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import UserForm


def select_role(req):
    return render(req, 'users/select_role.html')


def sign_up(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能註冊新帳號')
        return redirect(
            'members:index' if hasattr(req.user, 'member') else 'stores:index'
        )

    role = req.GET.get('role')
    if role not in ['member', 'store']:
        return redirect('users:select_role')

    userform = UserForm()
    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
            'role': role,
        },
    )


@require_POST
def create_user(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能再建立新帳號')
        return redirect(
            'members:index' if hasattr(req.user, 'member') else 'stores:index'
        )

    userform = UserForm(req.POST)
    role = req.POST.get('role')

    if role not in ['member', 'store']:
        return render(
            req,
            'users/sign_up.html',
            {
                'userform': userform,
                'error': '請選擇有效的角色。',
            },
        )

    if userform.is_valid():
        user = userform.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(req, user)

        if role == 'member':
            return redirect('members:new')
        else:
            return redirect('stores:new')

    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
            'role': role,
        },
    )


# 顯示登入頁面 (GET)
def sign_in(req):
    role = req.GET.get('role', '')
    return render(req, 'users/sign_in.html', {'role': role})


@require_POST
def create_session(req):
    email = req.POST.get('email')
    password = req.POST.get('password')

    user = authenticate(email=email, password=password)

    if user is None:
        return render(
            req,
            'users/sign_in.html',
            {
                'error': '帳號或密碼錯誤，請再試一次。',
                'email': email,
            },
        )

    login(req, user)

    if hasattr(user, 'member'):
        messages.success(req, '會員登入成功！')
        return redirect('members:show', user.member.id)
    elif hasattr(user, 'store'):
        messages.success(req, '店家登入成功！')
        return redirect('stores:show', user.store.id)
    else:
        user.delete()
        logout(req)
        return redirect('users:select_role')


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    messages.success(req, '已登出！')
    return redirect('users:select_role')
