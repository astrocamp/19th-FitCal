from django.urls import path

from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.index, name='index'),
    path('search_addr/', views.search_addr, name='search_addr'),
    path('search_store/', views.search_store, name='search_store'),
]
