from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.utils import timezone

from .models import Refresh
from social_account_main.celery_task import negative_comments_today_send_email
from facebook.decorator import custom_login_required


@custom_login_required
def refresh(request):
    """Call function to get currect ad/campaign status and capture comments."""
    current_time = timezone.now()
    ten_minutes_ago = current_time - timezone.timedelta(minutes=10)
    recent_refresh = Refresh.objects.filter(user=request.user, refresh_time__gte=ten_minutes_ago).exists()
    if not recent_refresh:
        try:
            negative_comments_today_send_email(user_id=request.user.id) 
            Refresh.objects.create(user=request.user, refresh_time=current_time)
            messages.info(request, "Your page is refreshed!")
        except Exception as e:
            messages.error(request, "Problem occured while refreshing. Please try after sometime.")
    else: 
        messages.info(request, "Please wait for 10 minutes before refreshing again.")
        
    return redirect(request.META.get('HTTP_REFERER', 'ad_spend'))