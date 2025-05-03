from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


# Create your views here.
def index(request):
    if request.POST:
        form = ProductForm(request.POST)
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return redirect('product:show', product.id)
    else:
        products = Product.objects.all()
        return render(request, 'product/index.html', {'products': products})


def new(request):
    form = ProductForm()
    return render(request, 'product/new.html', {'form': form})


def show(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        form = ProductForm(request.POST, instance=product)
        form.save()
        return redirect('product:show', product.id)
    else:
        return render(request, 'product/show.html', {'product': product})


def edit(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(instance=product)
    return render(request, 'product/edit.html', {'product': product, 'form': form})


def delete(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    return redirect('product:index')
