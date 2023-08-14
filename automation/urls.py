from django.urls import path 
from .reports import negative_report, positive_report


urlpatterns = [
    path("negative-comment-report/<int:ad_id>/", negative_report, name="negative_report"),
    path("positive_report/<int:ad_id>", positive_report, name="positive_report"),
]