from django.urls import path, include
from . import views

urlpatterns = [
    path("publish/", views.publish_trip_view, name="publish_trip_view"),
    path("request/", views.request_trip_view, name="request_trip_view"),
    path("cancel_trip/<int:trip_id>/", views.cancel_trip_view, name="cancel_trip"),
]
