from django.db.models import Q
from django.shortcuts import render

from products.models import Product

# Create your views here.
# views.py
from stores.models import Store


def index(request):
    query = request.GET.get('q', '').strip()
    stores = products = []

    if query:
        stores = Store.objects.filter(name__icontains=query)
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(calories__icontains=query)
        )

    context = {
        'query': query,
        'stores': stores,
        'products': products,
    }
    return render(request, 'search/index.html', context)
