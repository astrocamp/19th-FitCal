from django.urls import path

from . import views

app_name = 'stores'


urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('<uuid:pk>/', views.show, name='show'),  # 使用 uuid:pk
    path('<uuid:pk>/edit/', views.edit, name='edit'),
    path('<uuid:pk>/delete/', views.delete, name='delete'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('login/', views.create_session, name='login'),
    path('logout/', views.delete_session, name='logout'),
]
