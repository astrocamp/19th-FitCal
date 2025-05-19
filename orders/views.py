from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import Cart

from .forms import OrderForm
from .models import Order, OrderItem
from .services import OrderService


@transaction.atomic
def index(req):
    orders = Order.objects.order_by('-created_at')

    if req.method == 'POST':
        cart_id = req.POST.get('cart_id')
        if not cart_id:
            return redirect('carts:index')

        cart = get_object_or_404(Cart, id=cart_id)
        form = OrderForm(req.POST, mode='create')

        if form.is_valid():
            order = form.save(commit=False)
            order.store = cart.store
            order.member = cart.member
            order.save()

            # 建立訂單項目
            for cart_item in cart.items.all():
                # 檢查庫存
                if cart_item.product.quantity < cart_item.quantity:
                    form.add_error(
                        None, f'{cart_item.product.name} 庫存不足，請重新選擇數量'
                    )
                    return render(
                        req,
                        'orders/new.html',
                        {
                            'form': form,
                            'cart': cart,
                            'cart_items': cart.items.all(),
                        },
                    )

                # 建立訂單項目
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.price,
                )

                # 更新庫存
                cart_item.product.quantity -= cart_item.quantity
                cart_item.product.save()

            # 刪除購物車
            cart.delete()

            return redirect('orders:index')

        return render(
            req,
            'orders/new.html',
            {
                'form': form,
                'cart': cart,
                'cart_items': cart.items.all(),
            },
        )

    return render(req, 'orders/index.html', {'orders': orders})


def new(req):
    cart_id = req.GET.get('cart_id')
    if not cart_id:
        return redirect('carts:index')

    cart = get_object_or_404(Cart, id=cart_id)
    cart_items = cart.items.all()

    if not cart_items.exists():
        return redirect('carts:index')

    form = OrderForm(
        mode='create',
        initial={
            'store': cart.store,
            'note': cart.note,
        },
    )

    return render(
        req,
        'orders/new.html',
        {
            'form': form,
            'cart': cart,
            'cart_items': cart_items,
        },
    )


def show(req, id):
    order = get_object_or_404(Order, id=id)
    if req.method == 'POST':
        form = OrderForm(req.POST, instance=order, mode='update')

        if form.is_valid():
            form.save()
            return redirect('orders:show', id=order.id)
        else:
            return render(req, 'orders/edit.html', {'form': form, 'order': order})

    return render(req, 'orders/show.html', {'order': order})


def edit(req, id):
    order = get_object_or_404(Order, pk=id)
    form = OrderForm(instance=order, mode='update')
    return render(req, 'orders/edit.html', {'form': form, 'order': order})


def delete(req, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('orders:index')


def cancel(request, id):
    """取消訂單"""
    service = OrderService(id)
    if service.cancel_order():
        messages.success(request, '訂單已取消')
    else:
        messages.error(request, '此訂單無法取消')
    return redirect('orders:show', id=id)


def prepare(request, id):
    """開始準備訂單"""
    service = OrderService(id)
    if service.prepare_order():
        messages.success(request, '訂單開始準備中')
    else:
        messages.error(request, '此訂單無法開始準備')
    return redirect('orders:show', id=id)


def mark_ready(request, id):
    """標記訂單準備完成"""
    service = OrderService(id)
    if service.mark_order_ready():
        messages.success(request, '訂單已準備完成')
    else:
        messages.error(request, '此訂單無法標記為準備完成')
    return redirect('orders:show', id=id)


def complete(request, id):
    """完成訂單（顧客取餐）"""
    service = OrderService(id)
    if service.complete_order():
        messages.success(request, '訂單已完成')
    else:
        messages.error(request, '此訂單無法標記為完成')
    return redirect('orders:show', id=id)
