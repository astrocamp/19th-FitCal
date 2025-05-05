from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StoreForm
from .models import Store


@login_required
def index(request):
    # 如果使用者已有店家，導向該店家頁面
    if hasattr(request.user, 'store'):
        return redirect('stores:show', pk=request.user.store.pk)
    else:
        return redirect('stores:new')


@login_required
def new(request):
    # 如果已有店家，不允許再創建
    if hasattr(request.user, 'store'):
        messages.info(request, '您已經有一間店家了')
        return redirect('stores:show', pk=request.user.store.pk)

    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            messages.success(request, '店家創建成功')
            return redirect('stores:show', pk=store.pk)
    else:
        form = StoreForm()

    return render(request, 'stores/new.html', {'form': form})


@login_required
def show(request, pk):
    store = get_object_or_404(Store, pk=pk)

    if request.user != store.user:
        messages.error(request, '您無權查看此店家')
        return redirect('stores:index')

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, '店家資訊更新成功')
            return redirect('stores:show', pk=store.pk)
    else:
        form = StoreForm(instance=store)

    return render(request, 'stores/show.html', {'store': store})


@login_required
def edit(request, pk):
    store = get_object_or_404(Store, pk=pk)

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, '店家資訊更新成功')
            return redirect('stores:show', pk=store.pk)
    else:
        form = StoreForm(instance=store)

    return render(request, 'stores/edit.html', {'form': form, 'store': store})


# 用戶註冊頁面，創建一個對應的 auth_user 帳號
def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 創建店家，並將用戶與店家綁定
            store = Store.objects.create(user=user)
            store.save()
            messages.success(request, '註冊成功，您現在可以創建店家')
            login(request, user)  # 登入該用戶
            return redirect('stores:show', store.pk)  # 註冊成功後跳轉到店家頁面
    else:
        form = UserCreationForm()

    return render(
        request,
        'stores/sign_up.html',
        {'form': form},
    )


# 用戶登入頁面
def sign_in(request):
    if request.user.is_authenticated:
        return redirect('stores:index')  # 如果已經登入，重定向到商店首頁

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, '登入成功')
            next_url = request.GET.get(
                'next', 'stores:index'
            )  # 重定向到原先的頁面或首頁
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(
        request,
        'stores/sign_in.html',
        {'form': form},
    )


# 登入認證用的視圖
@require_POST
def create_session(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        next_url = request.POST.get('next', 'stores:index')
        messages.success(request, '登入成功')
        return redirect(next_url)
    else:
        messages.error(request, '登入失敗，請檢查帳號或密碼')
        return redirect('stores:sign_in')


# 用戶登出視圖
@require_POST
def delete_session(request):
    logout(request)
    messages.success(request, '已登出')
    return redirect('stores:index')


# 刪除店家功能
@login_required
def delete(request, pk):
    store = get_object_or_404(Store, pk=pk)

    # 確保該用戶是該店家的擁有者
    if store.user == request.user:
        store.delete()
        messages.success(request, '店家已刪除')
        return redirect('stores:index')
    else:
        messages.error(request, '您無權刪除此店家')
        return redirect('stores:index')
