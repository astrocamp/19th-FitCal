from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import condition

from carts.models import Cart

from .forms import OrderForm
from .models import Order, OrderItem, PendingOrder
from .services import OrderService


@transaction.atomic
def index(req):
    member = req.user.member
    orders = Order.objects.filter(member=req.user.member).order_by('-created_at')

    if req.method == 'POST':
        cart_id = req.POST.get('cart_id')
        if not cart_id:
            return redirect('carts:index')

        cart = get_object_or_404(Cart, id=cart_id)
        form = OrderForm(req.POST, mode='create')
        cart_items = cart.items.all()

        for cart_item in cart.items.all():
            # 檢查庫存
            if cart_item.product.quantity < cart_item.quantity:
                messages.error(
                    req, f'{cart_item.product.name} 庫存不足，請重新選擇數量'
                )
                return render(
                    req,
                    'carts/show.html',
                    {
                        'member': member,
                        'cart': cart,
                        'cart_item': cart_items,
                    },
                )

        if form.is_valid():
            order = form.save(commit=False)
            order.store = cart.store
            order.member = cart.member

            payment_method = form.cleaned_data['payment_method']

            # 如果是 LINE Pay，先不儲存訂單
            if payment_method == 'LINE_PAY':
                pending_order = PendingOrder.objects.create(
                    member_name=req.POST.get('ordering_member_name'),
                    member_phone=req.POST.get('ordering_member_phone_number'),
                    pickup_time=form.cleaned_data['pickup_time'],
                    note=form.cleaned_data.get('note', ''),
                )

                # 導向 linepay_request 並傳送 pending_order_id
                return redirect(
                    reverse('payment:linepay_request')
                    + f'?pending_order_id={pending_order.id}&cart_id={cart.id}'
                )

            member_name = req.POST.get('ordering_member_name')
            member_phone = req.POST.get('ordering_member_phone_number')

            if member_name:
                order.member_name = member_name
            else:
                order.member_name = cart.member.name
            if member_phone:
                order.member_phone = member_phone
            else:
                order.member_phone = cart.member.phone_number

            for cart_item in cart.items.all():
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

            # 計算總價
            total = (
                order.orderitem_set.aggregate(
                    total_price=Sum(F('unit_price') * F('quantity'))
                )['total_price']
                or 0
            )

            order.total_price = total
            order.save()

            # 刪除購物車
            cart.delete()
            messages.success(req, '訂單建立成功')
            return redirect('orders:show', id=order.id)

        return render(
            req,
            'orders/ordering_steps.html',
            {
                'form': form,
                'cart': cart,
                'cart_items': cart.items.all(),
            },
        )

    return render(req, 'orders/order_list.html', {'orders': orders})


def new(req):
    member = req.user.member
    cart_id = req.GET.get('cart_id')
    if not cart_id:
        return redirect('carts:index')

    cart = get_object_or_404(Cart, id=cart_id)
    cart_items = cart.items.all()

    for cart_item in cart.items.all():
        # 檢查庫存
        if cart_item.product.quantity < cart_item.quantity:
            messages.error(req, f'{cart_item.product.name} 庫存不足，請重新選擇數量')
            return render(
                req,
                'carts/show.html',
                {
                    'member': member,
                    'cart': cart,
                    'cart_item': cart_items,
                },
            )

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
        'orders/ordering_steps.html',
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


def cancel(request, id):
    """取消訂單"""
    service = OrderService(id)

    by_store = False
    if hasattr(request.user, 'store') and request.user.store:
        by_store = True

    success = service.cancel_order(by_store=by_store)
    order = get_object_or_404(Order, id=id)

    if success:
        messages.success(request, '訂單已取消')
    else:
        messages.error(request, '此訂單無法取消')

    return render(
        request, 'shared/orders/partial_order_status_response.html', {'order': order}
    )


def prepare(request, id):
    """開始準備訂單"""
    service = OrderService(id)

    success = service.prepare_order()
    order = get_object_or_404(Order, id=id)

    if success:
        messages.success(request, '訂單開始準備中')
    else:
        messages.error(request, '此訂單無法開始準備')

    return render(
        request, 'shared/orders/partial_order_status_response.html', {'order': order}
    )


def mark_ready(request, id):
    """標記訂單準備完成"""
    service = OrderService(id)

    success = service.mark_order_ready()
    order = get_object_or_404(Order, id=id)

    if success:
        messages.success(request, '訂單已準備完成')
    else:
        messages.error(request, '此訂單無法標記為準備完成')

    return render(
        request, 'shared/orders/partial_order_status_response.html', {'order': order}
    )


def complete(request, id):
    """完成訂單（顧客取餐）"""
    service = OrderService(id)

    success = service.complete_order()
    order = get_object_or_404(Order, id=id)

    if success:
        messages.success(request, '訂單已完成')
    else:
        messages.error(request, '此訂單無法標記為完成')

    return render(
        request, 'shared/orders/partial_order_status_response.html', {'order': order}
    )


# Last-Modified 判斷條件
def last_modified_func(request, id):
    order = get_object_or_404(Order, id=id)
    return order.updated_at


# 局部載入訂單狀態（適用於 HTMX polling）
@condition(last_modified_func=last_modified_func)
def partial_status(request, id):
    order = get_object_or_404(Order, id=id)

    response = render(
        request,
        'shared/orders/order_status_content.html',
        {
            'order': order,
        },
    )

    return response
