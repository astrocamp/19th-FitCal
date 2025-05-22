from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from common.decorator import store_required

from .forms import StoreForm
from .models import Store


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


@login_required
def index(request):
    stores = Store.objects.all()
    store = Store.objects.filter(user=request.user).first()
    return render(request, 'stores/index.html', {'stores': stores, 'store': store})


def show(req, id):
    store = get_object_or_404(Store, pk=id)
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
