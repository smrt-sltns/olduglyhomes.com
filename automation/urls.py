from django.urls import path 
from .reports import negative_report, positive_report, negative_comment_status


urlpatterns = [
    path("negative-comment-report/<int:ad_id>/", negative_report, name="negative_report"),
    path("positive_report/<int:ad_id>", positive_report, name="positive_report"),
    path("comment_view/<comment_id>/<ad_id>/<adset_id>", negative_comment_status, name="negative_comment_status"),
]