from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib import messages
from facebook.models import Creds, AccountPages,AccountsAd
from .models import LogNegativeComments, LogPositiveComments
from django.conf import settings 


def negative_report(request, ad_id):
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    adaccount = AccountsAd.objects.get(id=ad_id)
    negativelog = LogNegativeComments.objects.all().filter(adaccount=adaccount).order_by('-automation_runtime')
    context = {
        # "all_campaigns":all_campaigns,
        "base_url": settings.BASE_URL,
        "adaccount_is_set": adaccount_is_set,
        "negative_log": negativelog,
        "adaccount":adaccount,
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts
    return render(request, "reports/negative_comments.html", context) 


def positive_report(request, ad_id):
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    adaccount = AccountsAd.objects.get(id=ad_id)
    postivelog = LogPositiveComments.objects.all().filter(adaccount=adaccount).order_by('-automation_runtime')
    context = {
        # "all_campaigns":all_campaigns,
        "base_url": settings.BASE_URL,
        "adaccount_is_set": adaccount_is_set,
        "positive_log": postivelog,
        "adaccount":adaccount,
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts
    return render(request, "reports/positive_comments.html", context) 



def no_reports(request, message):
    message = message
    pass 