from celery import shared_task
import requests 
from .models import AdRecord
from .utils import save_ads, email_to_file_name
from .automation import check_spend_limit, send_limit_exceed_mail
from decouple import config 
from facebook.models import Creds
from django.contrib.auth.models import User 
from django.conf import settings 
import json 
import os 




@shared_task
def capture_new_ads(user_id="3"):
    """
    run every hour and capture new ads 
    with infomation like campaign and adset information.
    """
    user = User.objects.get(id=user_id)
    email = user.email 
    
    # email = "georgeyoumansjr@gmail.com"
    folder = os.path.join(settings.BASE_DIR, F"JSON/{email_to_file_name(email=email)}")
    user_files = os.listdir(folder)
    
    active_ad_list = []
    # user_files = []
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
                    # print(eff)
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
        print(f"file : {file}, len : {len(active_ad_list)}")
    for db_ads in AdRecord.objects.all():
        if db_ads.ad_id not in active_ad_list:
            db_ads.is_active = False
            db_ads.expired = True
            db_ads.save()
        else: 
            db_ads.is_active = True
            db_ads.expired = False
            db_ads.save()

@shared_task
def spend_limit_and_email(user_id):
    limit_list = check_spend_limit(user_id=user_id)
    send_limit_exceed_mail()
    for i in range(10):
        print("dummy print")
        
        
