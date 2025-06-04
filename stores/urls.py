from django.urls import path

from . import views

app_name = 'stores'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('create/', views.create_store, name='create_store'),
    path('<uuid:id>/', views.show, name='show'),
    path('<uuid:id>/edit/', views.edit, name='edit'),
    path('<uuid:id>/delete/', views.delete, name='delete'),
    path('<uuid:store_id>/rate/', views.rate_store, name='rate_store'),
    path(
        'store_management/',
        views.store_management,
        name='store_management',
    ),
    path('<uuid:id>/orders/', views.order_list, name='order_list'),
    path(
        '<uuid:store_id>/category/new/',
        views.new_category,
        name='new_category',
    ),
    path(
        'category/<int:category_id>/',
        views.show_category,
        name='show_category',
    ),
    path(
        '<uuid:store_id>/category/create/',
        views.category_create,
        name='category_create',
    ),
    path(
        'category/<int:category_id>/edit/',
        views.category_edit,
        name='category_edit',
    ),
    path(
        'category/<int:category_id>/delete/',
        views.category_delete,
        name='category_delete',
    ),
    path('<uuid:store_id>/management/', views.management, name='management'),
    path(
        '<uuid:store_id>/<int:category_id>/products',
        views.category_products,
        name='category_products',
    ),
]
