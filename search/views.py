from django.db.models import Q
from django.shortcuts import render

from products.models import Product

# Create your views here.
# views.py
from stores.models import Store

# def index(request):
#     query = request.GET.get('q', '').strip()
#     max_calories = request.GET.get('max_calories')
#     stores = products = []

#     if query or max_calories:
#         stores = Store.objects.filter(name__icontains=query)
#         products = Product.objects.filter(
#             Q(name__icontains=query) | Q(calories__icontains=query)
#         )

#     context = {
#         'query': query,
#         'stores': stores,
#         'products': products,
#     }
#     return render(request, 'search/index.html', context)




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

    # 如果有設定 max_calories，再加一個條件篩選
    if max_calories and max_calories.isdigit():
        products = products.filter(calories__lte=int(max_calories))

    context = {
        'query': query,
        'stores': stores,
        'products': products,
    }
    return render(request, 'search/index.html', context)
