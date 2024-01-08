from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import AdRecord
from django.contrib import messages 
from facebook.models import Creds, AccountsAd
from automation.models import LogNegativeComments
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
    print(f"ad account is set : {adaccount_is_set}")
        
    return render(request, "limit/limit.html", context)



def set_limit(request):
    if request.method == "POST":
        limit = request.POST['limit']
        ad_id = request.POST['ad_id']
        adrecord = AdRecord.objects.get(ad_id=ad_id)
        adrecord.ad_spend_limit = float(limit)
        adrecord.is_limit_set = True
        adrecord.save()
        
        print(limit, ad_id)
        messages.info(request , f"You have set a new limit for Ad -> `{adrecord.campaign_name} | {adrecord.adset_name} | {adrecord.ad_name}`.")
    return redirect("ad_spend")

def track(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        is_checked = request.POST.get('is_checked')
        print(ad_id, is_checked)
        adrecord = AdRecord.objects.get(ad_id=ad_id)
        if is_checked == 'true':
            adrecord.expired = False
            adrecord.save()
            # messages.info(request, f"We have stopped tracking `{adrecord.ad_name} | { adrecord.campaign_name}`. ")
        else:
            adrecord.expired = True
            adrecord.save()
            # messages.info(request, f"We have started tracking `{adrecord.ad_name} | {adrecord.campaign_name}`. ")

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})