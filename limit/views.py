from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages 
from django.utils.safestring import mark_safe
from facebook.models import Creds, AccountsAd
from .models import AdRecord
from .utils import adrecord_groups
from facebook.decorator import custom_login_required
# Create your views here.


@custom_login_required
def ad_spend(request):
    """
    Group all the ads with ad groups and futher 
    group then with associated campaign. 
    Display this group on limit.html
    """
    adrecords = AdRecord.objects.all().filter(user=request.user, is_active=True)
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    ad_records_by_campaign = adrecord_groups(adrecords=adrecords)
    
    context = {
        "adaccount_is_set": adaccount_is_set,
        'adrecords': ad_records_by_campaign
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts        
    return render(request, "limit/limit.html", context)


custom_login_required
def set_limit(request):
    if request.method == "POST":
        limit = request.POST['limit']
        ad_id = request.POST['ad_id']
        adrecord = AdRecord.objects.get(ad_id=ad_id)
        adrecord.ad_spend_limit = float(limit)
        adrecord.is_limit_set = True
        adrecord.expired = False
        adrecord.save()
        msg = f"You have set a new limit for Ad : `<strong >{adrecord.adset_name} -> {adrecord.ad_name} | $ {adrecord.ad_spend_limit }</strong>`."
        safe_message = mark_safe(msg)
        messages.info(request ,safe_message)
    return redirect("ad_spend")

@custom_login_required
def set_limit_campaign(request):
    if request.method == "POST":
        limit = request.POST['limit_campaign']
        campaign_id = request.POST['campaign_id']
        campaigns = AdRecord.objects.filter(campaign_id = campaign_id).all()
        for campaign in campaigns:
            campaign.campaign_spend_limit = limit
            campaign.is_campaign_limit_set = True
            campaign.save()
        msg = f"You have set a new limit for Campaign -> `<strong >{campaign.campaign_name} | $ {float(campaign.campaign_spend_limit)}</strong>`."
        safe_message = mark_safe(msg)
        messages.info(request ,safe_message)
    return redirect("ad_spend")

@custom_login_required
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

@custom_login_required
def sort(request, value):
    value_dir = {
        "active": "-is_active",
        "inactive": "is_active",
        "tracked": "expired",
        "untracked" : "-expired",
        "lowest" : "adset_spend",
        "highest": "-adset_spend"  
        
    }
    flt = value_dir.get(value)
    adrecords = AdRecord.objects.all().filter(user=request.user).order_by(flt).all()
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    adrecords_by_campaign = adrecord_groups(adrecords=adrecords)
    context = {
        "adaccount_is_set": adaccount_is_set,
        'adrecords': adrecords_by_campaign
        }
    if adaccount_is_set:
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        context['adaccounts'] = adaccounts
    return render(request, "limit/limit.html",context )
        