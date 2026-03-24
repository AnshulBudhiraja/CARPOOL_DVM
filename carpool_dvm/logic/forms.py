from django import forms
from .models import Trip, Carpool_request
from roadmap.models import Node

class CreateTripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['start_node', 'end_node', 'max_passengers_trip', 'departure_time']
        labels = {
            'start_node' : "Where do you want to start from?",
            'end_node' : "Where do you want to go?",
            'max_passengers_trip' : "How many vacant seats are there?",
            'departure_time' : "What time do you want to leave at?"
        }
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class RequestTripForm(forms.ModelForm):
    class Meta:
        model = Carpool_request
        fields = ['start_node', 'end_node', 'request_time']
        labels = {
            'start_node' : "Select your pickup point",
            'end_node' : "Select your dropoff point",
            'request_time' : "Input boarding time"
        }
        widgets = {
            'request_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
