from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.signup_view, name="signup"),
    path("driver_signup/", views.driver_signup_view, name="driver_signup_view"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout")
    ]


