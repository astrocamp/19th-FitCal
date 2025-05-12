from django.urls import path

from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('add/', views.add, name='add'),
    path('<uuid:id>', views.show, name='show'),
    path('<uuid:id>/edit', views.edit, name='edit'),
    path('<uuid:id>/delete_cart', views.delete_cart, name='delete_cart'),
    path('<uuid:id>/delete_item', views.delete_item, name='delete_item'),
]
