from django.contrib import admin
from django.urls import include, path

app_name = 'fitcal'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('members/', include('members.urls', namespace='members')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('stores/', include('stores.urls', namespace='stores')),
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('allauth.urls')),
    path('carts/', include('carts.urls', namespace='carts')),
    path('search/', include('search.urls', namespace='search')),
    path('payment/', include('payment.urls', namespace='payment')),
]
