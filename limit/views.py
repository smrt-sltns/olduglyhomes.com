from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import AdRecord
from django.contrib import messages 
from facebook.models import Creds, AccountsAd
from django.utils.safestring import mark_safe
# Create your views here.

def ad_spend(request):
    adrecords = AdRecord.objects.all().filter(user=request.user).order_by('-is_active')
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    context = {
        "adaccount_is_set": adaccount_is_set,
        'adrecords': adrecords
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts        
    return render(request, "limit/limit.html", context)



def set_limit(request):
    if request.method == "POST":
        limit = request.POST['limit']
        ad_id = request.POST['ad_id']
        adrecord = AdRecord.objects.get(ad_id=ad_id)
        adrecord.ad_spend_limit = float(limit)
        adrecord.is_limit_set = True
        adrecord.expired = False
        adrecord.save()
        msg = f"You have set a new limit for Ad -> `<strong >{adrecord.campaign_name} | {adrecord.adset_name} | {adrecord.ad_name}</strong>`."
        safe_message = mark_safe(msg)
        messages.info(request ,safe_message)
    return redirect("ad_spend")

def track(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        is_checked = request.POST.get('is_checked')
        adrecord = AdRecord.objects.get(ad_id=ad_id)
        if is_checked == 'true':
            adrecord.expired = False
            adrecord.save()
        else:
            adrecord.expired = True
            adrecord.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def sort(request, value):
    value_dir = {
        "active": "-is_active",
        "inactive": "is_active",
        "tracked": "expired",
        "untracked" : "-expired",
        "lowest" : "ad_spend",
        "highest": "-ad_spend"  
        
    }
    flt = value_dir.get(value)
    adrecords = AdRecord.objects.all().filter(user=request.user).order_by(flt)
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    context = {
        "adaccount_is_set": adaccount_is_set,
        'adrecords': adrecords
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts
    return render(request, "limit/limit.html",context )
        