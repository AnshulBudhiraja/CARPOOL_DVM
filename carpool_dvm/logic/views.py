from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CreateTripForm, RequestTripForm
from django.contrib import messages
from .models import Trip, Carpool_request
from .utils import shortest_path, potential_ride_requests
from roadmap.models import  Node
from django.utils import timezone
from datetime import timedelta

@login_required
def publish_trip_view(request):
    if not hasattr(request.user, "driver"):
        return redirect('driver_signup_view')
    
    if request.method == 'POST':
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
                trip.delete()
                messages.success(request, "Trip cancelled successfully.")
            else:
                messages.error(request, "Trips cannot be cancelled within 30 minutes of departure time")
    return redirect('home_driver')


@login_required
def request_trip_view(request):

    if request.method == 'POST':
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
def offer_ride_view(request,req_id):
    if request.method == 'POST':
        carpool_req = get_object_or_404(Carpool_request, id=req_id)
        
        driver_trip = Trip.objects.filter(driver=request.user, is_active=True).first()
        
        if driver_trip:
            carpool_req.matched_trip.add(driver_trip)
            messages.success(request, f"Ride offer sent to {carpool_req.passenger.username}!")
        else:
            messages.error(request, "You don't have an active trip.")
            
    return redirect('home_driver')


# def request_result_view(request, req_id):
#     ride_request = get_object_or_404(Carpool_request, id = req_id , passenger = request.user)

#     all_offers = ride_request.matched_trip.all()

#     context = {
#         'ride_request': ride_request,
#         'offers': all_offers,
#     }

#     return render(request, "logic/request_results.html", context)
