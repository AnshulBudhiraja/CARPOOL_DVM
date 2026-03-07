from django.db import models
from users.models import User
from roadmap.models import Node
from django.utils import timezone
from django.conf import settings

class Trip(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trips")

    start_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="driver_trip_start") 
    end_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="driver_trip_end") 

    max_passengers_trip = models.IntegerField(default=4)

    available_seats = models.IntegerField(default=4)

    route = models.JSONField(blank=True, null=True)

    current_node_index = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    departure_time = models.DateTimeField(default=timezone.now)

    passengers = models.ManyToManyField(User, related_name='joined_trips', blank=True)

    def __str__(self):
        return f"Trip: {self.start_node.name} to {self.end_node.name} by {self.driver.username} , seats left {self.available_seats}"
    
class Carpool_request(models.Model):
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carpool_request")

    STATUS_CHOICES = (
        ('Pending', 'Looking for a ride'),
        ('Matched', 'Matched with a driver'),
        ('Completed', 'Ride finished'),
        ('Cancelled', 'Cancelled')
    )

    start_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="passenger_trip_start")
    end_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="passenger_trip_end")

    matched_trip = models.ManyToManyField(
        Trip,
        null=True, 
        blank=True, 
        # related_name='offered_trips'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.passenger} requested to go : {self.start_node} --> {self.end_node}"
    
    
