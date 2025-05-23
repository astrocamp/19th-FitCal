from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from stores.models import Store

from .forms import CartForm, EditCartItemFormSet, NewCartItemFormSet
from .models import Cart, CartItem
from .utils import add_to_cart


# 這裏是後續以member關聯的購物車的相關功能
@require_POST
def add(req):
    product_id = req.POST.get('product_id')
    quantity = req.POST.get('quantity')
    print(product_id, quantity)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商品不存在'})

    cart, created = Cart.objects.get_or_create(
        member=req.user.member, store=product.store, total_price=0
    )
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        return JsonResponse({'success': True, 'message': '商品已成功加入購物車'})
    else:
        cart_item.quantity += int(quantity)
        cart_item.save()
        return JsonResponse(
            {'success': True, 'message': '購物車中已存在該商品，數量+1'}
        )


def index(req):
    member = req.user.member
    stores = Store.objects.filter(carts__member=member).distinct()
    carts = Cart.objects.filter(member=member)

    if req.method == 'POST':
        cart_form = CartForm(req.POST)
        formset = NewCartItemFormSet(req.POST)
        if cart_form.is_valid() and formset.is_valid():
            add_to_cart(member, cart_form, formset)
            return redirect('carts:index')
        else:
            return render(
                req,
                'carts/new.html',
                {
                    'cart_form': cart_form,
                    'formset': formset,
                    'stores': stores,
                },
            )
    return render(
        req, 'carts/index.html', {'carts': carts, 'stores': stores, 'member': member}
    )


def new(req):
    cart_form = CartForm()
    formset = NewCartItemFormSet()

    return render(
        req,
        'carts/new.html',
        {
            'cart_form': cart_form,
            'formset': formset,
        },
    )


def show(req, id):
    member = req.user.member
    cart = get_object_or_404(Cart, id=id)
    # cart_item = CartItem.objects.filter(cart=cart)
    # carts = Cart.objects.filter(member=req.user)
    if req.method == 'POST':
        formset = EditCartItemFormSet(req.POST, instance=cart)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    form.save()
        else:
            return render(
                req,
                'carts/edit.html',
                {
                    'cart_form': CartForm(instance=cart),
                    'formset': formset,
                    'id': id,
                },
            )
    if cart.items.count() == 0:
        return delete_cart(req, id)
    cart_item = CartItem.objects.filter(cart__member=member, cart=cart)
    return render(
        req,
        'carts/show.html',
        {
            'member': member,
            'cart': cart,
            'cart_item': cart_item,
        },
    )


def edit(req, id):
    cart = get_object_or_404(Cart, id=id)
    cart_form = CartForm(instance=cart)
    formset = EditCartItemFormSet(instance=cart)

    return render(
        req,
        'carts/edit.html',
        {'cart_form': cart_form, 'formset': formset, 'id': id},
    )


def delete_cart(req, id):
    cart = get_object_or_404(Cart, id=id)
    cart.delete()
    return redirect('carts:index')


def delete_item(req, id, from_show=False):
    cart_item = get_object_or_404(CartItem, id=id)
    cart = cart_item.cart
    cart_item.delete()
    if cart.items.count() == 0:
        cart.delete()
        return redirect('carts:index')
    return redirect('carts:show', id=cart_item.cart.id)
