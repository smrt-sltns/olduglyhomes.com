from facebook.decorator import custom_login_required
from django.shortcuts import render, redirect 
from social_account_main.celery_task import negative_comments_today_send_email
from django.contrib import messages 



@custom_login_required
def refresh(request):
    """Call function to get currect ad/campaign status and capture comments."""
    try:
        negative_comments_today_send_email(user_id=request.user.id) 
        messages.info(request, "Your page is refreshed!")
    except Exception as e:
        messages.error(request, "Probled occured on refreshing. Please try after sometime.")
    return redirect(request.META.get('HTTP_REFERER', 'ad_spend'))