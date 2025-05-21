from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StoreForm
from .models import Store


def store_required(view_func):
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_store:
            messages.error(req, '您不是店家，無法訪問此頁面')
            return redirect('users:index')
        return view_func(req, *args, **kwargs)

    return login_required(_wrapped_view)


def new(req):
    form = StoreForm()
    return render(req, 'stores/new.html', {'form': form})


@store_required
@transaction.atomic
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('stores:show', store.id)
    form = StoreForm()
    return render(request, 'stores/new.html', {'form': form})


@store_required
@login_required
def index(request):
    store = Store.objects.filter(user=request.user).first()
    return render(request, 'stores/index.html', {'store': store})


@store_required
def show(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    products = store.products.all()
    if req.method == 'POST':
        form = StoreForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('stores:show', id=store.id)
        return render(
            req,
            'stores/show.html',
            {'store': store, 'form': form, 'products': products},
        )
    return render(
        req,
        'stores/show.html',
        {'store': store, 'products': products},
    )


@store_required
def edit(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    form = StoreForm(instance=store)
    return render(req, 'stores/edit.html', {'form': form, 'store': store})


@store_required
def delete(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    store.delete()
    return redirect('users:sign_up')
