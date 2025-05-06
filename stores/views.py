from django.shortcuts import get_object_or_404, redirect, render

from .forms import StoreForm
from .models import Store


def index(req):
    if req.POST:
        form = StoreForm(req.POST)
        store = form.save()
        return redirect('stores:show', store.id)
    else:
        stores = Store.objects.order_by('-id')
    return render(
        req,
        'stores/index.html',
        {'stores': stores},
    )


def new(req):
    form = StoreForm()
    return render(
        req,
        'stores/new.html',
        {'form': form},
    )


def show(req, id):
    store = get_object_or_404(Store, pk=id)

    if req.POST:
        form = StoreForm(req.POST, instance=store)
        form.save()
        return redirect('stores:show', store.id)
    else:
        return render(
            req,
            'stores/show.html',
            {'store': store},
        )


def edit(req, id):
    store = get_object_or_404(Store, pk=id)
    form = StoreForm(instance=store)
    return render(
        req,
        'stores/edit.html',
        {
            'store': store,
            'form': form,
        },
    )


def delete(req, id):
    store = get_object_or_404(Store, pk=id)
    store.delete()

    return redirect('stores:index')
