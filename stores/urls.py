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
]
