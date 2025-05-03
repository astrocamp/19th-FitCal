from django.urls import path

from . import views

app_nmae = 'pages'
# app_name = 'pages'


urlpatterns = [
    path('', views.home, name='home'),
]
