from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls', namespace='pages')),
    path('users/', include('users.urls', namespace='users')),
    path('members/', include('members.urls', namespace='members')),
    path('orders/', include('orders.urls', namespace='orders')),
]
