from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from logic.models import Trip, Carpool_request
from roadmap.models import Node
from django.utils import timezone
from logic.utils import potential_ride_requests, passenger_route , passenger_fare

@login_required
def home(request):
    prev_trips = Trip.objects.filter(
        driver = request.user,
        status = 'Completed'
    ).all()
    
    prev_rides = Carpool_request.objects.filter(
        passenger=request.user,
        status = 'Completed'
    ).all()

    context = {
        "past_trips" : prev_trips,
        "past_rides" : prev_rides
    }
    return render(request, 'carpool_dvm/home.html', context)


def home_passenger(request):
    active_requests = Carpool_request.objects.filter(
        passenger=request.user,
        status__in=['Pending','Confirmed']
    ).order_by('-created_at').first()

    past_requests = Carpool_request.objects.filter(
        passenger=request.user,
        status__in=['Completed', 'Cancelled']
    ).order_by('-created_at')

    carpool_request = Carpool_request.objects.filter(
        passenger = request.user
    ).all()

    context = {
        'req': active_requests,
        'past_requests': past_requests,
    }

    if active_requests:
        matched_trips = active_requests.matched_trip.all()

        offers = []
        for trip in matched_trips:
            path = passenger_route(active_requests,trip)
            trip_fare = passenger_fare(active_requests, trip , 100 , 200)
            offers.append(
                {
                    "trip" : trip,
                    "route" : path,
                    "fare" : trip_fare
                }
            )

        context['offers'] = offers
    

    return render(request, 'carpool_dvm/home_passenger.html', context)


@login_required
def home_driver(request):
    active_trip = Trip.objects.filter(driver=request.user, is_active=True, status__in = ['Active','In Progress']).order_by('-created_at').first()
    past_trips = Trip.objects.filter(driver=request.user, is_active=False, status__in = ['Completed', 'Cancelled']).order_by('-created_at')

    potential_trips = []
    if active_trip:
       potential_trips = potential_ride_requests(active_trip)
    
    context = {
        'active_trip': active_trip,
        'past_trips': past_trips,
        'potential_trips' : potential_trips
    }

    return render(request, 'carpool_dvm/home_driver.html', context)
