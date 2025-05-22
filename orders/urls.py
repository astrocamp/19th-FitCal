from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('<uuid:id>/', views.show, name='show'),
    # 新增狀態變更路由
    path('<uuid:id>/cancel/', views.cancel, name='cancel'),
    path('<uuid:id>/prepare/', views.prepare, name='prepare'),
    path('<uuid:id>/mark-ready/', views.mark_ready, name='mark_ready'),
    path('<uuid:id>/complete/', views.complete, name='complete'),
    # sites
    path('ordering_step1', views.ordering_step1, name='ordering_step1'),
]
