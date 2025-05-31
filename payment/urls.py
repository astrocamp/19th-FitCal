from django.urls import path

from . import views

app_name = 'payment'

urlpatterns = [
    path('linepay/request', views.linepay_request, name='linepay_request'),
    path('linepay/confirm', views.linepay_confirm, name='linepay_confirm'),
    # path('linepay/cancel', views.linepay_cancel, name='linepay_cancel'),
]
