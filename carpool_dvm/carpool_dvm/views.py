from django.shortcuts import render
from logic.models import Trip
from roadmap.models import Node
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'carpool_dvm/home.html')

def home_passenger(request):
    return render(request, 'carpool_dvm/home_passenger.html')


@login_required
def home_driver(request):
    active_trips = Trip.objects.filter(driver=request.user, is_active=True).order_by('-created_at')
    past_trips = Trip.objects.filter(driver=request.user, is_active=False).order_by('-created_at')
    
    context = {
        'active_trips': active_trips,
        'past_trips': past_trips
    }
    return render(request, 'carpool_dvm/home_driver.html', context)