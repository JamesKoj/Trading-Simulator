from django.db import models
from django.contrib.auth.models import User


class Trader(models.Model):
    trader = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.FloatField()
