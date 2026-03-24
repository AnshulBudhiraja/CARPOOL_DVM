from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CreateTripForm, RequestTripForm
from django.contrib import messages
from .models import Trip, Carpool_request
from .utils import shortest_path, passenger_route, passenger_fare
from roadmap.models import  Node
from django.utils import timezone
from datetime import timedelta
from Wallet.models import Wallet, Transaction

@login_required
def publish_trip_view(request):
    if not hasattr(request.user, "driver"):
        return redirect('driver_signup_view')
    
    active_trip_exists = Trip.objects.filter(
        driver = request.user,
        status__in = ['Active', 'In Progress']
    ).exists()

    carpool_req = Carpool_request.objects.filter(
        passenger = request.user,
        status__in = ['Pending', 'Confirmed', 'In Progress']
    ).exists()

    if carpool_req:
        messages.error(request, "You have a ride ongoing. Please complete it before starting a trip.")
        return redirect('home_driver')

    if active_trip_exists:
        messages.error(request, "You already have an ongoing trip! Please complete it before starting a new one.") 
        return redirect('home_driver')

    if request.method == 'POST' :
        form = CreateTripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = request.user

            node_ids = shortest_path(trip.start_node.id, trip.end_node.id)

            if not node_ids:
                return render(request, "logic/create_trip.html",
                         {
                            "form": form,
                            "error": "❌ No physical route exists between these two locations on the campus map!"
                            })
            nodes = Node.objects.filter(id__in = node_ids)
            node_dict = {n.id : n.name for n in nodes}

            detailed_route = []
            for node_id in node_ids:
                detailed_route.append({
                    "id" : node_id,
                    "name": node_dict.get(node_id, "Unknown Node")
                })

            trip.route = detailed_route
            trip.available_seats = form.cleaned_data.get('max_passengers_trip')
            trip.status = 'Active'
            trip.save()
            return redirect("home_driver")
    else :
        form = CreateTripForm()

    return render(request, "logic/create_trip.html", {"form":form})


def cancel_trip_view(request, trip_id):
    if request.method == "POST":
        trip = get_object_or_404(Trip, id=trip_id)

        now = timezone.now()
        time_left = trip.departure_time - now

        if trip.driver != request.user:
            messages.error(request, "Unauthorized: You cannot cancel someone else's trip.")

        if trip.driver == request.user:
            if time_left > timedelta(minutes = 30):
                trip.is_active = False
                trip.status = 'Cancelled'
                trip.save()
                messages.success(request, "Trip cancelled successfully.")
            else:
                messages.error(request, "Trips cannot be cancelled within 30 minutes of departure time")
    return redirect('home_driver')


@login_required
def request_trip_view(request):
    buffer_time = timezone.now() - timedelta(hours=1)
    active_req_exists = Carpool_request.objects.filter(
        passenger = request.user,
        status__in = ['Confirmed', 'Pending'],
        request_time__gt = buffer_time 
    ).exists()

    active_trip_exists = Trip.objects.filter(
        driver = request.user,
        status__in = ['Active', 'In Progress']
    ).exists()

    if active_trip_exists:
        messages.error(request, "You have an active or running trip ")

    if active_req_exists:
        messages.error(request, "You already have an ongoing trip! Please complete it before starting a new one.")

    if request.method == 'POST' and not active_trip_exists and not active_req_exists:
        form  = RequestTripForm(request.POST)

        if form.is_valid():
            ride_request = form.save(commit=False)
            ride_request.passenger = request.user
            ride_request.save()
            return redirect("home_passenger")

    else:
        form = RequestTripForm()
    
    return render(request, "logic/request_trip.html", {"form": form})


@login_required
def cancel_request_view(request, req_id):
    if request.method == "POST":
        carpool_request = get_object_or_404(Carpool_request, id=req_id)

        if carpool_request.passenger != request.user:
            messages.error(request, "Unauthorized: You cannot cancel someone else's request.")
            return redirect("home_passenger")

        if carpool_request.status == "Pending":
            carpool_request.status = "Cancelled"
            carpool_request.save()
            messages.success(request, "Request cancelled successfully.")
            
        else:
            messages.error(request, "This request cannot be cancelled in its current state.")

    return redirect("home_passenger")

