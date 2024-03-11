from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages,auth
import re
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
# Create your views here.

@never_cache
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('f_name')
        last_name  = request.POST.get('l_name')
        username   = request.POST.get('username')
        email      = request.POST.get('email')
        password1  = request.POST.get('pass1')
        password2  = request.POST.get('pass2')

        if username.strip() == '':
            messages.error(request, 'The username is not valid')
            return redirect('register')
        elif password1 != password2:
            messages.error(request, 'The password does not match')
            return redirect('register')
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" , email):
            messages.error(request, 'Please enter a valid email address')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered')
            return redirect('register')

        elif User.objects.filter(username = username).exists():
            messages.error(request, 'The username is already taken')
            return redirect('register')

        user = User.objects.create_user(username=username, first_name = first_name, last_name = last_name, email=email, password=password1)
        user.save()
        messages.success(request, f'Welcome Mr.{first_name}')
        return redirect('login')

        
    return render(request, 'register.html')

def log_in(request):
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')

        if email != User.email:
            messages.error('Email does not match')
        elif password != User.password:
            messages.error('Password is incorrect')

        existing_user = auth.authenticate(email = email, password = password)
        if existing_user is not None:
            login(request,existing_user)
            return redirect('login')
        else:
            messages.error('email or password is not correct')
            return redirect('login')


    return render(request, 'log.html')

def index(request):
    return render(request, 'index.html')