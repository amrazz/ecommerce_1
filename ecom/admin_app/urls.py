from django.urls import path
from . import  views


# Admin_app urls

urlpatterns = [
    path('login/', views.access, name = 'admin'),
    path('dashboard/', views.dashboard, name ='dashboard'),
    
]
