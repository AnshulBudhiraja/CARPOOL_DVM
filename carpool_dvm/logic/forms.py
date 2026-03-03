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
            'max_passengers' : "How many vacant seats are there?",
        }

class RequestTripForm(forms.ModelForm):
    class Meta:
        model = Carpool_request
        fields = ["start_node", "end_node"]
        
