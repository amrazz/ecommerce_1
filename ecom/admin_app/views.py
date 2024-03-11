from django.shortcuts import render,redirect
from django.contrib.auth.models import User

# Create your views here.

def access(request):
    return render(request, 'login.html')


def dashboard(request):
    return render(request, 'dashboard.html')