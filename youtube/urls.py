from django.urls import path
from . import views

urlpatterns = [
    path("", views.YoutubeIndex, name="youtube-index"),
    path('google-auth/', views.google_auth, name='google-auth'),
    path("add_channel", views.add_channel, name="add_channel"),
    path('auth/google/callback/', views.google_auth_callback, name='google-auth-callback'),
    path("switch", views.switch, name="switch"),
]

