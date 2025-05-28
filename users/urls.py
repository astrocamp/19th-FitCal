from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('create_user/', views.create_user, name='create_user'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('create_session/', views.create_session, name='create_session'),
    path('delete_session/', views.delete_session, name='delete_session'),
    path('sign_up/store/', views.sign_up_store, name='sign_up_store'),
    path('create_user/store/', views.create_user_store, name='create_user_store'),
    path('sign_in/store/', views.sign_in_store, name='sign_in_store'),
    path(
        'create_session/store/', views.create_session_store, name='create_session_store'
    ),
]
