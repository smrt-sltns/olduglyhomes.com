from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib import messages
from facebook.models import Creds, AccountPages,AccountsAd
from .models import LogNegativeComments, LogPositiveComments
from django.contrib import messages
from django.conf import settings 
from django.urls import reverse
from facebook.utils import get_ad_name_and_effective_object_story_id, get_access_token_for_ad
import json 
import urllib.request

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


def negative_comment_status(request, comment_id, ad_id, adset_id ):
    access_token = Creds.objects.get(user=request.user).LONGLIVED_ACCESS_TOKEN
    comment = LogNegativeComments.objects.get(comment_id=comment_id)
    adaccount = LogNegativeComments.objects.get(comment_id=comment_id).adaccount
    page_token = adaccount.page_associated.longlived_access_token
    adaccount_id = adaccount.id
    name, eff = get_ad_name_and_effective_object_story_id(ad_id=ad_id, access_token=access_token)
    comment_url  = f"https://graph.facebook.com/v16.0/{eff}/comments?fields=id,message,created_time,is_hidden&summary=true&access_token={page_token}&pretty=1&summary=true&limit=100&after"
    comments_json = json.loads(urllib.request.urlopen(comment_url).read())
    print(comment_url)
    all_comment_id = [comment['id'] for comment in comments_json['data']]
    if comment_id not in all_comment_id:
        comment.is_deleted = True
        comment.save()
        messages.error(request, f"This comment '{comment.comment}' is deleted")
        url = reverse('negative_report', args=[adaccount_id])
        return redirect(url)
    else: 
        url = reverse("sentiment-graph", args=[adset_id])
        return redirect(url)



def no_reports(request, message):
    message = message
    pass 