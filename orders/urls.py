from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('success/', views.success, name='success'),
]
