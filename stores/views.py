from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from common.decorator import store_required
from orders.models import Order

from .forms import RatingForm, StoreForm
from .models import Rating, Store


def new(req):
    form = StoreForm()
    return render(req, 'stores/new.html', {'form': form})


@login_required
@transaction.atomic
def create_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect('stores:show', store.id)
    form = StoreForm()
    return render(request, 'stores/new.html', {'form': form})


@login_required
def index(request):
    user = request.user

    if user.is_store:
        try:
            store = user.store
            store.avg_rating = (
                Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg']
                or 0
            )
            stats = store_management(request)
            return render(
                request,
                'stores/store_management.html',
                {'store': store, 'stats': stats},
            )
        except Store.DoesNotExist:
            return redirect('stores:new')

    # 會員邏輯
    stores = Store.objects.all()
    member = getattr(user, 'member', None) if user.is_member else None

    for store in stores:
        store.avg_rating = (
            Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg'] or 0
        )
        if member:
            store.member_rating = Rating.objects.filter(
                store=store, member=member
            ).first()

    context = {
        'stores': stores,
        'member': member,
        'form': RatingForm() if member else None,
    }
    return render(request, 'stores/index.html', context)


def show(req, id):
    store = get_object_or_404(Store, pk=id)
    products = store.products.all()
    store.avg_rating = (
        Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg'] or 0
    )
    if req.method == 'POST':
        form = StoreForm(req.POST, req.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', id=store.id)
        return render(
            req,
            'stores/edit.html',
            {'store': store, 'form': form},
        )
    return render(
        req,
        'stores/show.html',
        {'store': store, 'products': products},
    )


@store_required
def edit(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    if req.method == 'POST':
        form = StoreForm(req.POST, req.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', store_id=store.id)
    form = StoreForm(instance=store)
    return render(
        req,
        'stores/edit.html',
        {
            'form': form,
            'store': store,
        },
    )


@store_required
def delete(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    store.delete()
    return redirect('users:sign_up')


@require_POST
@login_required
def rate_store(request, store_id):
    member = getattr(request.user, 'member', None)
    if not member:
        messages.error(request, '請先填寫會員資料')
        return redirect('members:new')

    store = get_object_or_404(Store, id=store_id)
    rating = Rating.objects.filter(store=store, member=member).first()
    form = RatingForm(request.POST, instance=rating)

    if form.is_valid():
        new_rating = form.save(commit=False)
        new_rating.member = member
        new_rating.store = store
        new_rating.save()

        # 如果是 HTMX 請求：回傳一個更新後的按鈕區塊
        if request.headers.get('Hx-Request') == 'true':
            html = render_to_string(
                'stores/_rating_button.html',
                {
                    'store': store,
                    'member_rating': new_rating,
                },
                request=request,
            )
            return HttpResponse(html)

    # 傳統表單提交：重新導向回 index
    return redirect('stores:index')


@login_required
def store_management(request):
    """商家管理頁面"""
    store = request.user.store

    order_queryset = store.orders.all()  # 透過 related_name='orders'

    stats = order_queryset.aggregate(
        total_amount=Sum('total_price'),
        average_order_price=Avg('total_price'),
        order_count=Count('id'),
    )

    # 預設為 0 或顯示友善數字（處理 None）
    stats = {
        'total_amount': stats['total_amount'] or 0,
        'average_order_price': round(stats['average_order_price'] or 0),
        'order_count': stats['order_count'] or 0,
    }

    return stats


@store_required
def order_list(request, id):
    store = get_object_or_404(Store, id=id)

    tab = request.GET.get('tab', 'today')
    today = date.today()

    if tab == 'reservation':
        orders = Order.objects.filter(
            store=store, pickup_time__date__gt=today
        ).order_by('-created_at')
    elif tab == 'history':
        orders = Order.objects.filter(
            store=store, pickup_time__date__lt=today
        ).order_by('-created_at')
    else:  # today
        orders = Order.objects.filter(store=store, pickup_time__date=today).order_by(
            '-created_at'
        )

    if request.headers.get('HX-Request') == 'true':
        return render(
            request,
            'shared/orders/_order_list.html',
            {
                'orders': orders,
                'tab': tab,
            },
        )

    return render(request, 'stores/orders.html', {'orders': orders, 'tab': tab})
