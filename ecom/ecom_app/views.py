from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from ecom.settings import EMAIL_HOST_USER
from validate_email_address import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import random
import re

@never_cache
def register(request):
    try:
        if request.user.is_authenticated:
            return redirect('index')
        
        if request.method == 'POST':
            first_name = request.POST.get('f_name')
            last_name = request.POST.get('l_name')
            username = request.POST.get('username') 
            email = request.POST.get('email')
            password1 = request.POST.get('pass1')
            password2 = request.POST.get('pass2')
            print(first_name)
            
            if not username:
                messages.error(request, 'Please provide a username')
                return redirect('register')
            elif not username.strip():
                messages.error(request, 'The username is not valid')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'The username is already taken')
                return redirect('register')
            
            try:
                validate_password(password1, user=User)
            except ValidationError as e:
                messages.error(request, ', '.join(e))
                return redirect('register')
            
            if len(password1) < 6:
                messages.error(request, 'The password should be at least 6 characters')
                return redirect('register')
            elif password1 != password2:
                messages.error(request, 'The passwords do not match')
                return redirect('register')
            if not any(char.isupper() for char in password1):
                messages.error(request, 'Password must contain at least one uppercase letter')
                return redirect('register')
            if not any(char.islower() for char in password1):  # Corrected condition
                messages.error(request, 'Password must contain at least one lowercase letter')
                return redirect('register')
            if not any(char.isdigit() for char in password1):
                messages.error(request, 'Password must contain at least one digit')
                return redirect('register')
            elif not re.match(r"^[\w\.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):  # Corrected regex pattern
                messages.error(request, 'Please enter a valid email address')
                return redirect('register')
            elif not validate_email(email):
                messages.error(request, 'Enter a valid email')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered')
                return redirect('register')

            otp = random.randint(1000, 9999)
            print(otp)
            otp_generated_at = timezone.now().isoformat()

            request.session['user_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,  
                'email': email,
                'password': password1,
                'otp': otp,
                'otp_generated_at' : otp_generated_at
                
            }

            send_mail(
                subject='Your OTP for verification',
                message=f'Your OTP for verification is: {otp}',
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True
            )
            messages.success(request, f'Welcome {first_name}')
            return redirect('my_otp')
        else:
            return render(request, 'register.html')
    except ValidationError as e:
        messages.error(request, ', '.join(e))
        return redirect('register')


@never_cache
def otp(request):
    try:
        email = request.session.get('user_data', {}).get('email', '')
        if request.method == 'POST':
            otp_digits = [request.POST.get(f'digit{i}') for i in range(1, 5)]

            if None in otp_digits:
                messages.error(request, 'Invalid OTP format, please try again.')
                return redirect('log_in')
            
            entered_otp = int(''.join(otp_digits))
            stored_otp = request.session.get('user_data', {}).get('otp')
            user_data = request.session.get('user_data', {})
            otp_generated_at = user_data.get('otp_generated_at', '')  # Get the ISO format string
            try:
                otp_generated_at_datetime = datetime.fromisoformat(otp_generated_at)
            except ValueError:
                otp_generated_at_datetime = None

            if otp_generated_at_datetime and otp_generated_at_datetime + timedelta(minutes=2) < timezone.now():
                messages.error(request, 'OTP has expired. Please try again.')
                return redirect('register')
            
            if str(entered_otp) == str(stored_otp):
                user = User.objects.create_user(username=user_data['username'], first_name=user_data['first_name'], last_name=user_data['last_name'], email=user_data['email'], password=user_data['password'])
                user.save()
                print('user created successfully')
                
                del request.session['user_data']
                print('session deleted')
                return render(request, 'log.html')
            else:
                messages.error(request, 'Invalid OTP, try again.')
                return redirect('my_otp')
            
        return render(request, 'otp.html', {'email': email})
    except Exception as e:
        messages.error(request, str(e))
        return redirect('register')


@never_cache
def log_in(request):
    try:
        if request.user.is_authenticated:
            return redirect('index')
        print('hello')
        if request.method == 'POST':
            email = request.POST.get('email')
            print(email)
            password = request.POST.get('password')
            print('recievied')

            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Email or password is incorrect')
                return redirect('login')
            

        return render(request, 'log.html')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('login')

def log_out(request):
    logout(request)
    return redirect('index')

def index(request):
    if request.user.is_authenticated:
        context = {'username' : request.user.username}  # Fixed request.user.username
        return render(request, 'index.html', context)
    return render(request, 'index.html')
