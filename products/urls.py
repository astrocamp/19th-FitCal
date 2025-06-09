from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/<int:category_id>/', views.new, name='new'),
    path('<uuid:id>', views.show, name='show'),
    path('<int:category_id>/create/', views.create, name='create'),
    path('<uuid:id>/edit/', views.edit, name='edit'),
    path('<uuid:id>/update/', views.update, name='update'),
    path('<uuid:id>/delete/', views.delete, name='delete'),
    path(
        'collections/<uuid:id>/',
        views.collections,
        name='collections',
    ),
    path(
        'estimate_calories/',
        views.estimate_calories_from_image,
        name='estimate_calories',
    ),
    path('api/product_sort/', views.api_product_sort, name='api_product_sort'),
]
