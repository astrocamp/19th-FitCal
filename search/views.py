from django.db.models import Q
from django.shortcuts import render

from products.models import Product
from stores.models import Store

# Create your views here.


def index(request):
    query = request.GET.get('q', '').strip()
    max_calories = request.GET.get('max_calories')
    stores = []
    products = Product.objects.all()

    if query:
        stores = Store.objects.filter(name__icontains=query)

        if query.isdigit():
            products = products.filter(
                Q(name__icontains=query) | Q(calories=int(query))
            )
        else:
            products = products.filter(name__icontains=query)

    if max_calories and max_calories.isdigit():
        products = products.filter(calories__lte=int(max_calories))

    context = {
        'query': query,
        'stores': stores,
        'products': products,
    }
    return render(request, 'search/index.html', context)
