from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib import messages
from facebook.models import Creds, AccountPages,AccountsAd
from .models import LogNegativeComments, LogPositiveComments
from django.contrib import messages
from django.conf import settings 
from django.urls import reverse
from facebook.utils import get_ad_name_and_effective_object_story_id, get_access_token_for_ad
from facebook.decorator import custom_login_required
from django.conf import settings 
import json 
import urllib.request


@custom_login_required
def negative_report(request, ad_id):
    adaccount_is_set = Creds.objects.get(user=request.user).has_ad_accounts
    adaccount = AccountsAd.objects.get(id=ad_id)
    negativelog = LogNegativeComments.objects.all().filter(adaccount=adaccount).filter(is_deleted=False,  is_hidden=False).order_by('-automation_runtime')
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

@custom_login_required
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

@custom_login_required
def negative_comment_status(request, comment_id, ad_id, adset_id ):
    # comment = LogNegativeComments.objects.get(comment_id=comment_id)
    comment = LogNegativeComments.objects.get(comment_id=comment_id)
    adaccount = LogNegativeComments.objects.get(comment_id=comment_id).adaccount
    page_token = adaccount.page_associated.longlived_access_token
    name, eff = get_ad_name_and_effective_object_story_id(ad_id=ad_id, access_token=page_token)
    page_token = get_access_token_for_ad(eff=eff, user=request.user)
    comment_url  = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{eff}/comments?fields=id,message,created_time,is_hidden&summary=true&access_token={page_token}&pretty=1&summary=true&limit=100&after"
    comments_json = json.loads(urllib.request.urlopen(comment_url).read())
    # print(comment_url)
    all_comment_id = [comment['id'] for comment in comments_json['data']]
    if comment_id not in all_comment_id:
        comment.is_deleted = True
        comment.save()
        messages.info(request, f"This comment '{comment.comment}' is deleted")
        url = reverse('negative_report', args=[comment.adaccount.id])
        return redirect(url)
    else: 
        url = reverse("sentiment-graph", args=[adset_id])
        return redirect(url)


@custom_login_required
def no_reports(request, message):
    message = message
    pass 