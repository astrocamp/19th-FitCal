from django.urls import path

from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:id>', views.show, name='show'),
    path('<uuid:id>/delete_cart', views.delete_cart, name='delete_cart'),
    path(
        'items/<uuid:product_id>/create/',
        views.create_cart_item,
        name='create_cart_item',
    ),
    path(
        'items/<uuid:item_id>/update/', views.update_cart_item, name='update_cart_item'
    ),
    path(
        'items/<uuid:item_id>/delete', views.delete_cart_item, name='delete_cart_item'
    ),
    path(
        'update_preview/<uuid:product_id>/', views.update_preview, name='update_preview'
    ),
    path(
        '<uuid:id>/delete_item_from_ordering',
        views.delete_item_from_ordering,
        name='delete_item_from_ordering',
    ),
]
