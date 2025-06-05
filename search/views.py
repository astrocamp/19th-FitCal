from collections import defaultdict

from django.db.models import Avg
from django.shortcuts import render

from products.models import Product
from stores.models import Rating, Store

# Create your views here.


def index(request):
    query = request.GET.get('q', '').strip()
    max_calories = request.GET.get('max_calories', '').strip()

    stores = Store.objects.all()
    products = Product.objects.select_related('store').order_by('store__name', 'name')

    if query:
        stores = stores.filter(name__icontains=query)
        products = products.filter(name__icontains=query)

    if max_calories.isdigit() and int(max_calories) > 0:
        products = products.filter(calories__lte=int(max_calories))

    grouped_by_store = defaultdict(list)
    for product in products:
        grouped_by_store[product.store].append(product)

    for store in stores:
        store.avg_rating = (
            Rating.objects.filter(store=store).aggregate(avg=Avg('score'))['avg'] or 0
        )
    context = {
        'query': query,
        'max_calories': max_calories,
        'stores': stores,
        'products': products,
        'grouped_products': grouped_by_store.items(),
    }
    return render(request, 'search/index.html', context)
