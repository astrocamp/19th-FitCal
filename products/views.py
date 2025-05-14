from django.shortcuts import get_object_or_404, redirect, render

from members.models import Member
from stores.models import Store

from .forms import ProductForm
from .models import Product


# Create your views here.
def index(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            store_id = request.POST.get('store_id')
            store = get_object_or_404(Store, id=store_id)
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('stores:show', id=store.id)
    else:
        form = ProductForm()
    products = Product.objects.all()
    members = Member.objects.all()
    return render(
        request,
        'products/index.html',
        {'products': products, 'form': form, 'members': members},
    )


def new(request, store_id):
    store = get_object_or_404(
        Store,
        id=store_id,
    )
    form = ProductForm(request.POST, request.FILES)
    if request.POST:
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('products:show', product.id)
    else:
        form = ProductForm()
    return render(request, 'products/new.html', {'form': form, 'store': store})


def show(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
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
