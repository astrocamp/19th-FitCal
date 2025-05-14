from django.shortcuts import get_object_or_404, redirect, render

from stores.models import Store

from .forms import ProductForm
from .models import Product


# Create your views here.
def index(request):
    if request.POST:
        form = ProductForm(request.POST)
        product = form.save()
        return redirect('products:show', product.id)
    products = Product.objects.all()
    return render(request, 'products/index.html', {'products': products})


def new(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('stores:show', id=store.id)
    else:
        form = ProductForm()
    return render(request, 'products/new.html', {'form': form, 'store': store})


def show(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        form = ProductForm(request.POST, instance=product)
        form.save()
        return redirect('products:show', product.id)
    return render(request, 'products/show.html', {'product': product})


def edit(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(instance=product)
    return render(request, 'products/edit.html', {'product': product, 'form': form})


def delete(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    return redirect('products:index')
