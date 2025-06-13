import csv
import json
import re
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, F, Prefetch, Sum
from django.db.models.functions import TruncDate
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from common.decorator import store_required
from orders.enums import OrderStatus
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


def index(request):
    # Store owner logic
    if request.user.is_authenticated and request.user.is_store:
        return handle_store_owner(request)

    # Member and unauthenticated user logic
    return handle_public_view(request)


def handle_store_owner(request):
    """Handle store owner dashboard view"""
    try:
        store = request.user.store
        store.avg_rating = (
            Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg'] or 0
        )
        stats = store_management(request)
        return render(
            request,
            'stores/store_management.html',
            {'store': store, 'stats': stats},
        )
    except Store.DoesNotExist:
        return redirect('stores:new')


def handle_public_view(request):
    """Handle public view for members and unauthenticated users"""
    # 預先載入評分資訊以減少資料庫查詢
    stores = Store.objects.annotate(
        avg_rating=Avg(
            'rating__score'
        )  # Changed from 'ratings__score' to 'rating__score'
    ).all()

    # Get member if user is authenticated and is a member
    member = None
    if request.user.is_authenticated and request.user.is_member:
        member = getattr(request.user, 'member', None)

        # 只為已登入會員載入個人評分
        if member:
            member_ratings = Rating.objects.filter(member=member).values_list(
                'store_id', 'score'
            )
            member_ratings_dict = dict(member_ratings)

            # 將會員評分加入店家資訊
            for store in stores:
                store.member_rating = member_ratings_dict.get(store.id)

    context = {
        'stores': stores,
        'member': member,
        'form': RatingForm() if member else None,
    }
    return render(request, 'stores/index.html', context)


def show(req, id):
    store = get_object_or_404(Store, pk=id)

    # 先查出所有商品，避免 N+1
    all_products = store.products.select_related('category').all()

    # 預先取得各類別的商品，排序好
    categories_qs = (
        store.categories.all()
        .order_by('sort_order')
        .prefetch_related(
            Prefetch(
                'products',
                queryset=all_products.order_by('sort_order'),
                to_attr='sorted_products',  # 自訂屬性名，避免覆蓋原來的 `products`
            )
        )
    )

    # 組裝資料
    categories = [
        {'name': category.name, 'products': category.sorted_products}
        for category in categories_qs
    ]

    store.avg_rating = (
        Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg'] or 0
    )

    if req.method == 'POST':
        form = StoreForm(req.POST, req.FILES, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:show', id=store.id)
        return render(req, 'stores/edit.html', {'store': store, 'form': form})

    if hasattr(req.user, 'member'):
        cart = store.carts.filter(member=req.user.member).first()
        if cart:
            cart_total_price = cart.total_price
            cart_total_calories = cart.total_calories
            cart_total_quantity = cart.total_quantity
        else:
            cart_total_price = 0
            cart_total_calories = 0
            cart_total_quantity = 0
    else:
        cart = None
        cart_total_price = 0
        cart_total_calories = 0
        cart_total_quantity = 0
    return render(
        req,
        'stores/show.html',
        {
            'store': store,
            'categories': categories,
            'cart': cart,
            'cart_total_price': cart_total_price,
            'cart_total_quantity': cart_total_quantity,
            'cart_total_calories': cart_total_calories,
        },
    )


@store_required
def store_settings(request):
    """
    商家基本設定編輯頁面
    顯示並處理商家自己的資料更新
    """
    store = request.user.store

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, '商家資訊已成功更新！')
            return redirect('stores:store_settings')
        else:
            messages.error(request, '請檢查您的輸入，有錯誤發生！')
    else:
        form = StoreForm(instance=store)

    return render(
        request,
        'stores/store_settings.html',
        {
            'form': form,
            'store': store,
        },
    )


@store_required
def delete(req, id):
    store = get_object_or_404(Store, pk=id, user=req.user)
    store.delete()
    return redirect('users:index')


