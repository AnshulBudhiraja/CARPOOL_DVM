from django.db import models
from django.conf import settings

# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.FloatField(max_length=10,default = 0.00)

    def __str__(self):
        return f"{self.user} has a balance of {self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('TOP_UP','Top-up'),
        ('RIDE_FARE', 'Ride fare')
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    time_stamp = models.DateTimeField(auto_now_add=True)
    trx_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
