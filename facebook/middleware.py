from django.shortcuts import redirect, render 
from .models import Creds, AccountPages, AccountsAd
import requests
import json 
from .token_expired import send_mail_token_expired, send_mail_token_limit_reached
from django.conf import settings 


#middleware for these prefix 
url_path_for_fb = [
    "/adsets/",
    "/set-ad-accounts/",
    '/sentiment-graph/',
    "/hide_comments/",
    "/unhide_comments/",
    "/my-accounts/",
    "/account-analysis/",
    
]


error_codes_limit_reached = [4, 17, 32, 613] # limit reached subtoken
error_code_expired = [190] # access token expired subtoken 

#condition for token to give 400 response 
# api response limit is exauhsted --done
# page token is invalid --done
# user token is invalid or expired (middleware only apply to this ) --done

#renew the page token if expired --done 
#redirect to token_expired page if User token is expired (critical) --done 
class TokenExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        request_path_prefix = str(request.path).split("/")
        if f"/{request_path_prefix[1]}/" in url_path_for_fb:
            if response.status_code >= 400:
                user_expired, user_limit, page_expired, page_limit = test_user_access_token(request)
                if user_expired:
                    send_mail_token_expired(request.user.email)
                    return redirect('token-expired') 
                if page_expired: 
                    send_mail_token_expired(request.user.email)
                    return redirect("token-expired-page")
                if user_limit or page_limit:
                    send_mail_token_limit_reached(request.user.email)
                    return redirect('token-limit-reached') 
        return response
    


# user access token test  
def test_user_access_token(request):
    access_token = Creds.objects.get(user=request.user).LONGLIVED_ACCESS_TOKEN
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/me/accounts?access_token={access_token}"
    user_token_expired = user_token_limit_reached = page_token_expired = page_token_limit_reached = False
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        error_data = response.json()
        error_message = error_data.get('error', 'Unknown Error')
        if error_message['code'] in error_codes_limit_reached:
            user_token_limit_reached = True
        if error_message['code'] in error_code_expired:
            user_token_expired = True
    if user_token_expired or user_token_limit_reached:
        return  (user_token_expired, user_token_limit_reached,  page_token_expired, page_token_limit_reached )
    else: 
        adaccounts = AccountsAd.objects.filter(user=request.user).all()
        for ad in adaccounts:
            ad_token = ad.page_associated.longlived_access_token
            ad_account_id = ad.ad_account_id
            page_token_expired, page_token_limit_reached = test_page_token(account_id=ad_account_id, token=ad_token)
            if page_token_expired or page_token_limit_reached:
                return ( user_token_expired, user_token_limit_reached, page_token_expired, page_token_limit_reached )
        return ( user_token_expired, user_token_limit_reached,  page_token_expired, page_token_limit_reached )


# need improvement on codes 
def test_page_token(account_id, token):
    url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{account_id}/campaigns?fields=id,name&access_token={token}"
    limit_reached = expired = False
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        campaign_id = data['data'][0]['id']
    except requests.exceptions.RequestException as e:
        campaign_id = None
        error_data = response.json()
        error_message = error_data.get("error", "Unknown error")
    if campaign_id == None:
        error_code  = error_message['code']
        if error_code in error_code_expired:
            expired = True
        if error_code in error_codes_limit_reached:
            limit_reached = True
        return (expired, limit_reached)
    else: 
        try:
            cm_url = f"https://graph.facebook.com/{settings.FACEBOOK_API_VERSION}/{campaign_id}/ads?fields=id,name&access_token={token}"
            cm_response = requests.get(cm_url)
            cm_response.raise_for_status()
            code = "200"
        except Exception as e: 
            cm_error = cm_response.json()
            cm_error_message = cm_error.get('error', 'Unknown Error')
            code = cm_error_message['code']
            
        if  code in error_codes_limit_reached:
            limit_reached = True
        if  code in error_code_expired:
            expired = True
    return (expired, limit_reached)
        




