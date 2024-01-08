import requests 
from .models import AdRecord
from .utils import save_ads, email_to_file_name
from decouple import config 
from facebook.models import Creds
from django.contrib.auth.models import User 
from django.conf import settings 
import json 
import os 



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
                    active_ad_list.append(ad_id)
                    adrecord = AdRecord()
                    if not AdRecord.objects.filter(ad_id=ad_id).exists():
                        adrecord = AdRecord(
                            user = user,
                            ad_id=ad_id, ad_name=ad_name, 
                            adset_name=adset_name, adset_id=adset_id, 
                            campaign_id = campaign_id, campaign_name=campaign_name,
                            effective_object_story_id=eff, 
                            account_id = "act_296865963")
                        adrecord.save()
        print(f"file : {file}, len : {len(active_ad_list)}")
    for db_ads in AdRecord.objects.all():
        if db_ads.ad_id not in active_ad_list:
            db_ads.is_active = False
            # db_ads.save()
        else: 
            db_ads.is_active = True
            # db_ads.save()
    
            # print(db_ads.adset_name, db_ads.campaign_name, "is not active!")



def check_spend_limit(user_id="3"):
    """
    run every 20 minutes on selected ads 
    which have their limit set and if limit 
    set has exceeded then send the email to the 
    user associated 
    """
    user = User.objects.get(id=user_id)
    access_token = Creds.objects.get(user=user).LONGLIVED_ACCESS_TOKEN
    ads = AdRecord.objects.filter(user=user,is_active=True, expired=False).all()
    for ad in ads:
        url =  f'https://graph.facebook.com/v18.0/{ad.ad_id}/insights?fields=spend&access_token={access_token}'
        response = requests.get(url)
        content = response.json()
        spend = content['data'][0]['spend']
        print(spend, ad.ad_spend_limit)
        ad.ad_spend = spend
        ad.is_limit_set = True
        ad.save()
        if float(spend) > ad.ad_spend_limit and ad.is_limit_set == True and ad.ad_spend_limit  != 0.0:
            print("Send notification email ", ad.ad_id)


def send_limit_exceed_mail():
    """
    Send remider email to user if 
    ad spend limit has exceeded 
    """ 
    pass 

if __name__ == "__main__":
    capture_new_ads()