from django.urls import path, include
from . import views

urlpatterns = [
    path("publish/", views.publish_trip_view, name="publish_trip_view"),
    path("request/", views.request_trip_view, name="request_trip_view"),
    path("cancel_trip/<int:trip_id>/", views.cancel_trip_view, name="cancel_trip_view"),
    path("cancel_request/<int:req_id>/", views.cancel_request_view, name="cancel_request_view"),
    path("offer_trip/<int:req_id>/", views.offer_ride_view , name="offer_ride_view"),
    path("accept_trip/<int:trip_id>", views.accept_ride_view, name="accept_ride_view"),
    path("start_trip/<int:trip_id>", views.start_trip_view, name="start_trip_view"),
    path("end_trip/<int:trip_id>", views.end_trip_view, name="end_trip_view"),
    path("start_ride/<int:req_id>", views.start_ride_view, name="start_ride_view"),
    path("end_ride/<int:req_id>", views.end_ride_view, name="end_ride_view"),

]
