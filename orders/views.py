from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderForm
from .models import Order, OrderItem


# Create your views here.
def index(req):
    orders = Order.objects.order_by('-created_at')
    return render(req, 'orders/index.html', {'orders': orders})


def create(req):
    if req.method == 'POST':
        form = OrderForm(req.POST)
        if form.is_valid():
            order = form.save(commit=False)  # 不立即儲存到資料庫
            order.save()
        else:
            print(order.errors)

        # 處理 OrderItem
        OrderItem.objects.create(
            order=order,
            quantity=req.POST.get('quantity', 1),  # 預設數量為1
            unit_price=req.POST.get('unit_price', 0),  # 預設單價為0
        )

        # 再次儲存 Order，更新總金額
        form.save(commit=True)

        return redirect('orders:success')  # 重定向到成功頁面

    form = OrderForm(mode='create')  # 預設模式為建立訂單

    return render(
        req,
        'orders/create.html',
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

    return redirect('orders:show', id=order.id)


def delete(req, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('orders:index')
