from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import UserForm

from .forms import StoreForm
from .models import Store


def store_required(view_func):
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not hasattr(req.user, 'store'):
            messages.error(req, '您不是店家，無法訪問此頁面')
            return redirect('users:select_role')
        return view_func(req, *args, **kwargs)

    return login_required(_wrapped_view)

def index(req):
    stores = Store.objects.all()
    if req.method == 'POST':
        form = StoreForm(req.POST)
        if form.is_valid():
            store = form.save()
            return redirect('stores:show', store.id)
        else:
            return render(req, 'stores/new.html', {'form': form})
    else:
        return render(req, 'stores/index.html', {'stores': stores})


def new(req):
    form = StoreForm()
    return render(req, 'stores/new.html', {'form': form})


@transaction.atomic
def create_store(request):
    user_data = request.session.get('temp_user_data')
    role = request.session.get('temp_user_role')

    if not user_data or role != 'store':
        messages.error(request, '註冊流程不完整，請重新開始')
        return redirect('users:select_role')

    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            user_form = UserForm(user_data)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()

                store = form.save(commit=False)
                store.user = user
                store.save()

                user.is_active = True
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                user.save()

                login(request, user)

                del request.session['temp_user_data']
                del request.session['temp_user_role']

                return redirect('stores:show', store.id)
            else:
                messages.error(request, '帳號資料驗證失敗，請重新註冊')
                return redirect('users:sign_up')
    else:
        form = StoreForm()

    return render(request, 'stores/new.html', {'form': form})


@login_required
def index(request):
    try:
        store = request.user.store
    except Store.DoesNotExist:
        return redirect('stores:new')
    return render(request, 'stores/index.html', {'store': store})


@store_required
def show(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    products = store.products.all()

    if req.method == 'POST':
        form = StoreForm(req.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', id=store.id)
        return render(
            req,
            'stores/show.html',
            {'store': store, 'form': form, 'products': products},
        )

    else:
        form = StoreForm(instance=store)

        return render(
            req,
            'stores/show.html',
            {'store': store, 'form': form, 'products': products},
        )


@store_required
def edit(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)

    if req.method == 'POST':
        form = StoreForm(req.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', store.id)
        else:
            return render(req, 'stores/edit.html', {'form': form, 'store': store})
    else:
        form = StoreForm(instance=store)
        return render(req, 'stores/edit.html', {'form': form, 'store': store})


@store_required
def delete(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    user = req.user

    store.delete()
    user.delete()
    logout(req)

    return redirect('users:sign_up')
