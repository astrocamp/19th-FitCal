from anymail.message import AnymailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from locations.views import add_location
from stores.forms import StoreForm
from stores.views import handle_store_owner

from .forms import UserForm


def index(req):
    if hasattr(req.user, 'store'):
        return handle_store_owner(req)
    else:
        return render(req, 'pages/index.html')


# 顯示註冊頁面(會員)
def sign_up(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能註冊新帳號')
        return redirect('stores:index')

    userform = UserForm()
    return render(
        req,
        'users/sign_up.html',
        {
            'userform': userform,
        },
    )


# 顯示註冊頁面(店家)
def sign_up_store(req):
    if req.user.is_authenticated:
        messages.error(req, '你已登入')
        return redirect('stores:index')
    return render(
        req,
        'users/sign_up_store.html',
        {
            'userform': UserForm(),
            'storeform': StoreForm(),
        },
    )


# 建立會員帳號
@transaction.atomic
def create_user(req):
    if req.user.is_authenticated:
        messages.error(req, '你已經登入，不能再建立新帳號')
        return redirect('stores:index')

    userform = UserForm(req.POST)

    if userform.is_valid():
        user = userform.save(commit=False)
        user.role = 'member'
        user.save()
        # ✅ 發送 Mailgun 歡迎信
        message = AnymailMessage(
            subject='歡迎加入 FitCal',
            to=[user.email],  # 使用者的 email
            # to=[
            #     '@gmail.com'
            # ],  # 若你要測試用 Mailgun 的測試功能，可以使用這個
        )
        message.template_id = 'welcome_email'  # Mailgun 後台的 template 名稱
        message.merge_global_data = {
            'useremail': user.email,  # 對應 template 的變數
        }
        message.send()
        next_url = req.POST.get('next') or '/stores/'
        return create_session(req, next_url)
    else:
        return render(
            req,
            'users/sign_up.html',
            {
                'userform': userform,
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
        add_location(store, store.address)
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
        return redirect('users:index')
    return render(req, 'users/sign_in.html')


# 顯示登入頁面（店家）
def sign_in_store(req):
    if req.user.is_authenticated:
        messages.error(req, '你已登入')
        return redirect('stores:index')
    return render(req, 'users/sign_in_store.html')


# 登入處理（會員）
@require_POST
def create_session(req, next_url=None):
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
    if not next_url:
        next_url = (
            '/stores/' if req.POST.get('next') == '/' else req.POST.get('next')
        )  # 預設跳 stores 頁
    print(next_url)
    response = HttpResponse()
    response['HX-Redirect'] = next_url
    return response


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
