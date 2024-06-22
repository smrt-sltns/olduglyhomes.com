from django.urls import path 
from . import views 


urlpatterns = [
    path("home", views.home, name="conversations_home"),
    path('webhook/', views.facebook_webhook, name='facebook_webhook'),
]