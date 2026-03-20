from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import DriverSetUpForm, UserSignupForm, DriverLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .models import User, Driver

from django.contrib import messages
# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserSignupForm()
    return render(request, 'users/signup.html', {'form': form})

@login_required
def driver_signup_view(request):
    if request.method == 'POST':
        form = DriverSetUpForm(request.POST)
        d_pass = request.POST.get('driver_password')
        if not d_pass:
            return HttpResponse("You must set a password to become a driver!")
        if form.is_valid():
            current_user = request.user
            current_user.is_driver = True
            current_user.save(update_fields=['is_driver'])

            driver_obj = form.save(commit=False)
            driver_obj.user = current_user
            driver_obj.driver_password = d_pass 
            driver_obj.save()
            
            login(request,current_user,backend='django.contrib.auth.backends.ModelBackend')

            return redirect('home_driver')
    else:
        form = DriverSetUpForm()

    return render(request, 'users/driver_signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # You might want to redirect based on user role but let's default to home
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


def driver_login_view(request):
    if request.method == 'POST':
        form = DriverLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home_driver')
        
    else:
        form = DriverLoginForm()
    return render(request, 'users/driver_login.html', {'form' : form})


    