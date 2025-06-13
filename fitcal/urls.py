from django.contrib import admin
from django.urls import include, path

from products import views as products_views

app_name = 'fitcal'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('users.urls', namespace='users')),
    path('members/', include('members.urls', namespace='members')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('stores/', include('stores.urls', namespace='stores')),
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('allauth.urls')),
    path('carts/', include('carts.urls', namespace='carts')),
    path('search/', include('search.urls', namespace='search')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path(
        'api/estimate-calories/',
        products_views.estimate_calories_from_image,
        name='estimate_calories_api',
    ),
    path('', include('pages.urls')),
]
