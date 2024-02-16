from facebook.decorator import custom_login_required
from django.shortcuts import render, redirect 
from social_account_main.celery_task import negative_comments_today_send_email



@custom_login_required
def refresh(request):
    """Call function to get currect ad/campaign status and capture comments."""
    negative_comments_today_send_email(user_id=request.user.id) 
    return redirect("ad_spend")