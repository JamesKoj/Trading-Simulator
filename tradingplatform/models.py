from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.
class Transaction(models.Model):
    trader = models.ForeignKey(User, on_delete=models.CASCADE)
    companyName = models.CharField(max_length=80)
    symbol = models.CharField(max_length=5)
    quantity = models.IntegerField()
    price = models.FloatField()
    datetime = models.DateTimeField(default=datetime.now, blank=True)