@login_required
def offer_ride_view(request,req_id):
    if request.method == 'POST':
        carpool_req = get_object_or_404(Carpool_request, id=req_id)
        
        driver_trip = Trip.objects.filter(driver=request.user, is_active=True, status__in =['Active', 'In Progress']).first()
        
        if driver_trip and driver_trip.available_seats > 0:
            carpool_req.matched_trip.add(driver_trip)
            messages.success(request, f"Ride offer sent to {carpool_req.passenger.username}!")

        elif driver_trip.available_seats <= 0:
            messages.error(request, "There are no empty seats for passengers")

        else:
            messages.error(request, "You don't have an active trip.")
            
    return redirect('home_driver')


def accept_ride_view(request, trip_id):
    if request.method == 'POST':
        accepted_trip = get_object_or_404(Trip, id=trip_id)

        carpool_req = Carpool_request.objects.filter(
            passenger = request.user,
            status = 'Pending',
            matched_trip = accepted_trip
        ).first()

        if carpool_req.confirmed_trip:
            messages.error(request, "You have already accepted a ride!")

        if carpool_req and not carpool_req.confirmed_trip :
            user_wallet = request.user.wallet
            fare = passenger_fare(carpool_req,accepted_trip,100,200)
            if user_wallet.balance < fare :
                messages.error(request, "You do not have adequate wallet balance for the trip.")
                return redirect('wallet_dashboard')

            elif user_wallet.balance >= fare:

                carpool_req.confirmed_trip = accepted_trip
                carpool_req.final_route = passenger_route(carpool_req, accepted_trip)
                
                carpool_req.status = 'Confirmed'

                accepted_trip.available_seats -= 1
                accepted_trip.passengers.add(request.user)

                user_wallet.balance -= fare
                Transaction.objects.create(
                    wallet = user_wallet,
                    amount = fare,
                    trx_type = 'RIDE_FARE',
                    description = f"Ride from {carpool_req.start_node} to {carpool_req.end_node}"
                )
                user_wallet.save()
                accepted_trip.save()
                carpool_req.save()

                messages.success(request, f"Ride accepted! Driver : {accepted_trip.driver}. Fare amount {fare} deducted from Wallet")

        else:
            messages.error(request, " You don't have a pending request")

    return redirect('home_passenger')


def start_trip_view(request, trip_id):
    trip = get_object_or_404(Trip, id = trip_id, driver = request.user)
    if trip.status == 'Active' and timezone.now() >= trip.departure_time:
        trip.status = 'In Progress' 
        trip.save()
        messages.success(request, "Trip started! Drive safely to your destination.")

    elif timezone.now() < trip.departure_time:
        messages.error(request, "You cannot start the trip before departure time")

    else:
        messages.error(request, "Trip cannot be started (it might be already running or completed)")

    return redirect('home_driver')


def end_trip_view(request, trip_id):
    trip = get_object_or_404(Trip, id = trip_id, driver = request.user)

    if trip.status == 'In Progress' and trip.current_node_index == (len(trip.route)-1):
        trip.status = 'Completed'
        trip.is_active = False
        trip.save()
        messages.success(request, "Congratulations! You completed a trip.")

    else:
        messages.error(request, "You have no trip in progress")

    return redirect('home_driver')


def start_ride_view(request, req_id):
    carpool_req = get_object_or_404(Carpool_request, id = req_id, passenger = request.user)

    if carpool_req.status == 'Confirmed' and carpool_req.confirmed_trip.status == 'In Progress':
        carpool_req.status = 'In Progress'
        carpool_req.save()
        messages.success(request, "Ride Started")

    else :
        messages.error(request, "You have no pending request or the ride has not started")

    return redirect('home_passenger')


def end_ride_view(request, req_id):
    carpool_req = get_object_or_404(Carpool_request, id = req_id, passenger = request.user)

    if carpool_req.status == 'In Progress':
        carpool_req.status = 'Completed'
        carpool_req.save()
        messages.success(request, "Glad you reached! Don't forget your luggage.")

    else:
        messages.error(request, "You have no rides in progress")
    
    return redirect('home_passenger')
        

