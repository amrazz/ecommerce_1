from django.urls import path
from . import  views

#ecom_app urls

urlpatterns = [
    path('', views.index, name = 'index')
]
