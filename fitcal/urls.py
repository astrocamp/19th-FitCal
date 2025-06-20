import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language

from products import views as products_views
from search import views as search_views

app_name = 'fitcal'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', include('users.urls', namespace='users')),
    path('members/', include('members.urls', namespace='members')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('stores/', include('stores.urls', namespace='stores')),
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('allauth.urls')),
    path('carts/', include('carts.urls', namespace='carts')),
    path('search/', search_views.index, name='search'),
    path('payment/', include('payment.urls', namespace='payment')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path(
        'api/estimate-calories/',
        products_views.estimate_calories_from_image,
        name='estimate_calories_api',
    ),
    path('', include('pages.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
]
