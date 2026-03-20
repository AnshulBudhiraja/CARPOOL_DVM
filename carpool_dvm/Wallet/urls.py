from django.urls import path
from . import views

urlpatterns = [
    path("wallet_dashboard/", views.wallet_dashboard_view, name="wallet_dashboard"),
]


