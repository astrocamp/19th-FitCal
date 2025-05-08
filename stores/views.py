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
            return render(req, 'stores/index.html', {'stores': stores, 'form': form})
    else:
        form = StoreForm()
        return render(req, 'stores/index.html', {'stores': stores, 'form': form})


def new(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            return redirect('stores:show', store.id)
        return render(request, 'stores/new.html', {'form': form})
    else:
        form = StoreForm()
        return render(request, 'stores/new.html', {'form': form})


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


def edit(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', store.id)  # 成功更新後，重定向到展示頁面
        else:
            # 如果表單驗證失敗，留在編輯頁面，顯示錯誤
            return render(request, 'stores/edit.html', {'form': form, 'store': store})
    else:
        form = StoreForm(instance=store)
        return render(request, 'stores/edit.html', {'form': form, 'store': store})


def delete(req, id):
    store = get_object_or_404(Store, pk=id)
    store.delete()

    return redirect('stores:index')
