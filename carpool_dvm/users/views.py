from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import DriverSetUpForm, UserSignupForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
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
        if form.is_valid():
            my_object = form.save(commit=False)
            my_object.user = request.user
            my_object.save()
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

    