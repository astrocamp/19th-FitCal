from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from common.decorator import member_required, store_required
from stores.models import Category, Store

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
    return render(
        request,
        'products/index.html',
        {'products': products, 'form': form},
    )


def new(request, category_id):
    store = request.user.store
    category = get_object_or_404(Category, id=category_id)
    form = ProductForm(store=store, category=category)
    return render(
        request,
        'shared/business/products/new_product.html',
        {'form': form, 'category': category},
    )


def show(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.POST:
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products:show', product.id)
    return render(
        request,
        'products/show.html',
        {
            'product': product,
            'quantity_range': range(1, 101),
        },
    )


@store_required
@require_POST
def create(request, category_id):
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        form = form.save(commit=False)
        form.store = request.user.store
        form.save()
        category = get_object_or_404(
            Category.objects.prefetch_related('products'), id=category_id
        )
        products = category.products.filter(store=request.user.store)
        messages.success(request, f'商品 {form.name} 已新增')
        return render(
            request,
            'shared/business/products/create_success.html',
            {'products': products, 'category': category},
        )
    return render(request, 'products/create.html', {'form': form})


@store_required
def edit(request, id):
    store = request.user.store
    product = get_object_or_404(Product, pk=id)
    category = product.category
    form = ProductForm(instance=product, store=store, category=category)
    return render(
        request,
        'shared/business/products/edit_product.html',
        {'form': form, 'category': category, 'product': product},
    )


@store_required
@require_POST
def update(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
        form = form.save(commit=False)
        # form.store = request.user.store
        form.save()
        messages.success(request, f'商品 {product.name} 已更新')
        category = product.category
        products = Product.objects.prefetch_related('category').filter(
            category=category, store=request.user.store
        )
        return redirect(
            request,
            'shared/business/products/create_success.html',
            {'products': products, 'category': category},
        )
    return render(
        request,
        'shared/business/products/edit_product.html',
        {'form': form, 'category': category},
    )


def delete(request, id):
    product = get_object_or_404(Product, pk=id)
    category = product.category
    product.delete()
    products = Product.objects.prefetch_related('category').filter(
        category=category, store=request.user.store
    )
    messages.success(request, f'商品 {product.name} 已刪除')
    return redirect(
        request,
        'stores/business/product_list.html',
        {'products': products, 'category': category},
    )


@member_required
def collections(request, id):
    product = get_object_or_404(Product, id=id)
    member = request.user.member  # 正常從user取出member

    collections = member.favorite_products

    if collections.filter(id=product.id).exists():
        collections.remove(product)
    else:
        collections.add(product)

    return render(
        request,
        'shared/collections_btn.html',
        {
            'member': member,
            'product': product,
        },
    )
