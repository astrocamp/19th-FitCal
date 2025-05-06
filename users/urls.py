from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("sign_up/", views.sign_up, name="sign_up"), 
    path("create_user/", views.create_user, name="create_user"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("create_session/", views.create_session, name="create_session"),
    path("delete_session/", views.delete_session, name="delete_session"),
]