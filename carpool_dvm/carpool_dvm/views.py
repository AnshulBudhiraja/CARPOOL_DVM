from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from logic.models import Trip, Carpool_request
from roadmap.models import Node
from django.utils import timezone
from logic.utils import potential_ride_requests

def home(request):
    return render(request, 'carpool_dvm/home.html')


def home_passenger(request):
    active_requests = Carpool_request.objects.filter(
        passenger=request.user,
        status__in=['Pending', 'Matched']
    ).order_by('-created_at')

    past_requests = Carpool_request.objects.filter(
        passenger=request.user,
        status__in=['Completed', 'Cancelled']
    ).order_by('-created_at')
    # invites = []
    # invites = active_requests.matched_trip.all()

    context = {
        'active_requests': active_requests,
        'past_requests': past_requests,
        # 'invites': invites
    }
    return render(request, 'carpool_dvm/home_passenger.html', context)


@login_required
def home_driver(request):
    active_trip = Trip.objects.filter(driver=request.user, is_active=True).order_by('-created_at').first()
    past_trips = Trip.objects.filter(driver=request.user, is_active=False).order_by('-created_at')

    potential_trips = []
    if active_trip:
       potential_trips = potential_ride_requests(active_trip)
    
    context = {
        'active_trip': active_trip,
        'past_trips': past_trips,
        'potential_trips' : potential_trips
    }

    return render(request, 'carpool_dvm/home_driver.html', context)
