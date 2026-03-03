from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    license_number = models.CharField(max_length=50, unique=True)
    car_model = models.CharField(max_length=100, help_text="e.g., Maruti Suzuki Swift")
    plate_number = models.CharField(max_length=20, help_text="e.g., RJ 18 XY 1234")
    max_passengers_car = models.IntegerField(default=4, help_text="Total empty seats available for passengers")

    def __str__(self):
        return f"DRIVER : {self.user.username} with CAR: {self.car_model}"

