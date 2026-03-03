from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.signup_view, name="signup"),
    path("driver_signup/", views.driver_signup_view, name="driver_signup_view"),
    
]


