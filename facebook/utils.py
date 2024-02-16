from urllib.request import urlopen
import json 
import asyncio
import urllib.request 
from access_token import LONGLIVED_ACCESS_TOKEN, USER_LONGLIVED_ACCESS_TOKEN
import requests 
from django.conf import settings
# from asgiref.sync import sync_to_async
from .models import AccountsAd, AccountPages



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Section : access token logic
 
valid_permission_list = [
    'pages_manage_instant_articles', 'pages_show_list', 'ads_management', 
    'ads_read', 'business_management', 'leads_retrieval', 'pages_read_engagement', 
    'pages_manage_metadata', 'pages_read_user_content', 'pages_manage_ads', 
    'pages_manage_posts', 'pages_manage_engagement'
    ]

def get_permission_list(token):
    permission_list = []
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/permissions?access_token={token}"
    read_url = json.loads(urllib.request.urlopen(url).read()) 
    for r in read_url['data']:
        if r['status'] == 'granted':
            permission_list.append(r['permission'])
    return permission_list

def get_long_lived_access_token(api_key, api_secret, access_token):
    url = u"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/oauth/access_token?grant_type=fb_exchange_token" \
            u"&client_id={}&client_secret={}&fb_exchange_token={}".format(api_key, api_secret, access_token)
    read_url = json.loads(urllib.request.urlopen(url).read())
    return read_url['access_token']

def PageAndAccountToken(access_token):
    data = []
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts?fields=id,name,access_token&access_token={access_token}"
    read_url = json.loads(urllib.request.urlopen(url).read())
    # print(read_url, '\n')
    for res in read_url['data']:
        data.append({"name": res['name'], "id": res['id'], "access_token": res['access_token']})
    # print(data)
    return data

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_access_token_for_ad(eff, user=None):
    page_id = eff.split("_")[0]
    try:
        page  = AccountPages.objects.get(page_id=page_id)
        token = page.longlived_access_token
    except Exception as e:
        token = AccountsAd.objects.filter(user=user)[0].access_token
    return token

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ad accounts 


def fetch(url, print_url=False, print_response=False):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(url) if print_url else None
    print(data) if print_response else None
    return data

def get_ad_account(token):
    adaccount_dict = {}
    data = []
    adaccount_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/adaccounts?fields=id,name&access_token={token}"
    adaccounts = json.loads(urllib.request.urlopen(adaccount_url).read())
    if len(adaccounts['data']) != 0: # list of ad accounts not empty 
        status = 200
        for a in adaccounts['data']:
            data.append({"name":a['name'], "id": a['id']})  
    else:
        status = 404  # error for ad accounts 
    adaccount_dict['status'] = status 
    adaccount_dict['data'] = data
    # print(adaccount_dict)
    return adaccount_dict


def single_ad_info(ad_id,token):
    ad_url =  f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_id}?fields=id,name&access_token={token}"
    ad = fetch(ad_url)
    return (ad['id'], ad['name'])
    

def pages_associated_with_adaccounts(token, ad_account_id="act_296865963"):
    account_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_account_id}?fields=business&access_token={token}"
    business = fetch(url=account_url, print_response=False,print_url=False)
    if "business" in business:
        business_id = business['business']['id']
        pages_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{business_id}/owned_pages?access_token={token}"
        pages = fetch(url=pages_url, print_response=False)
        if len(pages['data']) != 0:
            return pages
        else:
            return None
    else:
        return None 


def get_all_campaigns(ad_id, token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_id}/campaigns?effective_status=%5B%22ACTIVE%22%2C%22PAUSED%22%5D&fields=name%2Cobjective&access_token={token}&limit=100&after"
    campaigns = fetch(url, print_response=False)
    return (campaigns['data'][0]['id'], campaigns['data'][0]['name'])



def get_adset_name(adset_id="6345796776582", access_token=LONGLIVED_ACCESS_TOKEN):
    adset_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{adset_id}?fields=id,name&access_token={access_token}"
    adsets = json.loads(urllib.request.urlopen(adset_url).read()) 
    adset_name = adsets['name']
    return adset_name


# fix on the account_id 
def get_campaign_name_and_id(account_id="act_296865963", access_token=LONGLIVED_ACCESS_TOKEN):
    campaign_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{account_id}/campaigns?fields=id,name,effective_status&access_token={access_token}&limit=100&after"
    campaigns_json = json.loads(urllib.request.urlopen(campaign_url).read())
    active_campaign = []
    inactive_campaign = []
    for cam in campaigns_json['data']:
        if cam['effective_status'] == "ACTIVE":
            active_campaign.append(cam)
        else:
            inactive_campaign.append(cam)
    all_campaign = active_campaign + inactive_campaign    # print(campaigns_json['data'])
    return all_campaign

def get_single_campaign(campaign_id=6338868866982, access_token=LONGLIVED_ACCESS_TOKEN):
    campaign_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign_id}?fields=name&access_token={access_token}"
    campaigns_json = json.loads(urllib.request.urlopen(campaign_url).read())
    return campaigns_json['name']

