from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_waf, name='test_waf'),
    path('check/', views.waf_check, name='waf_check'),
    path('dashboard/', views.dashboard, name='dashboard'),
]