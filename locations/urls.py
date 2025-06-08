from django.urls import path

from . import views

app_name = 'locations'

urlpatterns = [
    path('api/store_distance/', views.store_distance, name='store_distance'),
]
