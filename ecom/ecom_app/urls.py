from django.urls import path
from . import  views

#ecom_app urls

urlpatterns = [
    path('', views.index, name = 'index'),
    path('register/',views.register, name = 'register'),
    path('login/', views.log_in, name = 'login')
]
