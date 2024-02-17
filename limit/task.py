from celery import shared_task
import requests 
from .models import AdRecord
from .utils import email_to_file_name
from .automation import check_spend_limit_ad, check_spend_limit_adset, check_spend_limit_campaign, send_limit_exceed_mail
from decouple import config 
from facebook.models import Creds
from django.contrib.auth.models import User 
from django.conf import settings 
import json 
import os 




@shared_task
def capture_new_ads(user_id):
    """
    run every hour and capture new ads 
    with infomation like campaign and adset information.
    """
    user = User.objects.get(id=user_id)
    folder = os.path.join(settings.BASE_DIR, F"JSON/{email_to_file_name(email=user.email)}")
    existing_ads = AdRecord.objects.filter(user=user).all()
    user_files = os.listdir(folder)
    active_ad_list = []
    for file in user_files:
        read_data = open(f"{folder}/{file}", "r").read()
        ads_data = json.loads(read_data)
        for adset in ads_data:
            campaign_name = adset['campaign_name']
            campaign_id = adset['campaign_id']
            for ad in adset['adsets']:
                adset_name = ad['adset_name']
                adset_id = ad['adset_id']
                for a in ad['ads']:
                    ad_id = a['ad_id']
                    ad_name = a['ad_name']
                    eff = a['eff']
                    active_ad_list.append(ad_id)
                    adrecord = AdRecord()
                    if not AdRecord.objects.filter(ad_id=ad_id).exists():
                        adrecord = AdRecord(
                            user = user,
                            ad_id=ad_id, ad_name=ad_name, 
                            adset_name=adset_name, adset_id=adset_id, 
                            campaign_id = campaign_id, campaign_name=campaign_name,
                            effective_object_story_id=eff, 
                            account_id = "")
                        adrecord.save()
    for db_ads in existing_ads:
        if db_ads.ad_id not in active_ad_list:
            db_ads.is_active = False
            db_ads.save()
        else: 
            db_ads.is_active = True
            db_ads.save()

@shared_task
def spend_limit_and_email(user_id):
    adlist, email = check_spend_limit_ad(user_id=user_id)
    check_spend_limit_adset(user_id=user_id)
    campaignlist = check_spend_limit_campaign(user_id=user_id)
    send_limit_exceed_mail(adlist=adlist, user_email=email, campaignlist=campaignlist)
    
    
@shared_task
def spend_wrapper(user_id):
    check_spend_limit_ad(user_id=user_id)
    check_spend_limit_adset(user_id=user_id)
