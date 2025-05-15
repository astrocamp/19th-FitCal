from django.shortcuts import get_object_or_404, redirect, render

from .forms import StoreForm
from .models import Store


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
    # todo:先提供一個預設值方便測試，上線前移除
    form = StoreForm(initial={'tax_id': '22099131'})
    return render(req, 'stores/new.html', {'form': form})


def show(req, id):
    store = get_object_or_404(Store, pk=id)

    if req.method == 'POST':
        form = StoreForm(req.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', store.id)
        return render(req, 'stores/show.html', {'store': store, 'form': form})

    else:
        form = StoreForm(instance=store)

        return render(
            req,
            'stores/show.html',
            {'store': store, 'form': form},
        )


def edit(req, store_id):
    store = get_object_or_404(Store, id=store_id)

    if req.method == 'POST':
        form = StoreForm(req.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', store.id)
        return render(req, 'stores/edit.html', {'form': form, 'store': store})
    else:
        form = StoreForm(instance=store)
        return render(req, 'stores/edit.html', {'form': form, 'store': store})


def delete(req, id):
    store = get_object_or_404(Store, pk=id)
    store.delete()

    return redirect('stores:index')
