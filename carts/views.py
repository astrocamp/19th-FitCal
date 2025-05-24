from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from common.decorator import member_required
from products.models import Product
from stores.models import Store

from .models import Cart, CartItem


@member_required
@require_POST
def create_cart_item(req, product_id):
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
        messages.success(req, '購物車已更新')
    except Exception:
        messages.error(req, '購物車更新失敗')
    return render(req, 'shared/messages.html')


@member_required
@require_POST
def update_cart_item(req, item_id):
    quantity = int(req.POST.get('quantity'))
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    innertext = ''
    try:
        if quantity < 1:
            return delete_cart_item(req, item_id)
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(req, '購物車已更新')
            innertext = f'{cart.calculate_total_price}'
    except Exception:
        messages.error(req, '購物車更新失敗')
    messages_html = render_to_string(
        'shared/messages.html', {'messages': get_messages(req)}
    )
    return HttpResponse(
        f'{innertext}'
        + f"""
        <div id="messages-container" hx-swap-oob="true">
            {messages_html}
        </div>
        """
    )


def index(req):
    member = req.user.member
    stores = Store.objects.filter(carts__member=member).distinct()
    carts = Cart.objects.filter(member=member)
    return render(
        req, 'carts/index.html', {'carts': carts, 'stores': stores, 'member': member}
    )


def show(req, id):
    member = req.user.member
    cart = get_object_or_404(Cart, id=id)
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


def delete_cart(req, id):
    cart = get_object_or_404(Cart, id=id)
    cart.delete()
    return redirect('carts:index')


def delete_cart_item(req, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    if cart.items.count() == 0:
        cart.delete()
        messages.success(req, '購物車已清空')
        if req.headers.get('HX-Request') == 'true':
            response = HttpResponse()
            response['HX-Redirect'] = reverse('carts:index')
            return response
        return redirect('carts:index')
    messages.success(req, f'{cart_item.product.name}已從購物車中刪除')
    return redirect('carts:show', id=cart_item.cart.id)
