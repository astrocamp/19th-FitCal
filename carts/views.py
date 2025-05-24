from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from common.decorator import member_required
from products.models import Product
from stores.models import Store

from .forms import CartForm, EditCartItemFormSet, NewCartItemFormSet
from .models import Cart, CartItem
from .utils import add_to_cart


@member_required
@require_POST
def add_item(req, product_id):
    quantity = req.POST.get('quantity')
    member = req.user.member
    product = get_object_or_404(Product, id=product_id)
    store = product.store
    cart, _ = Cart.objects.get_or_create(member=member, store=store)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    try:
        if created:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            cart_item.quantity += int(quantity)
            cart_item.save()
        cart.update_total_price()
        messages.success(req, '購物車已更新')
    except Exception:
        messages.error(req, '購物車更新失敗')
    return render(req, 'shared/messages.html')


@member_required
@require_POST
def edit_item(req, item_id):
    quantity = int(req.POST.get('quantity'))
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    try:
        if quantity < 1:
            cart_item.delete()
            messages.success(req, f'{cart_item.product.name}已從購物車中刪除')
            messages_html = render_to_string(
                'shared/messages.html', {'messages': get_messages(req)}
            )
            return HttpResponse(
                ''  # 空字串讓商品區塊被清空
                + f"""
                <template hx-swap-oob="true">
                    {messages_html}
                </template>
                """
            )
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(req, '購物車已更新')
        cart.update_total_price()
    except Exception:
        messages.error(req, '購物車更新失敗')
    return render(req, 'shared/messages.html')


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
