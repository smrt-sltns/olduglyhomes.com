from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from textblob import TextBlob

import urllib.request 
import requests 
import plotly.offline as opy
import plotly.graph_objs as go
from asgiref.sync import sync_to_async

from .models import Creds, AccountPages, AccountsAd
from .sentiment_graph import get_sentiment_graph
from .utils import (
    get_ad_id_list,get_ad_name_and_effective_object_story_id, 
    get_campaign_name_and_id, get_adsets_from_campaign,
    get_single_campaign, comment_count, comment_info, get_adset_name,
    get_ad_account, pages_associated_with_adaccounts,
    single_ad_info, get_all_campaigns, get_access_token_for_ad
    )
from .myads_test import save_pages_to_adaccount
from .decorator import custom_login_required
from access_token import LONGLIVED_ACCESS_TOKEN




# get list of adsets from the campains and also display the campaing name
@custom_login_required
def adset_list(request, account_id, access_token):
    request.session['page_access_token'] = access_token
    campaign_id, campaign_name = get_all_campaigns(ad_id=account_id, token=access_token)
    adsets =   get_adsets_from_campaign(campaign_id=campaign_id, access_token=access_token)
    all_campaigns =  get_campaign_name_and_id(account_id=account_id,access_token=access_token)
    request.session['all_campaigns'] = all_campaigns
    adaccount_is_set = False
    adaccounts = AccountsAd.objects.filter(user=request.user).all()
    if len(adaccounts) == 0:
        messages.error(request, "We couldn't find any Ad Accounts.")
        messages.info(request, "Please select all the Accounts you have ad campaigns on!")
        return redirect(reverse("save-adaccounts"))
    else:
        adaccount_is_set = True
        context = {
            "adsets":adsets,
            "all_campaigns":all_campaigns,
            "campaign_name":campaign_name,
            "adaccount_is_set":adaccount_is_set
        }
        return render(request, "facebook_ads/adset_list.html", context)
    
@custom_login_required
def adset_list_campaign(request, campaign_id):
    access_token = request.session['page_access_token']
    adsets = get_adsets_from_campaign(campaign_id=campaign_id, access_token=access_token)
    campaign_name = get_single_campaign(campaign_id=campaign_id, access_token=access_token)
    all_campaigns = request.session['all_campaigns']
    adaccount_is_set = False
    adaccounts = AccountsAd.objects.all().filter(user=request.user)
    if len(adaccounts) == 0:
        messages.error(request, "We couldn't find any Ad Accounts.")
        messages.info(request, "Please select all the Accounts you have ad campaigns on!")
        return redirect(reverse("save-adaccounts"))
    else:
        adaccount_is_set = True
        context = {
            "adsets":adsets,
            "all_campaigns":all_campaigns,
            "campaign_name":campaign_name,
            "adaccount_is_set":adaccount_is_set
        }
        return render(request, "facebook_ads/adset_list.html", context)



@custom_login_required
def sentiment_graph(request, adset_id):
    if "page_access_token" in request.session:
        
        access_token = request.session['page_access_token']
    else : 
        access_token = Creds.objects.get(user=request.user).LONGLIVED_ACCESS_TOKEN
    if "all_campaigns" in request.session:
        
        all_campaigns = request.session['all_campaigns']
    else: 
        all_campaigns =  []
        
    try:
        graph_container = []
        ad_id_list = get_ad_id_list(campaign_id=adset_id, access_token=access_token)
        adset_name = get_adset_name(adset_id=adset_id, access_token=access_token)
        for ad_id in ad_id_list:
            name, eff = get_ad_name_and_effective_object_story_id(ad_id=ad_id, access_token=access_token)
            page_token = get_access_token_for_ad(eff=eff, user=request.user)
            
            comment_len = comment_count(eff, access_token=page_token)
            if comment_len > 1:
                graph = get_sentiment_graph(effective_object_story_id=eff, post_title=name, access_token=page_token)
                graph_container.append(graph)
        request.session['page_access_token'] = page_token
        context = {
            "graph_container":graph_container,
            "all_campaigns":all_campaigns,
            "adset_name":adset_name,
            "adset_id":adset_id, 
        }
        if len(graph_container) ==0:
            messages.info(request, "No comments found in this AD Group!")
            context.update({"no_comments":True})
        return render(request, "facebook_ads/sentiment-graph.html", context)
    except Exception as e:
        print(e)
        return render(request, "facebook_ads/404NOADS.html", {"all_campaigns":all_campaigns})