def get_adsets_from_campaign(campaign_id, access_token):
    campaign_ads= f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign_id}/adsets?fields=id,name,effective_status&access_token={access_token}"
    adsets = json.loads(urllib.request.urlopen(campaign_ads).read()) 
    for d in adsets['data']:
        ads_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{d['id']}/ads?fields=id,name&access_token={access_token}"
        ads = json.loads(urllib.request.urlopen(ads_url).read()) 
        d['ad_count'] = len(ads['data'])
    return adsets['data']


def get_ad_id_list(campaign_id ="6338868868582", access_token=LONGLIVED_ACCESS_TOKEN): # all ads from wholesale as there are comments
    campaign_ads= f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign_id}/ads?fields=id,name,creative.fields(effective_object_story_id),insights.fields(actions)&access_token={access_token}"
    ads_json = json.loads(urllib.request.urlopen(campaign_ads).read())  
    comment_id_list = []
    for d in ads_json['data']:
        comment_id_list.append(d['id'])
    return comment_id_list

def get_ad_name_and_effective_object_story_id(ad_id="6338868872182", access_token=LONGLIVED_ACCESS_TOKEN):
    ad_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{ad_id}?fields=id,name,creative.fields(effective_object_story_id),insights.fields(actions)&access_token={access_token}"
    ad_json = json.loads(urllib.request.urlopen(ad_url).read()) 
    ad_name = ad_json['name']
    effective_object_story_id = ad_json['creative']['effective_object_story_id']
    return ad_name, effective_object_story_id


# get total comment count in the ad
# if the comment count is less than 3 then don't build a graph
def comment_count(eff, access_token):
    comment_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{eff}/comments?fields=id,toplevel,message&access_token={access_token}"
    comment_json = json.loads(urllib.request.urlopen(comment_url).read())
    comment_len = len(comment_json['data'])
    return comment_len

def comment_info(comment_id, access_token=LONGLIVED_ACCESS_TOKEN):
    comment_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{comment_id}?fields=id,message&access_token={access_token}"
    comment_json = json.loads(urllib.request.urlopen(comment_url).read())
    return comment_json['message']

# hide and unhide comments
def hide_comment(comment_id, access_token=LONGLIVED_ACCESS_TOKEN):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{comment_id}"
    comment_hide = {
        "is_hidden": "true",
        "access_token":access_token
        }
    response = requests.post(url, json=comment_hide)
    # if response.status_code == 200:
    #     print('Comment hidden successfully.')
    # else:
    #     print('Error hiding comment:', response.json()['error']['message'])

def unhide_comment(comment_id, access_token=LONGLIVED_ACCESS_TOKEN):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{comment_id}"
    comment_hide = {
        "is_hidden": "false",
        "access_token":access_token
        }
    response = requests.post(url, json=comment_hide)
    # if response.status_code == 200:
    #     print('Comment revealed successfully.')
    # else:
    #     print('Error hiding comment:', response.json()['error']['message']) 

# check if the comments is hidden 
def comment_status(comment_id, access_token=LONGLIVED_ACCESS_TOKEN):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{comment_id}?fields=is_hidden,can_hide&access_token={access_token}"
    status = json.loads(urllib.request.urlopen(url).read()) 
    return status["is_hidden"]

#<<=======================================================================================================================>>
#FACEBOOK ACCOUNT SECTION LOGIC 

def get_all_accounts(user_access_token):
    url  = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts?fileds=id,name,access_token&access_token={user_access_token}&limit=100"
    response = json.loads(urllib.request.urlopen(url).read())
    return response['data']

def get_account_name(page_id, page_access_token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{page_id}?fields=id,name&access_token={page_access_token}"
    read_url = json.loads(urllib.request.urlopen(url).read())
    return read_url["name"]


def get_account_post_list(account_id, account_access_token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{account_id}/posts?fileds=id,message&access_token={account_access_token}&limit=100"
    read_url = json.loads(urllib.request.urlopen(url).read())
    post_id = []
    for a in read_url['data'][:20]:
        post_id.append(a['id'])

    return post_id


def get_post_photos(post_id,page_access_token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{post_id}?fields=id,full_picture&access_token={page_access_token}"
    read_url = json.loads(urllib.request.urlopen(url).read())
    full_picture = read_url['full_picture']
    return full_picture


def get_post_comment_count(post_id, account_access_token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{post_id}/comments?summary=true&access_token={account_access_token}&limit=100"
    read_url = json.loads(urllib.request.urlopen(url).read())
    comment_count = read_url['summary']['total_count']
    return comment_count



#<<===========================================================================================================================>>
# previous logic for facebook post comments 
def get_post_name_from_commentid(commentid, account_data):
    comment_id = split_id(commentid, 0)
    for d in account_data:
        d_id = split_id(d['id'], 1)
        if d_id == comment_id:
            post_name = d['message']
    if d_id:
        return post_name
    else:
        return "NO Post name available"
        
def split_id(string, index):
    id = string.split("_")[index]
    return id


def get_account_name(acc_id, access_token):
    account_url =  u"https://graph.facebook.com/{0}?access_token={1}".format(
                        acc_id,
                        access_token,)
    account_info = json.loads(urlopen(account_url).read())
    return account_info['name']