@require_POST
@login_required
def rate_store(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, member=request.user.member)

        if order.order_status != 'COMPLETED':
            return HttpResponseBadRequest('訂單尚未完成，無法評分')

        if hasattr(order, 'rating'):
            return HttpResponseBadRequest('此訂單已評分')

        try:
            score = int(request.POST.get('score', 0))
        except (TypeError, ValueError):
            return HttpResponseBadRequest('請提供有效的分數')

        if score < 1 or score > 5:
            return HttpResponseBadRequest('分數必須在 1 到 5 分之間')

        Rating.objects.create(
            member=request.user.member,
            store=order.store,
            order=order,
            score=score,
        )

        return HttpResponse(f"""
            <div class="text-sm text-gray-600">
                ✅ 已評分：<strong>{score} 分</strong>
            </div>
        """)

    except Exception as e:
        return JsonResponse(
            {'error': '伺服器發生錯誤，請稍後再試', 'debug': str(e)}, status=500
        )


@login_required
def store_management(request):
    """商家管理頁面"""
    store = request.user.store

    today = timezone.now().date()  # 取得今天日期（含時區），使用 timezone.now()

    # 篩選今天的「已完成」訂單
    order_queryset = store.orders.filter(
        created_at__date=today,
        order_status='COMPLETED',
    )
    # Order.objects.values_list('order_status', flat=True).distinct() # 這行不需要

    stats = order_queryset.aggregate(
        total_amount=Sum('total_price'),
        average_order_price=Avg('total_price'),
        order_count=Count('id'),
    )

    # 預設為 0 或顯示友善數字（處理 None）
    stats = {
        'total_amount': stats['total_amount'] or 0,
        'average_order_price': round(stats['average_order_price'] or 0)
        if stats['average_order_price'] is not None
        else 0,  # 避免 round(None)
        'order_count': stats['order_count'] or 0,
    }

    return stats


@store_required
def order_list(request, id):
    # 確保從 URL 傳入的 id 獲取到 Store 物件
    store = get_object_or_404(Store, id=id)

    status = request.GET.get('status', '')
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

    # Apply status filter after tab filter
    if status and status != 'ALL':
        orders = orders.filter(order_status=status)

    # Pagination
    paginator = Paginator(orders, 10)  # 每頁10筆
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'tab': tab,
        'current_status': status,
        'status_choices': OrderStatus.choices,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'shared/orders/_order_list.html', context)

    return render(request, 'stores/orders.html', context)


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
    # 檢查類別名稱是否已經存在於該商店下
    if store.categories.filter(name=name).exists():
        messages.error(request, '此類別已存在')
        return render(request, 'shared/messages.html')

    store.categories.create(name=name)
    messages.success(request, '類別創建成功')
    response = HttpResponse()
    response['HX-Redirect'] = reverse('stores:management')
    return response


@store_required
@require_POST
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    new_name = request.POST.get('name')
    if new_name:
        # 檢查新的類別名稱是否與同商店下其他類別重複
        if (
            category.store.categories.filter(name=new_name)
            .exclude(id=category.id)
            .exists()
        ):
            messages.error(request, '此類別名稱已存在')
            return render(request, 'shared/messages.html')
        elif new_name != category.name:
            category.name = new_name
            category.save()
            messages.success(request, '類別名稱已更新')
    else:
        messages.error(request, '請輸入有效的類別名稱')
    response = HttpResponse()
    response['HX-Redirect'] = reverse('stores:management')
    return response


@store_required
@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # 確保只有商店自己的類別可以被刪除
    if category.store != request.user.store:
        messages.error(request, '您無權刪除此類別。')
        return HttpResponseBadRequest('Unauthorized access.')

    category.delete()
    messages.success(request, '類別已刪除')
    return redirect('stores:management')


