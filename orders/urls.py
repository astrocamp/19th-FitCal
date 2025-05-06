from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('create/', views.create, name='create'),
    path('success/', views.success, name='success'),
    path('<uuid:id>/', views.show, name='show'),
    path('<uuid:id>/edit/', views.edit, name='edit'),
    path('<uuid:id>/update/', views.update, name='update'),
    path('<uuid:id>/delete/', views.delete, name='delete'),
]
