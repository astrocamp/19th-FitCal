from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StoreForm
from .models import Store


@login_required
def index(request):
    store = getattr(request.user, 'store', None)

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('stores:show', store.id)
        else:
            return render(request, 'stores/new.html', {'form': form})
    else:
        return render(request, 'stores/index.html', {'store': store})


@login_required
def new(req):
    if hasattr(req.user, 'store'):
        return redirect('stores:show', req.user.store.id)
    # todo:先提供一個預設值方便測試，上線前移除
    form = StoreForm(initial={'tax_id': '22099131'})
    return render(req, 'stores/new.html', {'form': form})


@login_required
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


@login_required
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


@login_required
def delete(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    user = req.user

    store.delete()
    user.delete()
    logout(req)

    return redirect('users:sign_up')