@store_required
def management(request):
    store = request.user.store
    store_qs = Store.objects.prefetch_related(  # 對 Store 的 related objects 預抓
        Prefetch(
            'categories',  # related_name='categories' 的欄位（Category FK Store）
            queryset=Category.objects.prefetch_related(
                'products'
            ),  # 對每個 Category 預抓 products
        ),
    ).get(id=store.id)
    categories = store_qs.categories.order_by('sort_order')
    selected_category = categories.first() if categories.exists() else None
    products = (
        selected_category.products.filter(store=store).order_by(
            'sort_order', 'created_at'
        )
        if selected_category
        else []
    )
    if request.resolver_match.url_name == 'management':
        return render(
            request,
            'stores/business/product_management.html',
            {
                'store': store,
                'selected_category': selected_category,
                'categories': categories,
                'products': products,
            },
        )
    elif request.resolver_match.url_name == 'product_manage_panel':
        return render(
            request,
            'stores/business/product_manage_panel.html',
            {
                'store': store,
                'selected_category': selected_category,
                'categories': categories,
                'products': products,
            },
        )
    elif request.resolver_match.url_name == 'menu_sort_panel':
        return render(
            request,
            'stores/business/menu_sort_panel.html',
            {
                'store': store,
                'selected_category': selected_category,
                'categories': categories,
                'products': products,
            },
        )


@store_required
def category_products(request, store_id, category_id=None):
    store = get_object_or_404(Store, id=store_id)
    # 空類別商品的篩選
    uncategorized_products = Product.objects.filter(store=store, category__isnull=True)
    # 用 prefetch_related 搭配 Prefetch 並指定 to_attr 給 store 一個屬性存這筆資料
    store = Store.objects.prefetch_related(
        Prefetch('products', queryset=uncategorized_products, to_attr='uncat_products')
    ).get(id=store.id)
    if category_id:
        category = get_object_or_404(Category, id=category_id, store=store)
        products = store.products.filter(category=category).order_by(
            'sort_order', 'created_at'
        )
        if request.resolver_match.url_name == 'category_products':
            return render(
                request,
                'stores/business/product_manage_list.html',
                {'category': category, 'products': products},
            )
        else:
            return render(
                request,
                'stores/business/product_sort_list.html',
                {'category': category, 'products': products},
            )
    else:
        products = store.uncat_products
        return render(
            request,
            'stores/business/product_manage_list.html',
            {'category': '', 'products': products},
        )


def businesses_dashboard(request, store_id):
    store = request.user.store
    # 檢查 store_id 是否與當前登入用戶的 store_id 匹配
    if str(store.id) != str(store_id):
        return HttpResponseBadRequest('Unauthorized access to dashboard.')

    orders = Order.objects.filter(store=store, order_status='COMPLETED')
    ratings = Rating.objects.filter(store=store)
    today = timezone.now().date()  # 使用 timezone.now()

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


# 報表輸出
class Echo:
    def write(self, value):
        return value


@store_required
def export_sales_csv(request):
    """匯出銷售報表為 CSV 檔案"""
    store = Store.objects.get(user=request.user)

    queryset = (
        Order.objects.select_related('store')
        .prefetch_related('orderitem_set', 'orderitem_set__product')
        .filter(store=store)
    )

    # 將資料轉為迭代器，每列是一個 list
    def row_generator():
        header = [
            '訂單編號',
            '商品名稱',
            '購買數量',
            '商品單價',
            '小計',
            '商家名稱',
            '建立時間',
        ]
        yield header

        for order in queryset:
            for item in order.orderitem_set.all():
                yield [
                    order.order_number,
                    item.product.name if item.product else '（無商品名稱）',
                    item.quantity,
                    item.unit_price,
                    item.quantity * item.unit_price,
                    store.name,
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ]

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    safe_store_name = re.sub(r'[^\w\-]', '_', store.name)

    return StreamingHttpResponse(
        (writer.writerow(row) for row in row_generator()),
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{safe_store_name}_sales_report.csv"'
        },
    )


@store_required
def api_category_sort(request):
    ids = request.POST.getlist('ids')
    store = request.user.store
    print('Received category ids:', ids)
    for index, cid in enumerate(ids):
        Category.objects.filter(id=cid, store=store).update(sort_order=index)
    messages.success(request, '分類排序已更新')
    return render(request, 'shared/messages.html')
