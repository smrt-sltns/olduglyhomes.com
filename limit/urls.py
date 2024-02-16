from django.urls import path 
from . import views 
from .refresh import refresh


urlpatterns = [
    path("", views.ad_spend, name="ad_spend"),
    path('track/', views.track, name='track'),
    path("limit", views.set_limit, name="limit"),
    path("limit_campaign", views.set_limit_campaign, name="limit_campaign"),
    path("sort/<value>/", views.sort, name="sort"),
    path("adspenddays", views.adspenddays, name="adspenddays"),
    path("refresh", refresh, name="refresh"),
]