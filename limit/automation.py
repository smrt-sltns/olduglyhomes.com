import requests 
from decouple import config 
from facebook.models import Creds
from django.contrib.auth.models import User 
from django.db.models import Q
from django.conf import settings 
import json 
import os 
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, send_mail
from datetime import datetime, timedelta
from .models import AdRecord, AdRecordSpenddate
from .utils import email_to_file_name, one_month_old_dates
from .ad_status import set_ad_status, set_campaign_status




def check_spend_limit_ad(user_id="3"):
    """
    run every 20 minutes on selected ads 
    which have their limit set and if limit 
    set has exceeded then send the email to the 
    user associated 
    """
    over_spend_ads = []
    days = AdRecordSpenddate.objects.get(user_id=user_id)
    user = User.objects.get(id=user_id)
    access_token = Creds.objects.get(user=user).LONGLIVED_ACCESS_TOKEN
    ads = AdRecord.objects.filter(user=user,is_active=True, expired=False).all()
    today_date, last_month_date = one_month_old_dates(days_old=days.days)
    
    for ad in ads:
        url =  f'https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad.ad_id}/insights?fields=spend&time_range[since]={last_month_date}&time_range[until]={today_date}&access_token={access_token}'
        try:
            response = requests.get(url=url)
        except Exception as e:
            print(e)
            pass
        content = response.json()
        spend = content['data'][0]['spend'] if len(content['data']) > 0 else 0
        ad.ad_spend = spend
        ad.is_limit_set = True
        ad.save()
        if float(spend) > ad.ad_spend_limit and ad.is_limit_set == True and ad.ad_spend_limit  != 0.0:
            over_spend_ads.append(ad)
            ad.expired = True
            ad.save()
            result = set_ad_status(access_token=access_token, ad_id=int(ad.ad_id), status="PAUSED")
            if result == True:
                ad.is_active = False
                ad.save()
        print(ad.ad_name, ad.ad_spend, ad.ad_spend_limit)
    return (over_spend_ads, user.email)


def check_spend_limit_campaign(user_id):
    days = AdRecordSpenddate.objects.get(user_id=user_id)
    adrecords = AdRecord.objects.filter(user__id=user_id, is_active=True).all()
    campaigns = list(set([c.campaign_id for c in adrecords]))    
    today_date, last_month_date = one_month_old_dates(days_old=days.days)
    access_token = Creds.objects.get(user__id=user_id).LONGLIVED_ACCESS_TOKEN
    over_spend_campaigns = []
    for campaign in campaigns:
        url_last_month =  f'https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign}/insights?fields=spend&time_range[since]={last_month_date}&time_range[until]={today_date}&access_token={access_token}'
        try:
            response_last_month = requests.get(url=url_last_month)
        except Exception as e:
            print(e)
            pass
        content_last_month = response_last_month.json()
        spend = content_last_month['data'][0]['spend'] if len(content_last_month['data']) > 0 else 0
        print(f"campaign : {campaign} ->>>>> {spend}")
        db_campaign = AdRecord.objects.filter(campaign_id=campaign).all()
        for dc in db_campaign:
            dc.campaign_spend = spend
            dc.save()
        if float(dc.campaign_spend) > float(dc.campaign_spend_limit) and dc.is_campaign_limit_set == True and dc.campaign_spend_limit  != 0.0:
            over_spend_campaigns.append(dc)
            result = set_campaign_status(access_token=access_token, campaign_id=int(dc.campaign_id), status="PAUSED")
            if result == True:
                AdRecord.objects.filter(campaign_id=dc.campaign_id).update(is_campaign_limit_set=False, is_active=False)
            print(f"campaign : {dc.campaign_name} limit is reached!")
    return over_spend_campaigns


def check_spend_limit_adset(user_id, days=30):
    days = AdRecordSpenddate.objects.get(user_id=user_id)
    adrecords = AdRecord.objects.filter(user__id=user_id, is_active=True).all()
    access_token = Creds.objects.get(user__id=user_id).LONGLIVED_ACCESS_TOKEN
    adsets = list(set([c.adset_id for c in adrecords]))    
    today_date, last_month_date = one_month_old_dates(days=days.days)
    for adset in adsets:
        url =  f'https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{adset}/insights?fields=spend&time_range[since]={last_month_date}&time_range[until]={today_date}&access_token={access_token}'
        try:
            response = requests.get(url=url)
        except Exception as e:
            print(e)
            pass
        content = response.json()
        spend = content['data'][0]['spend'] if len(content['data']) > 0 else 0
        print(f"{adset} ->>>>> {spend}")
        db_campaign = AdRecord.objects.filter(adset_id=adset).all()
        for dc in db_campaign:
            dc.adset_spend = spend
            dc.save()
    return len(adsets)


def send_limit_exceed_mail(adlist, user_email, campaignlist):
    """
    Send remider email to user if 
    ad spend limit has exceeded 
    """ 
    if len(adlist) != 0 or len(campaignlist) != 0:
        msg_html = render_to_string('email_template/spend_limit.html', 
                                    {'adlist': adlist, "campaignlist": campaignlist})
        send_mail(
            'Ad Spend limit reached!',
            "Check belows Ads that have surpassed the spend limit!",
            settings.EMAIL_HOST_USER,
            [ user_email, "kundan.k.pandey02@gmail.com"],
            html_message=msg_html,
        )
