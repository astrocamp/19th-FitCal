from django.urls import path

from . import views

app_name = 'members'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('create/', views.create_member, name='create_member'),
    path('<uuid:id>/', views.show, name='show'),
    path('<uuid:id>/edit/', views.edit, name='edit'),
    path('<uuid:id>/delete/', views.delete, name='delete'),
    path('favorite/<uuid:store_id>', views.favorite, name='favorite'),
    path('favorite/', views.favorite_list, name='favorite_list'),
    path('store_list/', views.store_list, name='store_list'),
    path('collections/', views.collections, name='collections'),
]
