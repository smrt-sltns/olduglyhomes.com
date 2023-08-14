from django.shortcuts import render, redirect 
from django.contrib.auth import logout
from django.urls import reverse
from .decorator import custom_login_required 
from .models import Creds, AccountPages, AccountsAd


# Create your views here.
def login(request):
  return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect(reverse("home"))



@custom_login_required
def home(request):
    user = request.user
    ad = AccountsAd.objects.filter(user=user)
    if ad.exists():
        ad_id = ad[0].id
        redirect_url = reverse("negative_report", args=[ad_id])
        return redirect(redirect_url)
    else:
        adaccount_is_set = False # needs to come from database 
        context = {
            "adaccount_is_set":adaccount_is_set,
        }
        return render(request,"index.html", context)