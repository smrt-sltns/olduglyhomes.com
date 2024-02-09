from django.contrib.auth.models import User 
from django.conf import settings
from .models import AccountPages
import urllib.request
import json 



def save_pages_to_adaccount(request, ad_account_id): #check which page token is valid for the ad accounts 
    page_id = 0
    account_pages = AccountPages.objects.filter(user=request.user).all()
    pages = [{'id': p.page_id, "access_token": p.longlived_access_token} for p in account_pages]
    for p in pages: 
        try:
            # test 1: check if list of ad campaings and adsets can be obtained
            campaign_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_account_id}/campaigns?effective_status=%5B%22ACTIVE%22%2C%22PAUSED%22%5D&fields=name%2Cobjective&access_token={p['access_token']}"
            campaigns_json = json.loads(urllib.request.urlopen(campaign_url).read())
            if "data" in campaigns_json and len(campaigns_json) != 0:
                campaign_id = campaigns_json['data'][0]['id'] # first ad campaign id 
                ads_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign_id}/ads?fields=id,name,insights&access_token={p['access_token']}"
                ads_json = json.loads(urllib.request.urlopen(ads_url).read())  
                if "data" in ads_json and len(ads_json['data']) != 0: 
                    ad_id = ads_json['data'][0]['id']

                    # test 2: get effective object story id of an AD 
                    eff = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_id}?fields=creative.fields(effective_object_story_id),insights.fields(actions)&access_token={p['access_token']}" 
                    eff_json = json.loads(urllib.request.urlopen(eff).read())
                    eff_id = eff_json["creative"]["effective_object_story_id"]

                    # test 3 : get comments from the eff_id 
                    comments_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{eff_id}/comments?summary=true&access_token={p['access_token']}"
                    comments_json = json.loads(urllib.request.urlopen(comments_url).read())
                    if "data" in comments_json:
                        page_id = p['id']
                        break
                else:
                    raise ValueError("No ADs found!")
            else:
                raise ValueError("No campaigns found!")
        except Exception as e: 
            print(e)
            continue

    return page_id
    