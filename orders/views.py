from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .forms import OrderForm
from .models import Order, OrderItem


def index(req):
    orders = Order.objects.order_by('-created_at')
    return render(req, 'orders/index.html', {'orders': orders})


def new(req):
    form = OrderForm(mode='create')

    # 測試用，之後會用從 cart_item 取得商品資訊
    product = Product.objects.order_by('?').first()

    return render(
        req,
        'orders/new.html',
        {
            'form': form,
            'product': product,
        },
    )


# 若出現錯誤，自動回滾，使用 transaction.atomic()
@transaction.atomic
@require_POST
def create(req):
    form = OrderForm(req.POST)
    if form.is_valid():
        order = form.save(commit=False)  # 不立即儲存到資料庫

        # order.member = req.user.member
        order.save()

        # 從表單取得 product_id，並從資料庫取得對應 product
        product_id = req.POST.get('product_id')
        quantity = int(req.POST.get('quantity'))

        # 防止多用戶同時下單造成庫存負值，使用 select_for_update()
        product = Product.objects.select_for_update().get(id=product_id)

        if product.quantity < quantity:
            raise ValidationError('庫存不足，請重新選擇數量')

        # 處理 OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
        )

        # 再次儲存 Order，更新總金額
        form.save(commit=True)

        product.quantity -= quantity
        product.save()

        return redirect('orders:success')
    else:
        print(form.errors)

    return render(
        req,
        'orders/new.html',
        {
            'form': form,
        },
    )


def success(req):
    return render(req, 'orders/success.html')


def show(req, id):
    order = get_object_or_404(Order, id=id)
    return render(req, 'orders/show.html', {'order': order})


def edit(req, id):
    order = get_object_or_404(Order, pk=id)
    form = OrderForm(instance=order, mode='update')
    return render(req, 'orders/edit.html', {'form': form, 'order': order})


def update(req, id):
    order = get_object_or_404(Order, id=id)
    form = OrderForm(req.POST, instance=order, mode='update')

    if form.is_valid():
        form.save()
        return redirect('orders:show', id=order.id)
    else:
        return render(req, 'orders/edit.html', {'form': form, 'order': order})


def delete(req, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('orders:index')
