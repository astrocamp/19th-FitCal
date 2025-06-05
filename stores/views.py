import json
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.views.decorators.http import require_POST

from common.decorator import store_required
from orders.models import Order
from products.models import Product

from .forms import RatingForm, StoreForm
from .models import Category, Rating, Store


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
    categories = store.categories.all()
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
        {'store': store, 'products': products, 'categories': categories},
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


def new_category(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    return render(
        request,
        'shared/business/stores/new_category.html',
        {'store': store},
    )


def show_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return render(
        request,
        'shared/business/stores/show_category.html',
        {'category': category},
    )


@store_required
@require_POST
def category_create(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    name = request.POST.get('name')
    if not name:
        messages.error(request, '類別名稱不能為空')
        return render(request, 'shared/messages.html')
    if store.categories.filter(name=name).exists():
        messages.error(request, '此類別已存在')
        return render(request, 'shared/messages.html')

    store.categories.create(name=name)
    messages.success(request, '類別創建成功')
    response = HttpResponse()
    response['HX-Redirect'] = reverse('stores:management', args=[store_id])
    return response


@store_required
@require_POST
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    new_name = request.POST.get('name')
    if new_name:
        if category.store.categories.filter(name=new_name).exists():
            messages.error(request, '此類別名稱已存在')
            return render(request, 'shared/messages.html')
        elif new_name != category.name:
            category.name = new_name
            category.save()
            messages.success(request, '類別名稱已更新')
    else:
        messages.error(request, '請輸入有效的類別名稱')
    response = HttpResponse()
    response['HX-Redirect'] = reverse('stores:management', args=[category.store.id])
    return response


@store_required
@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    store = category.store

    category.delete()
    messages.success(request, '類別已刪除')
    return redirect('stores:management', store.id)


@store_required
def management(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    categories = store.categories.all()
    products = store.products.all()
    return render(
        request,
        'stores/business/product_management.html',
        {'store': store, 'categories': categories, 'products': products},
    )


@store_required
def category_products(request, store_id, category_id):
    store = get_object_or_404(Store, id=store_id)
    category = get_object_or_404(Category, id=category_id, store=store)
    products = category.products.all()
    return render(
        request,
        'stores/business/product_list.html',
        {'store': store, 'category': category, 'products': products},
    )


def businesses_dashboard(request, store_id):
    store = request.user.store
    orders = Order.objects.filter(store=store, order_status='COMPLETED')
    ratings = Rating.objects.filter(store=store)
    today = now().date()

    # 熱銷商品排行（Top 5）
    top_products = (
        orders.values('orderitem__product_name')
        .annotate(
            name=F('orderitem__product_name'),
            quantity=Sum('orderitem__quantity'),
            sales=Sum('orderitem__subtotal'),
        )
        .order_by('-quantity')[:5]
    )

    # 銷售明細（總量）+ 收藏數
    product_sales = list(
        orders.values('orderitem__product_name', 'orderitem__product_id')
        .annotate(
            name=F('orderitem__product_name'),
            total_quantity=Sum('orderitem__quantity'),
            total_revenue=Sum('orderitem__subtotal'),
        )
        .order_by('orderitem__product_name')
    )

    for item in product_sales:
        product = Product.objects.filter(id=item['orderitem__product_id']).first()
        item['collection_count'] = product.collections.count() if product else 0

    # 加入「今日銷售數量 / 營收」
    today_orders = orders.filter(created_at__date=today)
    today_product_sales = today_orders.values(
        'orderitem__product_id', 'orderitem__product_name'
    ).annotate(
        today_quantity=Sum('orderitem__quantity'),
        today_revenue=Sum('orderitem__subtotal'),
    )
    today_sales_map = {
        p['orderitem__product_id']: {
            'today_quantity': p['today_quantity'],
            'today_revenue': p['today_revenue'],
        }
        for p in today_product_sales
    }

    for item in product_sales:
        pid = item['orderitem__product_id']
        item['today_quantity'] = today_sales_map.get(pid, {}).get('today_quantity', 0)
        item['today_revenue'] = today_sales_map.get(pid, {}).get('today_revenue', 0)

    # 評分平均與總表
    avg_rating = round(ratings.aggregate(avg=Avg('score'))['avg'] or 0, 1)
    rating_count = ratings.count()
    store_ratings = ratings.values(
        member_name=F('member__name'),
        rating_score=F('score'),
        rating_time=F('created_at'),
    ).order_by('-created_at')

    # 圖表資料（近30日）
    start_date = today - timedelta(days=29)
    daily_orders = (
        orders.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total_sales=Sum('total_price'), order_count=Count('id'))
        .order_by('day')
    )
    daily_ratings = (
        ratings.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(avg_rating_score=Avg('score'))
        .order_by('day')
    )
    rating_dict = {
        r['day']: round(r['avg_rating_score'] or 0, 2) for r in daily_ratings
    }

    # ⬇️ 判斷今天是否有資料
    use_today_data = today_orders.exists()
    pie_orders = today_orders if use_today_data else orders

    # 圓餅圖：商品營收佔比
    pie_product_revenue = (
        pie_orders.values('orderitem__product_name')
        .annotate(name=F('orderitem__product_name'), revenue=Sum('orderitem__subtotal'))
        .order_by('-revenue')
    )
    chart_pie_data = [float(p['revenue']) for p in pie_product_revenue]
    total_revenue = sum(Decimal(p['revenue']) for p in pie_product_revenue) or 1
    chart_pie_labels = [
        f'{p["name"]} ({(Decimal(p["revenue"]) / total_revenue * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)}%)'
        for p in pie_product_revenue
    ]

    # 圓餅圖：商品數量佔比
    pie_product_orders = (
        pie_orders.values('orderitem__product_name')
        .annotate(name=F('orderitem__product_name'), count=Sum('orderitem__quantity'))
        .order_by('-count')
    )
    chart_order_data = [int(p['count']) for p in pie_product_orders]
    total_count = sum(chart_order_data) or 1
    chart_order_labels = [
        f'{p["name"]} ({round(p["count"] / total_count * 100, 1)}%)'
        for p in pie_product_orders
    ]

    # 折線圖資料
    chart_labels = [d['day'].strftime('%Y-%m-%d') for d in daily_orders]
    chart_sales = [float(d['total_sales'] or 0) for d in daily_orders]
    chart_orders = [d['order_count'] for d in daily_orders]
    chart_avg_ratings = [rating_dict.get(d['day'], 0) for d in daily_orders]
    chart_top_names = [p['name'] for p in top_products]
    chart_top_sales = [p['quantity'] for p in top_products]

    return render(
        request,
        'stores/businesses_dashboard.html',
        {
            'top_products': top_products,
            'avg_rating': avg_rating,
            'rating_count': rating_count,
            'store_ratings': store_ratings,
            'product_sales': product_sales,
            'chart_labels': json.dumps(chart_labels),
            'chart_labels_raw': chart_labels,
            'chart_sales': json.dumps(chart_sales),
            'chart_orders': json.dumps(chart_orders),
            'chart_avg_ratings': json.dumps(chart_avg_ratings),
            'chart_top_names': json.dumps(chart_top_names),
            'chart_top_sales': json.dumps(chart_top_sales),
            'today': today,
            'chart_pie_labels': json.dumps(chart_pie_labels),
            'chart_pie_data': json.dumps(chart_pie_data),
            'chart_order_labels': json.dumps(chart_order_labels),
            'chart_order_data': json.dumps(chart_order_data),
            'is_today_data': use_today_data,
        },
    )
