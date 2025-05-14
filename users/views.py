from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from members.models import Member

from .forms import UserForm


def select_role(req):
    return render(req, 'users/select_role.html')


# 顯示註冊表單 (GET)
def sign_up(req):
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


# 處理註冊 (POST)
@require_POST
def create_user(req):
    userform = UserForm(req.POST)
    role = req.POST.get('role')  # 'member' 或 'store'

    if role not in ['member', 'store']:
        return render(
            req,
            'users/sign_up.html',
            {
                'userform': userform,
                'error': '請選擇有效的角色。',
            },
        )

    # 檢查 email 是否已存在
    email = req.POST.get('email')
    User = get_user_model()
    if User.objects.filter(email=email).exists():
        return render(
            req,
            'users/sign_up.html',
            {
                'userform': userform,
                'role': role,
                'error': '此帳號已存在，請使用登入功能。',
            },
        )

    # 驗證表單是否合法
    if userform.is_valid():
        user = userform.save()

        # 防止同帳號有多個身分
        if hasattr(user, 'store') or hasattr(user, 'member'):
            return render(
                req,
                'users/sign_up.html',
                {
                    'userform': userform,
                    'role': role,
                    'error': '該帳號已經擁有會員或店家身份。',
                },
            )

        # 登入帳號
        user = authenticate(
            email=userform.cleaned_data['email'],
            password=userform.cleaned_data['password2'],
        )
        login(req, user)

        # 根據角色建立資料
        if role == 'member':
            Member.objects.create(user=user, name=user.email)
            return redirect('members:new')
        else:
            Store.objects.create(user=user, name=user.email)
            return redirect('stores:new')

    # 表單驗證失敗
    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
            'role': role,
            'error': '註冊失敗，請確認所有欄位是否正確填寫。',
        },
    )


# 顯示登入頁面 (GET)
def sign_in(req):
    role = req.GET.get('role', '')
    return render(req, 'users/sign_in.html', {'role': role})


# 處理登入 (POST)
@require_POST
def create_session(req):
    email = req.POST.get('email')
    password = req.POST.get('password')
    role = req.POST.get('role')

    user = authenticate(email=email, password=password)

    if user is not None:
        if role == 'member' and hasattr(user, 'store'):
            return render(
                req,
                'users/sign_in.html',
                {
                    'error': '您已註冊為店家，請使用店家身份登入。',
                    'email': email,
                    'role': role,
                },
            )
        elif role == 'store' and hasattr(user, 'member'):
            return render(
                req,
                'users/sign_in.html',
                {
                    'error': '您已註冊為會員，請使用會員身份登入。',
                    'email': email,
                    'role': role,
                },
            )

        login(req, user)

        try:
            messages.success(req, '登入成功！')
            return redirect('stores:show', user.store.id)
        except Store.DoesNotExist:
            messages.success(req, '登入成功！')
            return redirect('members:show', user.member.id)

    return render(
        req,
        'users/sign_in.html',
        {
            'error': '帳號或密碼錯誤，請再試一次。',
            'email': email,
            'role': role,
        },
    )


# 處理登出 (POST)
@require_POST
def delete_session(req):
    logout(req)
    messages.success(req, '已登出！')
    return redirect('pages:index')
