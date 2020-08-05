from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index),
    path("buy", views.buy),
    path("sell", views.sell),
    path("history", views.history),
    path("quote", views.quote),
    path("quoted", views.quoted),
    path("", views.index),
]