@custom_login_required
def Hide_comment(request, adset_id, comment_id):
    url = f'https://graph.facebook.com/{comment_id}'
    access_token = request.session['page_access_token']
    data = {
        'is_hidden': 'true',
        'access_token': access_token
    }
    response = requests.post(url, data=data)
    comment_message = comment_info(comment_id, access_token=access_token)
    print(comment_message)
    if response.status_code == 200:
        
        messages.success(
            request, 
            "Your request was successful. \nComment : `{}` is hidden now from users.".format(comment_message)
            )
    else:
        print(response.text)
        messages.error(request, f"Failed to hide `{comment_message}`.")
    print("status code , ",response.status_code)
    return HttpResponseRedirect(reverse('sentiment-graph', kwargs={'adset_id': adset_id}))


@custom_login_required
def Unhide_comment(request, adset_id, comment_id):
    url = f'https://graph.facebook.com/{comment_id}'
    access_token = request.session['page_access_token']
    data = {
        'is_hidden': 'false',
        'access_token': access_token
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        comment_message = comment_info(comment_id, access_token=access_token)
        messages.success(
            request, 
            "Your request was successful. \nComment : `{}` is unhidden now from users.".format(comment_message)
            )
    else:
        print(response.text)
        messages.error(request, f"Failed to Unhide `{comment_message}`.")
    return HttpResponseRedirect(reverse('sentiment-graph', kwargs={'adset_id': adset_id}))


def set_accountad(request):
    user = request.user
    creds = Creds.objects.get(user=user)
    token = creds.LONGLIVED_ACCESS_TOKEN # user access token 
    if request.method == "POST":
        adaccounts = request.POST.getlist("page_account")
        print("PAGE ACCOUNT IDS ::: {}".format(adaccounts))
        for a in adaccounts:
            ad_id, ad_name = single_ad_info(token=token, ad_id=a)
            try:
                adaccount_ = AccountsAd.objects.filter(ad_account_id=ad_id)
                if adaccount_.exists():
                    adaccount = AccountsAd.objects.get(ad_account_id=ad_id)
                    token = adaccount.page_associated.longlived_access_token
                    adaccount.access_token = token
                    adaccount.save()
                    if not creds.has_ad_accounts:
                        creds.has_ad_accounts = True
                        creds.save()
                    messages.info(
                        request, 
                        f"{ad_name} already in database! Access token for {adaccount.ad_account_name} is refreshed."
                        )
                else: 
                    page_id = save_pages_to_adaccount(request=request, ad_account_id=ad_id)
                    page_ = AccountPages.objects.get(page_id=page_id)
                    ad_object = AccountsAd()
                    ad_object.page_associated = page_
                    ad_object.user = user
                    ad_object.ad_account_name = ad_name
                    ad_object.ad_account_id = ad_id
                    ad_object.access_token = page_.longlived_access_token
                    ad_object.save()
                    if not creds.has_ad_accounts:
                        creds.has_ad_accounts = True
                        creds.save()
                    messages.success(request, "{} saved successfully!".format(ad_name))
            except Exception as e:
                    print(e)
                    messages.error(request, "Failed to save <b>{}</b>.".format(ad_name))
        return redirect(reverse("home"))
    else:
        adaccounts = get_ad_account(token=token)
        context = {}
        if adaccounts['status'] == 200:
            context['adaccounts'] = adaccounts['data']
            return render(request, "facebook_ads/choose_adaccount.html", context)
        else:
            messages.error(request, "We counldn't find any live ad accounts ")
            raise redirect(reverse('home'))

